"""Lower a regular PSS component to the C++ programming API: the pure-virtual
export/import interfaces, the component class (implements the export API, holds a
``pssc::mem_if&`` and the register model -- no redirect trick), and the factory.

Bodies translate the PSS procedural subset 1:1, and -- like SV but unlike the
free-function C backend -- keep native member-call register access
(``regs_.channels[ch].CSR.read()``), native value reads, native ``do...while``,
and native return values.

Design: design/pss-c-cpp-progseq-gen-design.md (§4.4, §4.5).
"""
from __future__ import annotations

from typing import Dict, List

from ..progseq_model import func_kind, FuncKind, field_is_reg_group, _dt_name
from ..c.lower_reg_model import c_struct_name, _prim_bits, _strip_pkg

_DT_STRUCT = "DataTypeStruct"
_DT_INT = "DataTypeInt"

_CPP_KEYWORDS = frozenset({
    "alignas", "alignof", "and", "asm", "auto", "bool", "break", "case", "catch",
    "char", "class", "const", "constexpr", "continue", "default", "delete", "do",
    "double", "else", "enum", "explicit", "export", "extern", "false", "float",
    "for", "friend", "goto", "if", "inline", "int", "long", "mutable", "namespace",
    "new", "not", "operator", "or", "private", "protected", "public", "register",
    "return", "short", "signed", "sizeof", "static", "struct", "switch", "template",
    "this", "throw", "true", "try", "typedef", "typename", "union", "unsigned",
    "using", "virtual", "void", "volatile", "while", "xor",
})


def mangle(name: str) -> str:
    return name + "_" if name in _CPP_KEYWORDS else name


def cpp_type(dtype) -> str:
    cn = _dt_name(dtype)
    if cn == _DT_INT:
        bits = int(getattr(dtype, "bits", 32) or 32)
        signed = bool(getattr(dtype, "signed", False))
        if not signed and bits == 1:
            return "bool"
        if signed:
            return "int" if bits <= 32 else "std::int64_t"
        return f"std::uint{_prim_bits(bits)}_t"
    if cn == _DT_STRUCT:
        nm = dtype.name.split("::")[-1]
        if nm == "addr_handle_t":
            return "pssc::addr_t"
        return c_struct_name(dtype)
    raise ValueError(f"unsupported C++ type for {cn}")


def _operations(comp) -> List[object]:
    return [fn for fn in comp.functions if func_kind(fn) == FuncKind.EXPORT_OP]


def _ctor(comp):
    for fn in comp.functions:
        if func_kind(fn) == FuncKind.CONSTRUCTOR:
            return fn
    return None


def _reg_group_members(comp) -> Dict[str, str]:
    return {f.name: f"{f.name}_" for f in comp.fields if field_is_reg_group(f)}


def _params(fn) -> str:
    return ", ".join(f"{cpp_type(a.annotation)} {mangle(a.arg)}" for a in fn.args.args)


def _ret(fn) -> str:
    return cpp_type(fn.returns) if fn.returns is not None else "void"


# --- body translation ------------------------------------------------------

_BINOP = {
    "Add": "+", "Sub": "-", "Minus": "-", "Mult": "*", "Mul": "*",
    "Div": "/", "Mod": "%", "Eq": "==", "NotEq": "!=", "Ne": "!=",
    "Lt": "<", "LtE": "<=", "Le": "<=", "Gt": ">", "GtE": ">=", "Ge": ">=",
    "And": "&&", "Or": "||", "BitAnd": "&", "BitOr": "|", "BitXor": "^",
    "LShift": "<<", "Shl": "<<", "RShift": ">>", "Shr": ">>",
}


class _BodyEmitter:
    def __init__(self, fn, comp):
        self.fn = fn
        self.arg_rename = {a.arg: mangle(a.arg) for a in fn.args.args}
        self.arg_names = set(self.arg_rename)
        self.member_of = _reg_group_members(comp)   # regs -> regs_

    def expr(self, e) -> str:
        cn = _dt_name(e)
        if cn == "ExprConstant":
            v = e.value
            if isinstance(v, bool):
                return "true" if v else "false"
            return str(v) if isinstance(v, int) else repr(v)
        if cn == "ExprRefLocal":
            return self.arg_rename.get(e.name, e.name)
        if cn == "ExprAttribute":
            base = e.value
            if _dt_name(base) == "TypeExprRefSelf":
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
            args = ", ".join(self.expr(a) for a in e.args)
            return f"{self.expr(e.func)}({args})"
        raise ValueError(f"unsupported expr {cn}")

    def stmts(self, body, ind: int) -> List[str]:
        out: List[str] = []
        for s in body:
            out += self.stmt(s, ind)
        return out

    def stmt(self, s, ind: int) -> List[str]:
        pad = "    " * ind
        cn = _dt_name(s)
        if cn == "StmtAnnAssign":
            ct = cpp_type(s.annotation)
            name = self.expr(s.target)
            if getattr(s, "value", None) is not None:
                return [f"{pad}{ct} {name} = {self.expr(s.value)};"]
            if _dt_name(s.annotation) == _DT_STRUCT:
                return [f"{pad}{ct} {name}{{}};"]    # value-init: zero reserved bits
            return [f"{pad}{ct} {name};"]
        if cn == "StmtAssign":
            return [f"{pad}{self.expr(s.targets[0])} = {self.expr(s.value)};"]
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

def emit_export_api(root, cls: str) -> str:
    lines = [f"struct {cls}_if {{", f"    virtual ~{cls}_if() = default;"]
    for fn in _operations(root):
        lines.append(f"    virtual {_ret(fn)} {mangle(fn.name)}({_params(fn)}) = 0;")
    lines.append("};")
    return "\n".join(lines)


def emit_import_api(root, cls: str) -> str:
    lines = [f"struct {cls}_import_if : pssc::mem_if {{"]
    for fn in root.functions:
        k = func_kind(fn)
        if k == FuncKind.IMPORT_TASK:
            lines.append(f"    virtual void {mangle(fn.name)}({_params(fn)}) = 0;")
        elif k == FuncKind.IMPORT_SOLVE:
            lines.append(f"    virtual {_ret(fn)} {mangle(fn.name)}({_params(fn)}) = 0;")
    lines.append("};")
    return "\n".join(lines)


def emit_component(root, cls: str) -> str:
    members = _reg_group_members(root)
    ctor = _ctor(root)
    ctor_params = ", ".join([f"{cpp_type(a.annotation)} {mangle(a.arg)}"
                             for a in (ctor.args.args if ctor else [])])
    full_params = "pssc::mem_if &imp" + (", " + ctor_params if ctor_params else "")
    addr_arg = mangle(ctor.args.args[0].arg) if (ctor and ctor.args.args) else "base"
    fwd = ", ".join(["imp"] + [mangle(a.arg) for a in (ctor.args.args if ctor else [])])

    lines = [f"class {cls} : public {cls}_if {{", "    pssc::mem_if &imp_;"]
    inits = ["imp_(imp)"]
    for f in root.fields:
        if field_is_reg_group(f):
            gt = _strip_pkg(f.datatype.name)
            lines.append(f"    {gt} {members[f.name]};")
            inits.append(f"{members[f.name]}(imp_, {addr_arg})")
    lines.append("public:")
    lines.append(f"    {cls}({full_params}) : " + ", ".join(inits) + " {}")
    lines.append("")
    for fn in _operations(root):
        be = _BodyEmitter(fn, root)
        lines.append(f"    {_ret(fn)} {mangle(fn.name)}({_params(fn)}) override {{")
        lines += be.stmts(fn.body, 2)
        lines.append("    }")
    lines.append("")
    lines.append(f"    static std::unique_ptr<{cls}_if> create({full_params}) {{")
    lines.append(f"        return std::make_unique<{cls}>({fwd});")
    lines.append("    }")
    lines.append("};")
    return "\n".join(lines)


def lower_component(root, cls: str) -> str:
    return "\n\n".join([emit_export_api(root, cls), emit_import_api(root, cls),
                        emit_component(root, cls)])
