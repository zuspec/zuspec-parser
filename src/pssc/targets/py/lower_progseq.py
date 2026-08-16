"""One operation body, rendered as Python.

The walk, the comment attachment and the call dispatch are
`targets/body_walker.py`'s -- the same ones the C emitter uses. What is here is
the Python rendering, and it is deliberately the whole of what this backend
knows about the language: thirteen statement hooks, ten expression hooks, and
one hook per `Disposition`.

Python differs from C in four places that are not cosmetic, and each is
commented where it happens:

* **A suite cannot be empty.** `yield` lowers to a comment on both targets, but
  a C block of only comments compiles and a Python one does not, so every
  block goes through :meth:`_BodyEmitter.block`, which supplies `pass`.
* **There is no do-while.** `repeat {} while (c)` becomes `while True:` with a
  trailing `if not (c): break`, which is the same loop and states so.
* **There is no `switch`.** `match` becomes an if/elif chain over a subject
  bound to a temporary, because a PSS subject may be a register read and
  evaluating it once per arm would issue one bus transaction per arm.
* **There are no out-parameters.** `ok = ch.try_get(tok)` writes through a
  pointer in C, and an int is immutable here. The local is declared as a
  one-element cell and read as `tok[0]` -- and WHICH locals those are is the
  shared `scan_output_locals`, the same analysis that widens them to
  `uint64_t` in C.
"""
from __future__ import annotations

from typing import List, Optional, Set

from ..body_walker import BodyWalker, CallDispatch, scan_output_locals
from ..call_legality import Ctx
from ..comments import HASH
from ..progseq_model import (_dt_name, array_base_stride, channel_fields,
                             field_is_reg_group, scalar_offset, sub_components)
from .lower_reg_model import accessor_map, value_class_name
from .naming import class_name, mangle, reg_symbol

_DT_STRUCT = "DataTypeStruct"
_DT_INT = "DataTypeInt"
_DT_BOOL = "DataTypeBool"
_DT_ENUM = "DataTypeEnum"
_DT_CHANDLE = "DataTypeChandle"
_DT_ARRAY = "DataTypeArray"

#: PSS binary operators, in Python. `&&`/`||` become `and`/`or`, which are the
#: same operator with a different spelling; every other entry is shared with C.
_BINOP = {
    "Add": "+", "Sub": "-", "Minus": "-", "Mult": "*", "Mul": "*",
    "Div": "//", "Mod": "%", "Eq": "==", "NotEq": "!=", "Ne": "!=",
    "Lt": "<", "LtE": "<=", "Le": "<=", "Gt": ">", "GtE": ">=", "Ge": ">=",
    "And": "and", "Or": "or", "BitAnd": "&", "BitOr": "|", "BitXor": "^",
    "LShift": "<<", "Shl": "<<", "RShift": ">>", "Shr": ">>",
}
#
# `Div` is the one entry that is a TRANSLATION rather than a spelling. PSS `/`
# is integer division on integral operands and Python's `/` is not, so `nbytes
# / 4` rendered with `/` produces a float and programs a float into a size
# register. `//` is the operator that means what the model means.

_UNOP = {
    "Not": "not ", "LogNot": "not ",
    "Invert": "~", "BitNot": "~", "Neg": "-", "USub": "-", "Minus": "-",
    "UAdd": "+", "Plus": "+",
}

_MEM_PRIMS = {
    "read8": ("read", 8), "read16": ("read", 16),
    "read32": ("read", 32), "read64": ("read", 64),
    "write8": ("write", 8), "write16": ("write", 16),
    "write32": ("write", 32), "write64": ("write", 64),
}

#: PSS built-ins this target claims a rendering for -- its half of the contract
#: in `targets/call_legality.py`. A name claimed there with no rendering here is
#: a call that would reach the output verbatim, which is the whole defect the
#: registry exists to prevent.
PY_BUILTINS = frozenset({
    "message", "print",
    "make_handle_from_handle", "addr_value",
}) | frozenset(_MEM_PRIMS)

#: Register methods this target renders, and the argument count each takes.
_REG_ACCESSORS = {
    "read": 0, "write": 1, "read_val": 0, "write_val": 1,
    "write_val_masked": 2,
}


def _array_size(dtype) -> Optional[int]:
    """Folded element count of an array type, or ``None``.

    ``None`` matters: the IR carries ``size: -1`` for a bound that is a package
    constant, and treating that as a number emits `range(-1)`, a loop that
    silently does nothing.
    """
    if dtype is None or _dt_name(dtype) != _DT_ARRAY:
        return None
    try:
        n = int(getattr(dtype, "size", None))
    except (TypeError, ValueError):
        return None
    return n if n >= 0 else None


def py_string_literal(s: str) -> str:
    """A PSS string constant as a Python literal. `repr` IS Python's spelling."""
    return repr(s)


class _BodyEmitter(CallDispatch, BodyWalker):
    """Translate one operation body to Python lines.

    A node kind is handled by a hook named after it (`StmtForeach` ->
    `stmt_foreach`), and a CALL by its `Disposition` from the same registry the
    legality gate consults. Neither of those is this backend's -- which is the
    claim P8.T1 exists to test.
    """

    indent = "    "
    comment_style = HASH

    legality_target = "op-model-py"
    call_context = Ctx.TARGET

    def __init__(self, fn, comp, model, *, imports=None, ctor_names=None):
        self.fn = fn
        self.comp = comp
        self.model = model
        self.ctor_names = ctor_names
        self.imports = dict(imports or {})
        self.accs = accessor_map(comp)
        self.arg_rename = {a.arg: mangle(a.arg) for a in fn.args.args}
        self.arg_names = set(self.arg_rename)
        self.comp_fields = {f.name for f in getattr(comp, "fields", [])}
        self.reg_fields = {f.name for f in comp.fields if field_is_reg_group(f)}
        self.reg_groups = {f.name: f.datatype for f in comp.fields
                           if field_is_reg_group(f)}
        self.chan_fields = {f.name for f in channel_fields(comp)}
        self.subs = {s.name: s for s in sub_components(comp)}
        self.model_ops = {f.name for f in comp.functions}
        #: Locals a channel `try_get` writes through. They are emitted as
        #: ONE-ELEMENT LISTS and read as `name[0]`, because a PSS output
        #: argument has no other form here: an int is immutable and a name
        #: rebound inside a call is not rebound outside it. The C backend uses
        #: the same scan for the same reason and reaches a different answer --
        #: it widens the declaration to `uint64_t` because `try_get` writes
        #: through a pointer. Both are "the declaration has to change"; only
        #: the change differs, which is what makes the SCAN language-neutral
        #: and the response not.
        self.chan_out_locals: Set[str] = scan_output_locals(
            fn.body, lambda n: self._is_chan_method(n, "try_get"),
            what="channel try_get()")
        #: `match` subjects are bound to a temporary; the counter keeps nested
        #: matches from shadowing each other.
        self._match_depth = 0

    # -- blocks --------------------------------------------------------------

    def block(self, body, ind: int) -> List[str]:
        """A Python suite: *body*, or `pass` when it renders to no statements.

        Not the same question as "is the body empty". A body of one `yield`
        lowers to one COMMENT on this target, and a suite of only comments is a
        syntax error where the equivalent C block merely has nothing in it.
        """
        lines = self.stmts(body, ind)
        if not any(l.strip() and not l.strip().startswith("#") for l in lines):
            lines.append(self.pad(ind) + "pass")
        return lines

    def emit(self, body, ind: int = 1) -> List[str]:
        return self.block(body, ind)

    # -- expressions ---------------------------------------------------------

    def _operand(self, e) -> str:
        """An operand of a compound expression, bracketed if it is one too.

        The IR tree says how the expression groups and Python precedence only
        happens to agree. Printing the tree's own structure settles it, and
        costs a pair of brackets.
        """
        s = self.expr(e)
        return f"({s})" if _dt_name(e) in ("ExprBin", "ExprUnary") else s

    def expr_constant(self, e) -> str:
        v = e.value
        if isinstance(v, bool):
            return "True" if v else "False"
        if isinstance(v, int):
            return str(v)
        if isinstance(v, str):
            return py_string_literal(v)
        raise ValueError(f"unsupported constant of type {type(v).__name__}")

    def expr_ref_local(self, e) -> str:
        name = self.arg_rename.get(e.name, mangle(e.name))
        # A channel-output local is a cell; every use of it is a use of its
        # contents. The one place that wants the cell itself is the `try_get`
        # call, which asks for it directly (`_chan_call`).
        return f"{name}[0]" if e.name in self.chan_out_locals else name

    def type_expr_ref_self(self, e) -> str:
        return "self"

    def expr_attribute(self, e) -> str:
        base = e.value
        if _dt_name(base) == "TypeExprRefSelf":
            # A component DATA MEMBER is an attribute of the instance; an
            # argument shadows nothing and stays a local. Anything else is a
            # package-scope constant, which reaches Python as a bare name -- and
            # if nothing defines it, as a NameError at the first call rather
            # than as C's silent resolution against whatever else is in scope.
            if e.attr in self.comp_fields:
                return f"self.{mangle(e.attr)}"
            if e.attr in self.arg_names:
                return self.arg_rename[e.attr]
            return mangle(e.attr)
        return f"{self.expr(base)}.{e.attr}"

    def expr_subscript(self, e) -> str:
        return f"{self.expr(e.value)}[{self.expr(e.slice)}]"

    def expr_bin(self, e) -> str:
        op = _BINOP.get(e.op.name)
        if op is None:
            raise ValueError(f"unsupported binop {e.op.name}")
        return f"{self._operand(e.lhs)} {op} {self._operand(e.rhs)}"

    def expr_unary(self, e) -> str:
        op = _UNOP.get(e.op.name)
        if op is None:
            raise ValueError(f"unsupported unary op {e.op.name}")
        return f"{op}({self.expr(e.operand)})"

    def expr_cast(self, e) -> str:
        """`(bit[32])x` -> `x & 0xffffffff`.

        A cast is NOT dropped here, and this is the one place where Python needs
        MORE than C rather than less. A C `uint32_t` truncates on assignment;
        a Python int does not, so a model that casts a computed value to the
        register's width and relies on it would otherwise hand the bus a number
        the device cannot hold. Signed and non-integral casts are the identity,
        as they are in C.
        """
        dt = e.target_type
        inner = self.expr(e.value)
        if _dt_name(dt) == _DT_INT and not getattr(dt, "signed", False):
            bits = int(getattr(dt, "bits", 32) or 32)
            return f"(({inner}) & 0x{(1 << bits) - 1:x})"
        return inner

    def expr_ref_bottom_up(self, e) -> str:
        raise ValueError(
            f"component '{getattr(self.comp, 'name', '?')}' refers UPWARD to "
            f"its parent ({_dt_name(e)}). This lowering constructs each "
            f"sub-component with its own bus and base and emits no parent "
            f"back-pointer, so there is nothing for this to resolve to. Move "
            f"the shared state down, or pass it as an argument.")

    # -- calls, one hook per Disposition -------------------------------------

    def call_names(self):
        from ..validate_calls import model_names

        _, ops, ctors = model_names(self.comp, self.ctor_names)
        return dict(model_ops=ops, imports=frozenset(self.imports),
                    subcomps=ctors)

    def call_reg(self, call) -> Optional[str]:
        return self._reg_call(call)

    def call_channel(self, call) -> Optional[str]:
        return self._chan_call(call)

    def call_mem(self, call) -> Optional[str]:
        return self._builtin_call(call)

    #: Address arithmetic and the console are both rendered by the same method,
    #: which dispatches on the built-in's own name.
    call_addr = call_mem
    call_utility = call_mem

    def call_model_op(self, call) -> Optional[str]:
        return self._model_call(call)

    call_import = call_model_op

    # -- registers -----------------------------------------------------------

    def _chain(self, e):
        """Flatten `self.<group>...<reg>[i]` to `[[name, index|None], ...]`.

        ``None`` for anything not rooted at `self`, which is how a call on
        something else falls through to the generic paths.
        """
        cn = _dt_name(e)
        if cn == "TypeExprRefSelf":
            return []
        if cn == "ExprAttribute":
            b = self._chain(e.value)
            if b is None:
                return None
            b.append([e.attr, None])
            return b
        if cn == "ExprSubscript":
            b = self._chain(e.value)
            if not b:
                return None
            b[-1][1] = e.slice
            return b
        return None

    def _reg_call(self, call) -> Optional[str]:
        """A register access -> the generated accessor method.

        The method NAME is asked of `naming.reg_symbol`, the same function that
        named the definition, so a rename cannot leave the two disagreeing. An
        unrecognised method on a register raises rather than falling through:
        `regs.csr.write_val(x)` reaching the generic path would emit
        `self.regs.csr.write_val(x)`, an attribute chain that exists nowhere and
        that says nothing useful when it fails.
        """
        func = call.func
        if _dt_name(func) != "ExprAttribute":
            return None
        chain = self._chain(func.value)
        # A register lives inside a group, so its path is at least
        # `<group>.<reg>`. A one-element chain is a call on the GROUP.
        if not chain or len(chain) < 2 or chain[0][0] not in self.reg_fields:
            return None

        reg = chain[-1][0]
        segs = [c[0] for c in chain[:-1]]
        idx = [self.expr(c[1]) for c in chain if c[1] is not None]
        args = [self.expr(a) for a in call.args]

        method = func.attr
        if method not in _REG_ACCESSORS:
            raise ValueError(
                f"unsupported register method '{method}' on "
                f"'{'.'.join(segs + [reg])}'. This target emits one accessor "
                f"per register method; known: "
                f"{', '.join(sorted(_REG_ACCESSORS))}.")
        want = _REG_ACCESSORS[method]
        if len(args) != want:
            raise ValueError(
                f"register method '{method}' takes {want} argument(s), got "
                f"{len(args)}")
        acc = self.accs.get(tuple(segs) + (reg,))
        if acc is None:
            raise ValueError(
                f"'{'.'.join(segs + [reg])}' is accessed as a register, but "
                f"'{getattr(self.comp, 'name', '?')}' emits no accessor for it. "
                f"Reachable: {', '.join('.'.join(p) for p in sorted(self.accs))}")
        name = reg_symbol(acc.segs, acc.name, method)
        return f"self.{name}(" + ", ".join(idx + args) + ")"

    # -- channels ------------------------------------------------------------

    def _chan_name(self, call) -> Optional[str]:
        func = getattr(call, "func", None)
        if _dt_name(func) != "ExprAttribute":
            return None
        chain = self._chain(func.value)
        if not chain or len(chain) != 1 or chain[0][0] not in self.chan_fields:
            return None
        return chain[0][0]

    def _is_chan_method(self, call, method: str) -> bool:
        return (_dt_name(getattr(call, "func", None)) == "ExprAttribute"
                and call.func.attr == method
                and self._chan_name(call) is not None)

    def _chan_call(self, call) -> Optional[str]:
        """`wake.try_put(1)` -> `self.wake.try_put(1)`, on the shipped `Chan1`.

`try_get` is handed the output local's CELL: see
        `Chan1.try_get` for why a PSS output argument reaches Python that way.

        Blocking `get()`/`put()` are refused by the registry before they get
        here; `Chan1` also raises, for the model that reached it another way.
        """
        name = self._chan_name(call)
        if name is None:
            return None
        m = call.func.attr
        ref = f"self.{mangle(name)}"
        if m == "try_put":
            if len(call.args) != 1:
                raise ValueError("channel try_put() takes one argument")
            return f"{ref}.try_put({self.expr(call.args[0])})"
        if m == "try_get":
            if len(call.args) != 1:
                raise ValueError("channel try_get() takes one output argument")
            # The CELL, not its contents: this call is what fills it.
            out = call.args[0]
            cell = self.arg_rename.get(out.name, mangle(out.name))
            return f"{ref}.try_get({cell})"
        raise ValueError(
            f"unsupported channel method '{m}' on '{name}'. The Python channel "
            f"runtime implements try_put/try_get (share/py/pssc_rt.py).")

    # -- built-ins and model calls -------------------------------------------

    def _builtin_name(self, func) -> Optional[str]:
        cn = _dt_name(func)
        if cn == "ExprRefUnresolved":
            return getattr(func, "name", None)
        if cn == "ExprAttribute":
            return func.attr
        return None

    def _builtin_call(self, call) -> Optional[str]:
        """PSS built-ins, which have no definition to call.

        The address built-ins are not calls at all here: `addr_handle_t` is
        opaque in PSS and a plain integer address in the generated code, so
        deriving a handle from another is an add and reading its value is the
        identity.
        """
        name = self._builtin_name(call.func)
        if name is None or name not in PY_BUILTINS:
            return None
        args = call.args
        if name == "make_handle_from_handle":
            return f"({self.expr(args[0])} + {self.expr(args[1])})"
        if name == "addr_value":
            return self.expr(args[0])
        if name in _MEM_PRIMS:
            return self._mem_call(name, args)
        if name in ("message", "print"):
            return self._message_call(name, args)
        raise ValueError(
            f"built-in '{name}' is claimed by the Python target but has no "
            f"rendering; see targets/py/lower_progseq.py")

    def _mem_call(self, name: str, args) -> str:
        """`read32(h)` / `write32(h, v)` -> the bus protocol.

        NOT register accesses -- a model uses these to put a descriptor into
        system RAM -- but they cross the same seam and are rendered against the
        same object, so a bus implementation serves both.
        """
        direction, width = _MEM_PRIMS[name]
        want = 1 if direction == "read" else 2
        if len(args) != want:
            raise ValueError(f"'{name}' takes {want} argument(s), got {len(args)}")
        rendered = [self.expr(a) for a in args]
        return f"self._bus.{name}(" + ", ".join(rendered) + ")"

    def _message_call(self, name: str, args) -> str:
        """`message(verbosity, text)` -> `self._bus.message(text)`.

        Routed through the bus rather than to `print` so that a harness driving
        several models can collect their output; `Bus.message` defaults to
        printing, which is what a bare script wants. The verbosity has no
        analogue and is dropped, exactly as the SV and C projections drop it.
        """
        rest = args[1:] if (name == "message" and len(args) >= 2) else args
        rendered = ", ".join(self.expr(a) for a in rest)
        return f"self._bus.message({rendered})"

    def _model_call(self, call) -> str:
        """Another operation of this component, or a declared import."""
        func = call.func
        args = [self.expr(a) for a in call.args]
        name = None
        if _dt_name(func) == "ExprRefUnresolved":
            name = func.name
        elif (_dt_name(func) == "ExprAttribute"
                and _dt_name(func.value) == "TypeExprRefSelf"):
            name = func.attr
        if name is not None and name in self.model_ops:
            return f"self.{mangle(name)}(" + ", ".join(args) + ")"
        if name is not None and name in self.imports:
            # An `import target/solve function` is a PLATFORM function, not a
            # method of this component: it is called on the bus object, which is
            # the one thing the environment supplies. `lower_imports` documents
            # the required signature from the same declaration, so the two
            # cannot disagree about it.
            return f"self._bus.{mangle(name)}(" + ", ".join(args) + ")"
        raise ValueError(
            f"call to '{name or _dt_name(func)}' has no lowering in the Python "
            f"target. It is not a register access, not a PSS built-in this "
            f"target claims ({', '.join(sorted(PY_BUILTINS))}), not an "
            f"operation of '{getattr(self.comp, 'name', '?')}', and not a "
            f"declared `import target/solve function`.")

    # -- statements ----------------------------------------------------------

    def stmt_ann_assign(self, s, ind: int) -> List[str]:
        """A declaration. Python has none, so this is an initialisation.

        The value matters even where the PSS gives none: `dma_ch_csr_s csr;`
        followed by three field assignments and a write means "all other fields
        zero", and a name that did not exist yet would be an UnboundLocalError
        at the first field assignment.
        """
        pad = self.pad(ind)
        name = self.expr(s.target)
        value = getattr(s, "value", None)
        init = (self.expr(value) if value is not None
                else self._zero(s.annotation))
        if getattr(s.target, "name", None) in self.chan_out_locals:
            # A CELL, deliberately, and stated in the output because `bit tok`
            # becoming `[0]` is otherwise an unexplained discrepancy with the
            # PSS source. See `Chan1.try_get`.
            cell = name[:-3] if name.endswith("[0]") else name
            return [f"{pad}{cell} = [{init}]"
                    f"   # PSS local, held in a cell: channel try_get output"]
        return [f"{pad}{name} = {init}"]

    def _zero(self, dtype) -> str:
        """The default value of a declared local."""
        cn = _dt_name(dtype)
        if cn == _DT_STRUCT:
            nm = (dtype.name or "").split("::")[-1]
            # `addr_handle_t` is an opaque handle in PSS and an integer address
            # here, the same mapping `chandle` gets.
            if nm == "addr_handle_t":
                return "0"
            return f"{value_class_name(dtype)}()"
        if cn in (_DT_INT, _DT_BOOL, _DT_ENUM, _DT_CHANDLE):
            return "0"
        raise ValueError(f"no default value for a local of type {cn}")

    def stmt_assign(self, s, ind: int) -> List[str]:
        pad = self.pad(ind)
        tgt = s.targets[0]
        return [f"{pad}{self.expr(tgt)} = {self.expr(s.value)}"]

    def stmt_aug_assign(self, s, ind: int) -> List[str]:
        op = _BINOP.get(s.op.name)
        if op is None:
            raise ValueError(f"unsupported augmented-assign op {s.op.name}")
        if op in ("and", "or"):
            raise ValueError(
                f"'{s.op.name}' has no augmented-assignment form in Python")
        return [f"{self.pad(ind)}{self.expr(s.target)} {op}= "
                f"{self.expr(s.value)}"]

    def stmt_expr(self, s, ind: int) -> List[str]:
        return [f"{self.pad(ind)}{self.expr(s.expr)}"]

    def stmt_return(self, s, ind: int) -> List[str]:
        pad = self.pad(ind)
        if s.value is not None:
            return [f"{pad}return {self.expr(s.value)}"]
        return [f"{pad}return"]

    def stmt_if(self, s, ind: int) -> List[str]:
        pad = self.pad(ind)
        lines = [f"{pad}if {self.expr(s.test)}:"]
        lines += self.block(s.body, ind + 1)
        if getattr(s, "orelse", None):
            lines.append(f"{pad}else:")
            lines += self.block(s.orelse, ind + 1)
        return lines

    def stmt_while(self, s, ind: int) -> List[str]:
        pad = self.pad(ind)
        return [f"{pad}while {self.expr(s.test)}:"] + self.block(s.body, ind + 1)

    def stmt_repeat_while(self, s, ind: int) -> List[str]:
        """`repeat { ... } while (c)` -- a do-while, which Python does not have.

        `while True:` with the test at the BOTTOM, which is the same loop: the
        body runs at least once, and that is the whole reason a model writes a
        completion poll this way rather than as a `while`.
        """
        pad = self.pad(ind)
        inner = self.pad(ind + 1)
        lines = [f"{pad}while True:"]
        lines += self.block(s.body, ind + 1)
        lines.append(f"{inner}if not ({self.expr(s.condition)}):")
        lines.append(f"{inner}{self.indent}break")
        return lines

    def stmt_break(self, s, ind: int) -> List[str]:
        return [f"{self.pad(ind)}break"]

    def stmt_continue(self, s, ind: int) -> List[str]:
        return [f"{self.pad(ind)}continue"]

    def stmt_foreach(self, s, ind: int) -> List[str]:
        """`foreach (a[i]) { ... }` -> `for i in range(N):`.

        The bound is folded at generation time rather than taken as `len(...)`.
        A sub-component array IS a Python list here and `len()` would work, but
        the collection may also be a register array, which has no object to
        measure -- so the model's own stated size is the one answer that covers
        both.
        """
        pad = self.pad(ind)
        idx = mangle(getattr(getattr(s, "target", None), "name", None) or "i")
        n = _array_size(self._iter_dtype(s))
        if n is None:
            raise ValueError(
                f"cannot lower `foreach` over '{self.expr(s.iter)}': its size "
                f"is not known at generation time.")
        return [f"{pad}for {idx} in range({n}):"] + self.block(s.body, ind + 1)

    def _iter_dtype(self, s):
        it = s.iter
        if (_dt_name(it) == "ExprAttribute"
                and _dt_name(it.value) == "TypeExprRefSelf"):
            for f in getattr(self.comp, "fields", []):
                if f.name == it.attr:
                    return f.datatype
        return None

    def stmt_match(self, s, ind: int) -> List[str]:
        """PSS `match` -> an if/elif chain over a bound subject.

        `match`/`case` exists in Python 3.10+ and is deliberately not used: it
        would put a floor under the interpreter a generated model runs on, and
        a generated driver is exactly the kind of code that ends up on whatever
        Python the lab machine has.

        The subject is bound to a temporary FIRST. A PSS subject may be a
        register read, and re-evaluating it per arm would issue one bus
        transaction per arm -- on a status register whose read clears bits, that
        is not merely wasteful.

        PSS makes an unmatched subject an error (§22.7.9). Where the model
        states no default this emits one that says so, rather than falling
        through in silence.
        """
        pad = self.pad(ind)
        var = f"_subject{self._match_depth or ''}"
        self._match_depth += 1
        try:
            lines = [f"{pad}{var} = {self.expr(s.subject)}"]
            keyword = "if"
            default = None
            for case in s.cases:
                labels = self._pattern_labels(case.pattern)
                if not labels:
                    default = case
                    continue
                test = " or ".join(f"{var} == {lb}" for lb in labels)
                lines.append(f"{pad}{keyword} {test}:")
                lines += self.block(case.body, ind + 1)
                keyword = "elif"
            lines.append(f"{pad}else:")
            if default is not None:
                lines += self.block(default.body, ind + 1)
            else:
                lines.append(
                    f"{pad}{self.indent}raise ValueError("
                    f"{py_string_literal(f'{self.fn.name}: unmatched match subject')}"
                    f' + " (%r)" % (' + var + ",))")
        finally:
            self._match_depth -= 1
        return lines

    def _pattern_labels(self, pattern) -> List[str]:
        if pattern is None:
            return []
        cn = _dt_name(pattern)
        if cn == "PatternValue":
            return [self.expr(pattern.value)]
        if cn in ("PatternOr", "PatternSequence"):
            out: List[str] = []
            for p in pattern.patterns:
                out += self._pattern_labels(p)
            return out
        raise ValueError(f"unsupported match pattern {cn}")

    def stmt_yield(self, s, ind: int) -> List[str]:
        """`yield` -- the polling wait primitive.

        LOWERED, NOT REJECTED, and the rendering is a comment. `yield` is a hint
        to a scheduler and this target has none, so the honest cost of "let
        something else run" is zero and the surrounding loop becomes a poll --
        which is what a model reaching `yield` asked for. `block()` supplies the
        `pass` when this is a body's only statement.
        """
        return [f"{self.pad(ind)}# yield: nothing to yield to on this target"]


class _CtorMixin:
    """The three forms that only ever appear in a constructor.

    Not a separate emitter: a constructor assigns attributes, loops and calls
    built-ins exactly as an operation does, so all of that is inherited. What is
    added is the part with no runtime representation -- binding a register group
    and folding a group offset both become constants here, which is why a
    generated model carries no register objects at all.
    """

    #: A constructor body is a SOLVE context. The registry refuses a target-only
    #: call there, which is how `write32(...)` in a constructor becomes a
    #: diagnostic rather than code that runs before the bus exists.
    call_context = Ctx.SOLVE

    def call_structural(self, call) -> Optional[str]:
        return self._group_call(call)

    #: A group offset is folded at generation time, by the same method: both are
    #: calls on a register GROUP, which has no object in the generated Python.
    call_fold = call_structural

    def call_subcomp_ctor(self, call) -> Optional[str]:
        return self._sub_ctor_call(call)

    def _group_call(self, call) -> Optional[str]:
        func = call.func
        if _dt_name(func) != "ExprAttribute":
            return None
        chain = self._chain(func.value)
        if not chain or len(chain) != 1 or chain[0][0] not in self.reg_groups:
            return None
        group = self.reg_groups[chain[0][0]]
        m = func.attr
        args = call.args
        if m == "set_handle":
            # The group has no object: binding it IS setting the component's
            # base, and every accessor folds its offset from there. An
            # ASSIGNMENT, like `_sub_ctor_call`'s -- `set_handle` returns void,
            # so it can only ever appear as a statement.
            return f"self._base = {self.expr(args[0])}"
        if m == "get_offset_of_instance":
            return f"0x{scalar_offset(group, _str_const(args[0], m)):x}"
        if m == "get_offset_of_instance_array":
            base, stride = array_base_stride(group, _str_const(args[0], m))
            return f"(0x{base:x} + 0x{stride:x} * {self._operand(args[1])})"
        raise ValueError(
            f"unsupported register-group method '{m}'. This target folds group "
            f"offsets at generation time; a method it does not know would "
            f"become a call on a group object that does not exist.")

    def _sub_ctor_call(self, call) -> Optional[str]:
        """`ch[i].initialize(...)` -> constructing the sub-component object.

        A sub-component is a real object here, unlike in C where it is embedded
        storage that `_init` writes into. So the constructor CALL is the
        construction, and the list element is assigned rather than addressed.
        """
        func = call.func
        if _dt_name(func) != "ExprAttribute":
            return None
        chain = self._chain(func.value)
        if not chain or len(chain) != 1 or chain[0][0] not in self.subs:
            return None
        sub = self.subs[chain[0][0]]
        if func.attr not in (self.ctor_names or ()):
            raise ValueError(
                f"'{sub.name}.{func.attr}()' is called during construction, but "
                f"only a sub-component's constructor may be. An operation is a "
                f"target function and cannot run in a solve exec.")
        args = ["self._bus"] + [self.expr(a) for a in call.args]
        ctor = f"{class_name(getattr(sub.dtype, 'name', ''))}(" + \
               ", ".join(args) + ")"
        idx = chain[0][1]
        target = (f"self.{mangle(sub.name)}[{self.expr(idx)}]"
                  if idx is not None else f"self.{mangle(sub.name)}")
        # An ASSIGNMENT, not a call, which is why this reaches the output only
        # through `stmt_expr`: PSS states sub-component construction as a call
        # statement, and it is never an operand of anything.
        return f"{target} = {ctor}"


class _CtorEmitter(_CtorMixin, _BodyEmitter):
    """The constructor emitter: the ctor-only forms over the default body."""


def _str_const(e, method: str) -> str:
    """The string-literal argument of an offset query."""
    if (_dt_name(e) != "ExprConstant"
            or not isinstance(getattr(e, "value", None), str)):
        raise ValueError(
            f"'{method}' needs a literal instance name so its offset can be "
            f"folded at generation time; got {_dt_name(e)}.")
    return e.value
