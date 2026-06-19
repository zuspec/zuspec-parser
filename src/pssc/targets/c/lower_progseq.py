"""Lower a regular PSS component to the C programming API: the component handle
(+ pssc_bus shim), export-function declarations, the factory/lifecycle, and the
operation bodies.

Bodies translate the PSS procedural subset 1:1. Unlike the SV backend, C keeps
native value-returning register reads, native ``return`` values, and native
``do...while`` (PSS ``repeat{}while``) -- so the three SV-only rewrites do not
fire here; the body is closer to the PSS source.

Design: design/pss-c-cpp-progseq-gen-design.md (§3.5, §3.6, §3.7).
"""
from __future__ import annotations

from typing import Dict, List, Optional, Set

from ..progseq_model import func_kind, FuncKind, field_is_reg_group, _dt_name
from .lower_reg_model import accessor_base, c_struct_name, _prim_bits

_DT_STRUCT = "DataTypeStruct"
_DT_INT = "DataTypeInt"

# C reserved words that could collide with PSS identifiers (small, extend as needed).
_C_KEYWORDS = frozenset({
    "auto", "break", "case", "char", "const", "continue", "default", "do",
    "double", "else", "enum", "extern", "float", "for", "goto", "if", "inline",
    "int", "long", "register", "restrict", "return", "short", "signed", "sizeof",
    "static", "struct", "switch", "typedef", "union", "unsigned", "void",
    "volatile", "while", "bool",
})


def mangle(name: str) -> str:
    return name + "_" if name in _C_KEYWORDS else name


# --- type mapping ----------------------------------------------------------

def c_type(dtype) -> str:
    cn = _dt_name(dtype)
    if cn == _DT_INT:
        bits = int(getattr(dtype, "bits", 32) or 32)
        signed = bool(getattr(dtype, "signed", False))
        if signed:
            return "int" if bits <= 32 else "int64_t"
        return f"uint{_prim_bits(bits)}_t"
    if cn == _DT_STRUCT:
        nm = dtype.name.split("::")[-1]
        if nm == "addr_handle_t":
            return "pssc_addr_t"
        return c_struct_name(dtype)
    raise ValueError(f"unsupported C type for {cn}")


# --- component introspection ----------------------------------------------

def _operations(comp) -> List[object]:
    return [fn for fn in comp.functions if func_kind(fn) == FuncKind.EXPORT_OP]


def _ctor(comp):
    for fn in comp.functions:
        if func_kind(fn) == FuncKind.CONSTRUCTOR:
            return fn
    return None


def _reg_group_fields(comp) -> Set[str]:
    return {f.name for f in comp.fields if field_is_reg_group(f)}


# --- handle + shim ---------------------------------------------------------

def emit_handle(prefix: str, link_style: str = "vtable") -> str:
    prefix_t = f"{prefix}_t"
    lines = ["/* ----- Component handle. ----- */", f"typedef struct {prefix}_s {{"]
    if link_style == "vtable":
        lines.append("    const pssc_mem_if *bus;")
    lines.append("    pssc_addr_t base;")
    lines.append(f"}} {prefix_t};")
    lines.append("")
    lines.append(
        "/* pssc_bus(s): the seam's first argument -- the ONLY line varying by style. */")
    if link_style == "vtable":
        lines.append(
            f"static inline const pssc_mem_if *pssc_bus(const {prefix_t} *s) "
            f"{{ return s->bus; }}")
    else:
        lines.append(
            f"static inline const void *pssc_bus(const {prefix_t} *s) "
            f"{{ (void)s; return (const void *)0; }}")
    return "\n".join(lines)


# --- signatures ------------------------------------------------------------

def _op_params(fn) -> str:
    parts = [f"{c_type(a.annotation)} {mangle(a.arg)}" for a in fn.args.args]
    return (", " + ", ".join(parts)) if parts else ""


def _op_signature(fn, prefix: str, qual: str = "") -> str:
    ret = c_type(fn.returns) if fn.returns is not None else "void"
    return f"{qual}{ret} {prefix}_{mangle(fn.name)}({prefix}_t *s{_op_params(fn)})"


def _create_params(ctor, link_style: str) -> str:
    parts = []
    if link_style == "vtable":
        parts.append("const pssc_mem_if *bus")
    if ctor is not None:
        parts += [f"{c_type(a.annotation)} {mangle(a.arg)}" for a in ctor.args.args]
    return ", ".join(parts)


# --- body translation ------------------------------------------------------

_BINOP = {
    "Add": "+", "Sub": "-", "Minus": "-", "Mult": "*", "Mul": "*",
    "Div": "/", "Mod": "%", "Eq": "==", "NotEq": "!=", "Ne": "!=",
    "Lt": "<", "LtE": "<=", "Le": "<=", "Gt": ">", "GtE": ">=", "Ge": ">=",
    "And": "&&", "Or": "||", "BitAnd": "&", "BitOr": "|", "BitXor": "^",
    "LShift": "<<", "Shl": "<<", "RShift": ">>", "Shr": ">>",
}


class _BodyEmitter:
    """Translate one operation body to C lines."""

    def __init__(self, fn, comp, prefix: str, reg_style: str = "bitfields"):
        self.fn = fn
        self.prefix = prefix
        self.reg_style = reg_style
        self.arg_rename = {a.arg: mangle(a.arg) for a in fn.args.args}
        self.arg_names = set(self.arg_rename)
        self.reg_fields = _reg_group_fields(comp)
        # struct-typed locals (name -> C value-union type), for --reg-style
        # accessors field get/set rewriting.
        self.struct_locals: Dict[str, str] = {}
        for s in fn.body:
            if _dt_name(s) == "StmtAnnAssign" and _dt_name(s.annotation) == _DT_STRUCT:
                nm = s.annotation.name.split("::")[-1]
                if nm != "addr_handle_t":
                    self.struct_locals[s.target.name] = c_type(s.annotation)

    def _struct_field(self, e):
        """If ``e`` is ``<struct-local>.<FIELD>``, return (ctype, local, field);
        else None. Used only in --reg-style accessors mode."""
        if _dt_name(e) != "ExprAttribute" or _dt_name(e.value) != "ExprRefLocal":
            return None
        local = e.value.name
        ct = self.struct_locals.get(local)
        if ct is None:
            return None
        return ct, local, e.attr

    # register access chain -------------------------------------------------

    def _chain(self, e):
        """Flatten self.<reg-group>...<reg>[idx] to [[name, index|None], ...],
        rooted at self; None if not a self-rooted access path."""
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
        """If ``call`` is a register read()/write(), return the baked-accessor
        call; else None."""
        func = call.func
        if _dt_name(func) != "ExprAttribute" or func.attr not in ("read", "write"):
            return None
        chain = self._chain(func.value)
        if not chain or chain[0][0] not in self.reg_fields:
            return None
        reg = chain[-1][0]
        segs = [c[0] for c in chain[:-1]]
        idx = [c[1] for c in chain if c[1] is not None]
        base = accessor_base(self.prefix, segs, reg)
        idx_args = "".join(f", {self.expr(i)}" for i in idx)
        if func.attr == "read":
            return f"{base}_read(s{idx_args})"
        return f"{base}_write(s{idx_args}, {self.expr(call.args[0])})"

    # expressions -----------------------------------------------------------

    def expr(self, e) -> str:
        cn = _dt_name(e)
        if cn == "ExprConstant":
            v = e.value
            if isinstance(v, bool):
                return "1" if v else "0"
            return str(v) if isinstance(v, int) else repr(v)
        if cn == "ExprRefLocal":
            return self.arg_rename.get(e.name, e.name)
        if cn == "ExprAttribute":
            base = e.value
            if _dt_name(base) == "TypeExprRefSelf":
                if e.attr in self.arg_names:
                    return self.arg_rename[e.attr]
                return e.attr           # static const, etc.
            if self.reg_style == "accessors":
                sf = self._struct_field(e)
                if sf is not None:
                    ct, local, field = sf
                    return f"{ct}_{field}_get({local})"
            return f"{self.expr(base)}.{e.attr}"
        if cn == "ExprSubscript":
            return f"{self.expr(e.value)}[{self.expr(e.slice)}]"
        if cn == "ExprBin":
            op = _BINOP.get(e.op.name)
            if op is None:
                raise ValueError(f"unsupported binop {e.op.name}")
            return f"{self.expr(e.lhs)} {op} {self.expr(e.rhs)}"
        if cn == "ExprCall":
            rc = self._reg_call(e)
            if rc is not None:
                return rc
            args = ", ".join(self.expr(a) for a in e.args)
            return f"{self.expr(e.func)}({args})"
        raise ValueError(f"unsupported expr {cn}")

    # statements ------------------------------------------------------------

    def stmts(self, body, ind: int) -> List[str]:
        out: List[str] = []
        for s in body:
            out += self.stmt(s, ind)
        return out

    def stmt(self, s, ind: int) -> List[str]:
        pad = "    " * ind
        cn = _dt_name(s)
        if cn == "StmtAnnAssign":
            ct = c_type(s.annotation)
            name = self.expr(s.target)
            if getattr(s, "value", None) is not None:
                return [f"{pad}{ct} {name} = {self.expr(s.value)};"]
            if _dt_name(s.annotation) == _DT_STRUCT:
                return [f"{pad}{ct} {name} = {{0}};"]   # zero reserved/padding bits
            return [f"{pad}{ct} {name};"]
        if cn == "StmtAssign":
            tgt = s.targets[0]
            if self.reg_style == "accessors":
                sf = self._struct_field(tgt)
                if sf is not None:
                    ct, local, field = sf
                    return [f"{pad}{ct}_{field}_set(&{local}, {self.expr(s.value)});"]
            return [f"{pad}{self.expr(tgt)} = {self.expr(s.value)};"]
        if cn == "StmtExpr":
            return [f"{pad}{self.expr(s.expr)};"]
        if cn == "StmtReturn":
            if s.value is not None:
                return [f"{pad}return {self.expr(s.value)};"]
            return [f"{pad}return;"]
        if cn == "StmtIf":
            lines = [f"{pad}if ({self.expr(s.test)}) {{"]
            lines += self.stmts(s.body, ind + 1)
            if getattr(s, "orelse", None):
                lines.append(f"{pad}}} else {{")
                lines += self.stmts(s.orelse, ind + 1)
            lines.append(f"{pad}}}")
            return lines
        if cn == "StmtRepeatWhile":
            lines = [f"{pad}do {{"]
            lines += self.stmts(s.body, ind + 1)
            lines.append(f"{pad}}} while ({self.expr(s.condition)});")
            return lines
        if cn == "StmtWhile":
            lines = [f"{pad}while ({self.expr(s.condition)}) {{"]
            lines += self.stmts(s.body, ind + 1)
            lines.append(f"{pad}}}")
            return lines
        raise ValueError(f"unsupported stmt {cn}")


# --- emission --------------------------------------------------------------

def lower_decls(root_dtype, prefix: str, *, link_style: str = "vtable") -> str:
    ctor = _ctor(root_dtype)
    cp = _create_params(ctor, link_style)
    prefix_t = f"{prefix}_t"
    lines = ["/* ----- Export API + lifecycle. ----- */"]
    lines.append(f"{prefix_t} *{prefix}_create({cp});")
    lines.append(f"void {prefix}_init({prefix_t} *self, {cp});")
    lines.append(f"void {prefix}_destroy({prefix_t} *self);")
    lines.append("")
    for fn in _operations(root_dtype):
        lines.append(f"{_op_signature(fn, prefix)};")
    return "\n".join(lines)


def _lifecycle_impl(root_dtype, prefix: str, link_style: str, qual: str) -> List[str]:
    ctor = _ctor(root_dtype)
    cp = _create_params(ctor, link_style)
    prefix_t = f"{prefix}_t"
    addr_arg = mangle(ctor.args.args[0].arg) if (ctor and ctor.args.args) else "base"
    fwd = []
    if link_style == "vtable":
        fwd.append("bus")
    if ctor:
        fwd += [mangle(a.arg) for a in ctor.args.args]
    fwd_s = ", ".join(fwd)

    lines = [f"{qual}void {prefix}_init({prefix_t} *self, {cp}) {{"]
    if link_style == "vtable":
        lines.append("    self->bus = bus;")
    lines.append(f"    self->base = {addr_arg};")     # PSS: regs.set_handle(base)
    lines.append("}")
    lines.append(f"{qual}{prefix_t} *{prefix}_create({cp}) {{")
    lines.append(f"    {prefix_t} *self = ({prefix_t} *)malloc(sizeof({prefix_t}));")
    lines.append(f"    if (self) {prefix}_init(self, {fwd_s});")
    lines.append("    return self;")
    lines.append("}")
    lines.append(f"{qual}void {prefix}_destroy({prefix_t} *self) {{ free(self); }}")
    return lines


def lower_impl(root_dtype, prefix: str, *, link_style: str = "vtable",
               static_inline: bool = False, reg_style: str = "bitfields") -> str:
    qual = "static inline " if static_inline else ""
    lines: List[str] = ["/* ----- Component lifecycle + operations. ----- */"]
    lines += _lifecycle_impl(root_dtype, prefix, link_style, qual)
    lines.append("")
    for fn in _operations(root_dtype):
        be = _BodyEmitter(fn, root_dtype, prefix, reg_style=reg_style)
        lines.append(f"{_op_signature(fn, prefix, qual)} {{")
        lines += be.stmts(fn.body, 1)
        lines.append("}")
        lines.append("")
    return "\n".join(lines).rstrip()
