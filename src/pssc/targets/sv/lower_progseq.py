"""Lower a regular PSS component (its operations + sub-components) to the SV
programming API: an export-API interface class and an implementation class.

The export API is one ``task`` per runtime operation (PSS ``int`` return ->
``output int status``; every following arg explicit ``input``; SV-keyword args
renamed). The impl translates each body 1:1, rewriting register access to the
task form (``x = r.read()`` -> ``r.read(x)``) and ``repeat{}while`` to
``forever .. break`` (design §6.5/§6.6).

It also emits the import-API interface and the component handle/factory class
(`emit_component`) -- a single class named after the component that redirects the
import API to the user object and exposes the static `create()`.
"""
from __future__ import annotations

from typing import Dict, List, Optional

from ..progseq_model import func_kind, FuncKind, field_is_reg_group, _dt_name

_DT_STRUCT = "DataTypeStruct"
_DT_INT = "DataTypeInt"

# SystemVerilog reserved words that can appear as PSS identifiers; renamed by
# appending '_' so generated code compiles. (Extend as needed.)
_SV_KEYWORDS = frozenset({
    "priority", "wait", "do", "final", "time", "table", "type", "begin", "end",
    "fork", "join", "wire", "reg", "logic", "bit", "byte", "int", "shortint",
    "longint", "module", "endmodule", "class", "endclass", "task", "function",
    "return", "default", "force", "release", "assign", "static", "automatic",
    "local", "protected", "virtual", "ref", "const", "event", "disable",
})


def _strip_pkg(name: Optional[str]) -> str:
    return name.split("::")[-1] if name else name


def mangle(name: str) -> str:
    """Rename an identifier that collides with an SV keyword."""
    return name + "_" if name in _SV_KEYWORDS else name


# --- type mapping ----------------------------------------------------------

def sv_type(dtype) -> str:
    """SV type string for a PSS datatype used as an arg/return/local."""
    cn = _dt_name(dtype)
    if cn == _DT_INT:
        bits = int(getattr(dtype, "bits", 32) or 32)
        signed = bool(getattr(dtype, "signed", False))
        if signed and bits == 32:
            return "int"
        if bits == 1:
            return "bit"
        return f"bit [{bits - 1}:0]"
    if cn == _DT_STRUCT:
        nm = _strip_pkg(dtype.name)
        # addr_reg_pkg::addr_handle_t -> the core typedef
        return "addr_handle_t" if nm == "addr_handle_t" else nm
    raise ValueError(f"unsupported SV type for {cn}")


# --- signatures ------------------------------------------------------------

def _arg_names(fn) -> List[str]:
    return [a.arg for a in fn.args.args]


def _signature(fn) -> str:
    """Build the parenthesized task signature for operation ``fn``.

    ``int`` return becomes a leading ``output int status``; every following arg
    is explicit ``input`` (SV inherits the previous direction otherwise -- a
    real codegen pitfall).
    """
    parts: List[str] = []
    if fn.returns is not None:
        parts.append(f"output {sv_type(fn.returns)} status")
    for a in fn.args.args:
        parts.append(f"input {sv_type(a.annotation)} {mangle(a.arg)}")
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
    """Translate one function body to SV lines."""

    def __init__(self, fn, comp, member_of):
        self.fn = fn
        # rename map for SV-keyword args
        self.arg_rename = {a.arg: mangle(a.arg) for a in fn.args.args}
        self.arg_names = set(self.arg_rename)
        # component field name -> member ref (reg-group fields become m_<name>)
        self.member_of = member_of  # dict: field_name -> "m_<field>"
        self.has_status = fn.returns is not None

    # expressions ----------------------------------------------------------

    def expr(self, e) -> str:
        cn = _dt_name(e)
        if cn == "ExprConstant":
            v = e.value
            return str(int(v)) if isinstance(v, bool) else (str(v) if isinstance(v, int) else repr(v))
        if cn == "ExprRefLocal":
            return self.arg_rename.get(e.name, e.name)
        if cn == "TypeExprRefSelf":
            return "this"
        if cn == "ExprAttribute":
            base = e.value
            if _dt_name(base) == "TypeExprRefSelf":
                # self.<x>: a component field -> member; a function arg -> name
                if e.attr in self.member_of:
                    return self.member_of[e.attr]
                if e.attr in self.arg_names:
                    return self.arg_rename[e.attr]
                return e.attr
            return f"{self.expr(base)}.{e.attr}"
        if cn == "ExprSubscript":
            return f"{self.expr(e.value)}[{self.expr(e.slice)}]"
        if cn == "ExprBin":
            op = _BINOP.get(e.op.name)
            if op is None:
                raise ValueError(f"unsupported binop {e.op.name}")
            return f"{self.expr(e.lhs)} {op} {self.expr(e.rhs)}"
        if cn == "ExprCall":
            callee = e.func
            args = ", ".join(self.expr(a) for a in e.args)
            return f"{self.expr(callee)}({args})"
        raise ValueError(f"unsupported expr {cn}")

    # statements -----------------------------------------------------------

    def stmts(self, body, ind: int) -> List[str]:
        out: List[str] = []
        for s in body:
            out += self.stmt(s, ind)
        return out

    def stmt(self, s, ind: int) -> List[str]:
        pad = "  " * ind
        cn = _dt_name(s)
        if cn == "StmtAnnAssign":
            # local variable declaration (no initializer); bits default to 0.
            return [f"{pad}{sv_type(s.annotation)} {self.expr(s.target)};"]
        if cn == "StmtAssign":
            # register read rewrite: lhs = r.read()  ->  r.read(lhs);
            target = s.targets[0]
            v = s.value
            if (_dt_name(v) == "ExprCall"
                    and _dt_name(v.func) == "ExprAttribute"
                    and v.func.attr == "read" and not v.args):
                return [f"{pad}{self.expr(v.func.value)}.read({self.expr(target)});"]
            return [f"{pad}{self.expr(target)} = {self.expr(v)};"]
        if cn == "StmtExpr":
            return [f"{pad}{self.expr(s.expr)};"]
        if cn == "StmtReturn":
            if self.has_status and s.value is not None:
                return [f"{pad}status = {self.expr(s.value)};", f"{pad}return;"]
            return [f"{pad}return;"]
        if cn == "StmtIf":
            lines = [f"{pad}if ({self.expr(s.test)}) begin"]
            lines += self.stmts(s.body, ind + 1)
            if getattr(s, "orelse", None):
                lines.append(f"{pad}end else begin")
                lines += self.stmts(s.orelse, ind + 1)
            lines.append(f"{pad}end")
            return lines
        if cn == "StmtRepeatWhile":
            # PSS do-while: execute body, continue while cond -> forever .. break
            lines = [f"{pad}forever begin"]
            lines += self.stmts(s.body, ind + 1)
            lines.append(f"{pad}  if (!({self.expr(s.condition)})) break;")
            lines.append(f"{pad}end")
            return lines
        if cn == "StmtWhile":
            lines = [f"{pad}while ({self.expr(s.condition)}) begin"]
            lines += self.stmts(s.body, ind + 1)
            lines.append(f"{pad}end")
            return lines
        raise ValueError(f"unsupported stmt {cn}")


# --- emission --------------------------------------------------------------

def _operations(comp) -> List[object]:
    return [fn for fn in comp.functions if func_kind(fn) == FuncKind.EXPORT_OP]


def _reg_group_members(comp) -> Dict[str, str]:
    """Map reg-group field name -> SV member name (``m_<name>``)."""
    return {f.name: f"m_{f.name}" for f in comp.fields if field_is_reg_group(f)}


def emit_export_api(comp) -> str:
    cls = f"{_strip_pkg(comp.name)}_if"
    lines = [f"  interface class {cls};"]
    for fn in _operations(comp):
        lines.append(f"    pure virtual task {mangle(fn.name)}({_signature(fn)});")
    lines.append("  endclass")
    return "\n".join(lines)


def _ctor(comp):
    for fn in comp.functions:
        if func_kind(fn) == FuncKind.CONSTRUCTOR:
            return fn
    return None


def lower_component_api(comp) -> str:
    """Export interface for a regular component, as package-body text.

    The implementation is folded into the component class itself (see
    `emit_component`), so there is no separate `<comp>_impl`.
    """
    return emit_export_api(comp)


# --- import API, adapter, factory (Phase 5) --------------------------------

# The core memory-access ABI: (method, data-type, is_read). Frozen to match
# pssc_reg_pkg::pss_mem_if.
_MEM_PRIMS = [
    ("write8", "bit [7:0]", False), ("read8", "bit [7:0]", True),
    ("write16", "bit [15:0]", False), ("read16", "bit [15:0]", True),
    ("write32", "bit [31:0]", False), ("read32", "bit [31:0]", True),
    ("write64", "bit [63:0]", False), ("read64", "bit [63:0]", True),
]


def emit_import_api(root) -> str:
    """``interface class <root>_import_if extends pss_mem_if`` plus any
    engine-specific import functions (none for the WB DMA engine)."""
    cls = f"{_strip_pkg(root.name)}_import_if"
    lines = [f"  interface class {cls} extends pss_mem_if;"]
    for fn in root.functions:
        k = func_kind(fn)
        if k == FuncKind.IMPORT_TASK:
            lines.append(f"    pure virtual task {mangle(fn.name)}({_signature(fn)});")
        elif k == FuncKind.IMPORT_SOLVE:
            ret = sv_type(fn.returns) if fn.returns is not None else "void"
            lines.append(f"    pure virtual function {ret} {mangle(fn.name)}({_signature(fn)});")
    lines.append("  endclass")
    return "\n".join(lines)


def emit_component(root) -> str:
    """The component class, named after the component itself -- one class that is

      * the **export implementation** (`implements <comp>_if`, the operations),
      * the **import redirect** (`implements <comp>_import_if`, forwarding each
        primitive to the user object `m_imp`), and
      * the **factory** (static `create()`).

    It holds the register model, constructed with ``this`` as the bus: because
    the class is-a ``pss_mem_if`` (via the import interface), register accesses
    route ``m_regs -> this.write32/read32 -> m_imp`` to the user object. ``IMP_T``
    defaults to the component's ``import_if``; override it to wire a
    signature-compatible (duck-typed) object that does not formally implement it.
    """
    name = _strip_pkg(root.name)
    api = f"{name}_if"
    import_if = f"{name}_import_if"
    members = _reg_group_members(root)

    ctor = _ctor(root)
    ctor_params = ""
    fwd = ""
    base_arg = "base"
    if ctor is not None and ctor.args.args:
        ps = [f"{sv_type(a.annotation)} {mangle(a.arg)}" for a in ctor.args.args]
        names = [mangle(a.arg) for a in ctor.args.args]
        ctor_params = ", " + ", ".join(ps)
        fwd = ", " + ", ".join(names)
        base_arg = mangle(ctor.args.args[0].arg)

    lines = [
        f"  class {name} #(type IMP_T = {import_if}) implements {api}, {import_if};",
        f"    protected IMP_T m_imp;",
    ]
    for f in root.fields:
        if field_is_reg_group(f):
            lines.append(f"    protected {_strip_pkg(f.datatype.name)} {members[f.name]};")
    lines.append("")

    # constructor: store the user object; build the register model with `this`
    # as the bus (this is-a pss_mem_if -> accesses route back through m_imp).
    lines.append(f"    function new(IMP_T imp{ctor_params});")
    lines.append(f"      m_imp = imp;")
    for f in root.fields:
        if field_is_reg_group(f):
            lines.append(f"      {members[f.name]} = new(this, {base_arg});")
    lines.append("    endfunction")
    lines.append("")

    # export operations (virtual -- they implement the export interface's pure
    # virtuals; stricter simulators, e.g. Vivado xsim, require the override).
    for fn in _operations(root):
        be = _BodyEmitter(fn, root, members)
        lines.append(f"    virtual task {mangle(fn.name)}({_signature(fn)});")
        lines += be.stmts(fn.body, 3)
        lines.append("    endtask")
        lines.append("")

    # import redirect: forward each memory-access primitive to the user object.
    for meth, dt, is_read in _MEM_PRIMS:
        if is_read:
            lines.append(
                f"    virtual task {meth}(addr_handle_t addr, output {dt} data); "
                f"m_imp.{meth}(addr, data); endtask")
        else:
            lines.append(
                f"    virtual task {meth}(addr_handle_t addr, {dt} data); "
                f"m_imp.{meth}(addr, data); endtask")

    # static factory entry point -> returns the export-interface handle.
    lines += [
        f"    static function {api} create(IMP_T imp{ctor_params});",
        f"      {name} #(IMP_T) self = new(imp{fwd});",
        f"      return self;",
        f"    endfunction",
        f"  endclass",
    ]
    return "\n".join(lines)


def lower_root_glue(root) -> str:
    """Import interface + the merged component class for the root component."""
    return "\n\n".join([emit_import_api(root), emit_component(root)])
