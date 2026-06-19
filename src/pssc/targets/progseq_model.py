"""Backend-neutral model for programming-sequence generation.

Walks a PSS component tree (rooted at a named component) and classifies each
reachable component, and classifies functions by kind. Deliberately free of any
SystemVerilog/C specifics so future backends (SV now; C-embedded, C++/host
later -- design §10.6) can share it.

See design/pss-programming-seq-gen-design.md (§6.2) and
design/pss-programming-seq-gen-impl-plan.md (Phase 0 findings).
"""
from __future__ import annotations

import dataclasses as dc
from enum import Enum
from typing import Dict, List, Optional, Tuple


# --- Function kind ---------------------------------------------------------

class FuncKind(Enum):
    """How a PSS function maps to a generated artifact."""
    CONSTRUCTOR = "constructor"   # solve `ctor` -> impl constructor
    EXPORT_OP = "export_op"       # component operation -> export-API task
    EXPORT_SOLVE = "export_solve"  # export solve fn -> export-API function
    IMPORT_TASK = "import_task"   # import target fn -> import-API task
    IMPORT_SOLVE = "import_solve"  # import solve fn -> import-API function
    REG_OFFSET = "reg_offset"     # get_offset_of_instance[_array] -- evaluated, not emitted


#: Register-group offset functions are consumed by the generator (to compute
#: addresses) rather than emitted as callable API.
_REG_OFFSET_FNS = frozenset({"get_offset_of_instance", "get_offset_of_instance_array"})


def func_kind(fn) -> FuncKind:
    """Classify an ``ir.Function`` by the flags the front end already sets.

    Phase-0 finding: the IR carries ``is_import`` / ``is_target`` / ``is_solve``;
    component operations carry none of them. ``ctor`` is the solve constructor;
    the register offset functions are recognized by name.
    """
    if fn.name in _REG_OFFSET_FNS:
        return FuncKind.REG_OFFSET
    if getattr(fn, "is_solve", False):
        return FuncKind.CONSTRUCTOR if fn.name == "ctor" else FuncKind.EXPORT_SOLVE
    if getattr(fn, "is_import", False):
        return FuncKind.IMPORT_SOLVE if getattr(fn, "is_solve", False) else FuncKind.IMPORT_TASK
    return FuncKind.EXPORT_OP


# --- Component classification ----------------------------------------------

class CompKind(Enum):
    REG_GROUP = "reg_group"     # super chain includes reg_group_c
    REGULAR = "regular"         # everything else (has operations / sub-components)


def _super_ref_name(dtype) -> Optional[str]:
    """Return the immediate super type's ``ref_name`` if present, else None."""
    sup = getattr(dtype, "super", None)
    if sup is None:
        return None
    return getattr(sup, "ref_name", None) or getattr(sup, "name", None)


def is_reg_group(dtype) -> bool:
    """True if ``dtype`` is (or derives from) ``reg_group_c``."""
    return _super_ref_name(dtype) == "reg_group_c"


def comp_kind(dtype) -> CompKind:
    return CompKind.REG_GROUP if is_reg_group(dtype) else CompKind.REGULAR


# --- Field / sub-component introspection -----------------------------------

# IR datatype class names (matched by name to avoid importing ir here).
_DT_REGISTER = "DataTypeRegister"
_DT_REGISTER_GROUP = "DataTypeRegisterGroup"
_DT_ARRAY = "DataTypeArray"


def _dt_name(dtype) -> str:
    return type(dtype).__name__


def field_is_register(field) -> bool:
    return _dt_name(field.datatype) == _DT_REGISTER


def field_is_reg_group(field) -> bool:
    return _dt_name(field.datatype) == _DT_REGISTER_GROUP


def field_is_array(field) -> bool:
    return _dt_name(field.datatype) == _DT_ARRAY


def array_element_type(field):
    """Element datatype of an array field."""
    return field.datatype.element_type


def array_size(field) -> int:
    return int(field.datatype.size)


@dc.dataclass
class CompNode:
    """One component type in the walked tree."""
    name: str                       # qualified IR name
    dtype: object                   # DataTypeComponent / RegisterGroup
    kind: CompKind
    children: List["CompNode"] = dc.field(default_factory=list)


def walk_tree(root_dtype, resolve) -> CompNode:
    """Walk the component tree from ``root_dtype``.

    ``resolve(dtype) -> dtype`` maps a (possibly ref/array-element) datatype to
    its defining component datatype; callers supply it so this module stays
    independent of the type table. Register-group and regular sub-components are
    both recorded; register/array-of-register leaves are not components and are
    handled by the register-model emitter.
    """
    seen: Dict[int, CompNode] = {}

    def visit(dtype) -> CompNode:
        key = id(dtype)
        if key in seen:
            return seen[key]
        node = CompNode(
            name=getattr(dtype, "name", None) or "<anon>",
            dtype=dtype,
            kind=comp_kind(dtype),
        )
        seen[key] = node
        for f in getattr(dtype, "fields", []) or []:
            child_dt = None
            if field_is_reg_group(f):
                child_dt = f.datatype
            elif field_is_array(f) and _dt_name(array_element_type(f)) == _DT_REGISTER_GROUP:
                child_dt = array_element_type(f)
            elif _dt_name(f.datatype) == "DataTypeComponent":
                child_dt = f.datatype
            if child_dt is not None:
                node.children.append(visit(resolve(child_dt)))
        return node

    return visit(root_dtype)


# --- affine offset evaluation (language-neutral) ---------------------------
# Hoisted from sv/lower_reg_model.py so every backend (SV, C, C++) shares one
# copy. These evaluate the PSS `get_offset_of_instance[_array]` bodies, which are
# entirely language-neutral; SV, C, and C++ all need (base, stride) and scalar
# offsets. See design/pss-c-cpp-progseq-gen-design.md §6.1.

_DT_STRUCT = "DataTypeStruct"


def _eval_off(expr, index: int) -> int:
    """Evaluate an affine offset expression at array ``index``."""
    cn = _dt_name(expr)
    if cn == "ExprConstant":
        return int(expr.value)
    if cn == "ExprAttribute" and getattr(expr, "attr", None) == "index":
        return index
    if cn == "ExprBin":
        l = _eval_off(expr.lhs, index)
        r = _eval_off(expr.rhs, index)
        op = expr.op.name
        if op in ("Add",):
            return l + r
        if op in ("Sub", "Minus"):
            return l - r
        if op in ("Mul", "Mult"):
            return l * r
        raise ValueError(f"unsupported offset op {op}")
    raise ValueError(f"unsupported offset expr {cn}")


def _pattern_str(pattern) -> Optional[str]:
    """The string value of a ``PatternValue`` whose value is a string constant,
    else None. (``PatternValue.value`` is an ``ExprConstant``.)"""
    if _dt_name(pattern) != "PatternValue":
        return None
    v = getattr(pattern, "value", None)
    inner = getattr(v, "value", None)
    return inner if isinstance(inner, str) else None


def _array_base_stride(group_dtype, field_name: str) -> Tuple[int, int]:
    """Return (base, stride) for an array child by evaluating the affine
    ``get_offset_of_instance_array`` arm whose pattern matches ``field_name``."""
    for fn in getattr(group_dtype, "functions", []) or []:
        if fn.name != "get_offset_of_instance_array":
            continue
        if not fn.body or _dt_name(fn.body[0]) != "StmtMatch":
            continue
        for case in fn.body[0].cases:
            if _pattern_str(case.pattern) == field_name:
                expr = case.body[0].value   # StmtReturn.value
                base = _eval_off(expr, 0)
                stride = _eval_off(expr, 1) - base
                return base, stride
    raise ValueError(f"no array offset for {field_name}")


def _scalar_offset(group_dtype, name: str) -> int:
    return int(group_dtype.offset_map[name])


# --- value-struct / reg-group collection walks (language-neutral) ----------
# Hoisted from sv/lower_reg_model.py; they produce the ordered type lists every
# backend emits. See design §6.2.

def _is_reserved(field) -> bool:
    """Reserved-gap fields (leading underscore) are not surfaced; their space is
    already accounted for in following siblings' offsets."""
    return field.name.startswith("_")


def collect_reg_groups(root_dtype) -> List[object]:
    """Post-order list of unique reg-group datatypes reachable from ``root``
    (nested groups before the groups that use them)."""
    out: List[object] = []
    seen = set()

    def visit(dt):
        if id(dt) in seen:
            return
        seen.add(id(dt))
        for f in getattr(dt, "fields", []) or []:
            child = None
            if field_is_reg_group(f):
                child = f.datatype
            elif field_is_array(f) and _dt_name(array_element_type(f)) == _DT_REGISTER_GROUP:
                child = array_element_type(f)
            if child is not None and is_reg_group(child):
                visit(child)
        out.append(dt)

    # Start from reg-group fields of the (possibly regular) root.
    if is_reg_group(root_dtype):
        visit(root_dtype)
    else:
        for f in getattr(root_dtype, "fields", []) or []:
            if field_is_reg_group(f) and is_reg_group(f.datatype):
                visit(f.datatype)
    return out


def collect_value_structs(groups: List[object]) -> List[object]:
    """Unique register value structs used across ``groups``, first-use order."""
    out: List[object] = []
    seen = set()

    def consider(reg_dtype):
        vt = reg_dtype.register_value_type
        if _dt_name(vt) == _DT_STRUCT and id(vt) not in seen:
            seen.add(id(vt))
            out.append(vt)

    for g in groups:
        for f in g.fields:
            if field_is_register(f):
                consider(f.datatype)
            elif field_is_array(f) and _dt_name(array_element_type(f)) == _DT_REGISTER:
                consider(array_element_type(f))
    return out
