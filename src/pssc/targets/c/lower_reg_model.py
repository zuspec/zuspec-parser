"""Lower a PSS register tree to C: value unions + baked inline accessors.

Emits, for the register subtree reachable from a root component:
  * one C11 anonymous-union value type per register value struct (fields in
    declaration order -- LSB-first, the opposite of SV; little-endian assumed);
  * a baked ``static inline`` accessor trio (``_addr``/``_read``/``_write``) per
    register, with the address arithmetic folded to gen-time constants (only the
    component ``base`` and any array indices are runtime). The accessors call the
    seam primitives ``pssc_r*/w*(pssc_bus(s), ...)`` and are emitted identically
    across all link styles; only ``pssc_bus`` (emitted in lower_progseq) varies.

Design: design/pss-c-cpp-progseq-gen-design.md (§3.3, §3.4).
"""
from __future__ import annotations

import dataclasses as dc
from typing import List, Optional

from ..progseq_model import (
    field_is_register, field_is_array, field_is_reg_group, array_element_type,
    _dt_name, _scalar_offset, _array_base_stride, _is_reserved,
    collect_reg_groups, collect_value_structs,
)

_DT_REGISTER = "DataTypeRegister"
_DT_REGISTER_GROUP = "DataTypeRegisterGroup"
_DT_STRUCT = "DataTypeStruct"


# --- small helpers ---------------------------------------------------------

def _strip_pkg(name: Optional[str]) -> str:
    return name.split("::")[-1] if name else name


def c_struct_name(struct_dtype) -> str:
    """C value-type name for a register value struct: ``dma_csr_s`` -> ``dma_csr_t``."""
    n = _strip_pkg(struct_dtype.name)
    return (n[:-2] + "_t") if n.endswith("_s") else (n + "_t")


def _prim_bits(bits: int) -> int:
    for w in (8, 16, 32, 64):
        if bits <= w:
            return w
    return 64


def _struct_total_bits(struct_dtype) -> int:
    return sum(int(f.datatype.bits) for f in struct_dtype.fields)


def _reg_value_bits(reg_dtype) -> int:
    sb = getattr(reg_dtype, "size_bits", None)
    if sb:
        return int(sb)
    vt = reg_dtype.register_value_type
    if _dt_name(vt) == _DT_STRUCT:
        return _struct_total_bits(vt)
    return int(getattr(vt, "bits", 32) or 32)


def _reg_is_struct(reg_dtype) -> bool:
    return _dt_name(reg_dtype.register_value_type) == _DT_STRUCT


def _reg_c_type(reg_dtype) -> str:
    """C value type for a register: a value-union name or ``uintN_t``."""
    vt = reg_dtype.register_value_type
    if _dt_name(vt) == _DT_STRUCT:
        return c_struct_name(vt)
    return f"uint{_prim_bits(_reg_value_bits(reg_dtype))}_t"


def accessor_base(prefix: str, segs: List[str], reg: str) -> str:
    """The shared accessor name stem: ``<prefix>_<seg>_..._<reg>``.

    The body emitter (lower_progseq) reconstructs the same name from a register
    access expression, so the two stay in lock-step without a shared registry.
    """
    return "_".join([prefix] + segs + [reg])


# --- value unions ----------------------------------------------------------

def emit_value_union(struct_dtype, reg_style: str = "bitfields") -> str:
    name = c_struct_name(struct_dtype)
    total = _struct_total_bits(struct_dtype)
    prim = _prim_bits(total)
    ut = f"uint{prim}_t"
    if reg_style == "accessors":
        return _emit_accessor_struct(struct_dtype, name, ut)
    lines = [f"typedef union {{ {ut} raw; struct {{"]
    bit = 0
    for f in struct_dtype.fields:
        w = int(f.datatype.bits)
        lines.append(f"    {ut} {f.name:12} : {w:2};   /* [{bit + w - 1}:{bit}] */")
        bit += w
    lines.append(f"}}; }} {name};")
    return "\n".join(lines)


def _emit_accessor_struct(struct_dtype, name: str, ut: str) -> str:
    """Layout-independent fallback (--reg-style accessors): a plain raw word plus
    inline shift/mask helpers ``<name>_<FIELD>_get/_set``."""
    lines = [f"typedef struct {{ {ut} raw; }} {name};"]
    bit = 0
    for f in struct_dtype.fields:
        w = int(f.datatype.bits)
        if not _is_reserved(f):
            mask = (1 << w) - 1
            lines.append(
                f"static inline {ut} {name}_{f.name}_get({name} v) "
                f"{{ return ({ut})((v.raw >> {bit}) & 0x{mask:x}u); }}")
            lines.append(
                f"static inline void {name}_{f.name}_set({name} *v, {ut} x) "
                f"{{ v->raw = (v->raw & ~(0x{mask:x}u << {bit})) | "
                f"(({ut})(x & 0x{mask:x}u) << {bit}); }}")
        bit += w
    return "\n".join(lines)


def lower_value_unions(root_dtype, reg_style: str = "bitfields") -> str:
    groups = collect_reg_groups(root_dtype)
    structs = collect_value_structs(groups)
    parts = ["/* ----- Register value layouts. ----- */"]
    for s in structs:
        parts.append(emit_value_union(s, reg_style))
    return "\n".join(parts)


# --- baked accessors -------------------------------------------------------

@dc.dataclass
class _Acc:
    base: str            # accessor name stem
    c_type: str          # value type
    prim: int            # transaction width 8/16/32/64
    is_struct: bool
    access: str          # READWRITE / READONLY / WRITEONLY
    const_off: int
    strides: List[int]   # one per array index parameter


def _collect_accessors(root_dtype, prefix: str) -> List[_Acc]:
    accs: List[_Acc] = []

    def visit(group_dt, segs: List[str], const_off: int, strides: List[int]):
        for f in group_dt.fields:
            if _is_reserved(f):
                continue
            if field_is_register(f):
                off = const_off + _scalar_offset(group_dt, f.name)
                accs.append(_mk_acc(prefix, segs, f.name, f.datatype, off, strides))
            elif field_is_reg_group(f):
                off = const_off + _scalar_offset(group_dt, f.name)
                visit(f.datatype, segs + [f.name], off, strides)
            elif field_is_array(f):
                elem = array_element_type(f)
                base, stride = _array_base_stride(group_dt, f.name)
                if _dt_name(elem) == _DT_REGISTER:
                    accs.append(_mk_acc(prefix, segs, f.name, elem,
                                        const_off + base, strides + [stride]))
                elif _dt_name(elem) == _DT_REGISTER_GROUP:
                    visit(elem, segs + [f.name], const_off + base, strides + [stride])

    for f in getattr(root_dtype, "fields", []) or []:
        if field_is_reg_group(f):
            visit(f.datatype, [f.name], 0, [])
        elif field_is_array(f) and _dt_name(array_element_type(f)) == _DT_REGISTER_GROUP:
            base, stride = _array_base_stride(root_dtype, f.name)
            visit(array_element_type(f), [f.name], base, [stride])
    return accs


def _mk_acc(prefix, segs, reg_name, reg_dtype, const_off, strides) -> _Acc:
    return _Acc(
        base=accessor_base(prefix, segs, reg_name),
        c_type=_reg_c_type(reg_dtype),
        prim=_prim_bits(_reg_value_bits(reg_dtype)),
        is_struct=_reg_is_struct(reg_dtype),
        access=getattr(reg_dtype, "access_mode", "READWRITE") or "READWRITE",
        const_off=const_off,
        strides=list(strides),
    )


def _idx_params(n: int, leading_comma: bool) -> str:
    if n == 0:
        return ""
    s = ", ".join(f"int i{k}" for k in range(n))
    return (", " + s) if leading_comma else s


def _idx_args(n: int) -> str:
    return "".join(f", i{k}" for k in range(n))


def _addr_expr(acc: _Acc) -> str:
    terms = [f"s->base + 0x{acc.const_off:x}u"]
    for k, stride in enumerate(acc.strides):
        terms.append(f"(pssc_addr_t)i{k} * 0x{stride:x}u")
    return " + ".join(terms)


def emit_accessor(acc: _Acc, prefix_t: str) -> str:
    n = len(acc.strides)
    idx_p = _idx_params(n, leading_comma=True)
    idx_a = _idx_args(n)
    lines = [
        f"static inline pssc_addr_t {acc.base}_addr(const {prefix_t} *s{idx_p}) "
        f"{{ return {_addr_expr(acc)}; }}",
    ]
    if acc.access != "WRITEONLY":
        if acc.is_struct:
            lines.append(
                f"static inline {acc.c_type} {acc.base}_read({prefix_t} *s{idx_p}) "
                f"{{ {acc.c_type} v; v.raw = pssc_r{acc.prim}(pssc_bus(s), "
                f"{acc.base}_addr(s{idx_a})); return v; }}")
        else:
            lines.append(
                f"static inline {acc.c_type} {acc.base}_read({prefix_t} *s{idx_p}) "
                f"{{ return pssc_r{acc.prim}(pssc_bus(s), {acc.base}_addr(s{idx_a})); }}")
    if acc.access != "READONLY":
        raw = "v.raw" if acc.is_struct else "v"
        lines.append(
            f"static inline void {acc.base}_write({prefix_t} *s{idx_p}, {acc.c_type} v) "
            f"{{ pssc_w{acc.prim}(pssc_bus(s), {acc.base}_addr(s{idx_a}), {raw}); }}")
    return "\n".join(lines)


def lower_accessors(root_dtype, prefix: str, *, link_style: str = "vtable") -> str:
    accs = _collect_accessors(root_dtype, prefix)
    prefix_t = f"{prefix}_t"
    parts = ["/* ----- Baked inline register accessors. ----- */"]
    for a in accs:
        parts.append(emit_accessor(a, prefix_t))
    return "\n".join(parts)
