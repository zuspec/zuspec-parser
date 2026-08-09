"""Name the register fields a folded ``write_val_masked`` came from.

``reg_rmw`` reduces every field-wise and masked register write to one primitive
carrying a *constant* (mask, value) pair, and ``test_reg_ir_equivalence.py``
asserts that no field name and no field-name string ever reaches a backend.
That invariant is what stops each new backend from needing its own name table,
and it is not relaxed here: **this module puts nothing into the IR**. It reads
the constant the reduction produced and asks the register model, which the SV
target already has, which field has exactly those bits.

So the flow is one-way and lossless in the direction that matters:

    write_field("ars", enable)          -- PSS source, front end resolves 'ars'
      -> write_val_masked(64, (32'(enable) & 1) << 6)     -- IR, no names
        -> csr.write_field(WB_DMA_CH_CSR_ars, 32'(enable))  -- SV, names restored

The C target sees the middle line unchanged, which is why it needs no changes
for any of this.

Two things can fail, and both fall back to emitting the folded literals rather
than guessing:

* the receiver is not a path this module can walk to a register;
* the value expression is not the shape ``_place()`` produces, so the shifted
  value cannot be turned back into the unshifted one the wrapper wants.
"""
from __future__ import annotations

import dataclasses as dc
from typing import Dict, List, Optional, Tuple

from ...reg_field_resolve import FieldSlice, field_layout, value_struct
from ..progseq_model import _dt_name

_DT_REGISTER = "DataTypeRegister"


def _strip_pkg(name: Optional[str]) -> str:
    return name.split("::")[-1] if name else name


def const_prefix(struct_name: str) -> str:
    """``wb_dma_ch_csr_s`` -> ``WB_DMA_CH_CSR``.

    Keyed on the VALUE STRUCT's type name, not the register instance name.
    `csr` is ambiguous in a typical model -- a channel bank and a global bank
    both have one -- whereas struct typedef names are already unique within the
    generated package, so this is collision-free by construction rather than by
    luck.
    """
    n = _strip_pkg(struct_name) or "REG"
    if n.endswith("_s"):
        n = n[:-2]
    return n.upper()


def const_name(struct_name: str, field: str) -> str:
    """The localparam naming one field: ``WB_DMA_CH_CSR_ars``.

    The field keeps its source spelling rather than being upper-cased, so the
    identifier round-trips: grepping `ars` finds the PSS declaration, the packed
    struct member and this constant. Upper-casing would be a lossy transform a
    reader has to reverse by hand.
    """
    return f"{const_prefix(struct_name)}_{field}"


# --- value un-placing -------------------------------------------------------

def unplace(value, fs: FieldSlice):
    """Undo ``reg_rmw._place()``: the value as the caller wrote it, or ``None``.

    ``_place`` is the sole producer of these expressions and its shape is known
    exactly: ``(v & ((1<<width)-1)) << lsb``, with the shift dropped when the
    field is at bit 0 and the whole thing folded to a literal when ``v`` is
    constant. Anything else returns ``None`` and the caller emits the folded
    form -- a wrong guess here would write the wrong register bits with no
    diagnostic anywhere, so the match is exact or it is refused.
    """
    import zuspec.ir.core as ir

    c = _const_int(value)
    if c is not None:
        # A constant folded all the way to a literal at its final position. It
        # has to lie inside the field, or this is not the value that mask was
        # placed for.
        if c & ~fs.mask:
            return None
        return ir.ExprConstant(value=(c & fs.mask) >> fs.lsb)

    # Non-constant: `_and_lit` never folds, so the width AND is always present.
    e = value
    if fs.lsb:
        if not _is_bin(e, "LShift") or _const_int(e.rhs) != fs.lsb:
            return None
        e = e.lhs
    if not _is_bin(e, "BitAnd") or _const_int(e.rhs) != (1 << fs.width) - 1:
        return None
    return e.lhs


def _is_bin(e, op_name: str) -> bool:
    return _dt_name(e) == "ExprBin" and getattr(e.op, "name", None) == op_name


def _const_int(e) -> Optional[int]:
    if _dt_name(e) != "ExprConstant":
        return None
    v = e.value
    if isinstance(v, bool):
        return int(v)
    return v if isinstance(v, int) else None


# --- the namer --------------------------------------------------------------

@dc.dataclass
class FieldRef:
    """One field of one register, with the constant that names it."""
    slice: FieldSlice
    const: str


class FieldNamer:
    """Answers "which field(s) is this mask, on this receiver?" for one component.

    Constructed per component because receiver paths are resolved against that
    component's fields. ``type_map`` resolves ``DataTypeRef`` value types, which
    is how a register declared in one package and used in another is reached.
    """

    def __init__(self, comp, type_map: Optional[Dict[str, object]] = None):
        self._comp = comp
        self._type_map = type_map or {}
        self._layout_cache: Dict[int, Optional[Tuple[str, List[FieldSlice]]]] = {}

    def _resolve_name(self, name):
        return self._type_map.get(name)

    # -- receiver -> register --------------------------------------------

    def _steps(self, e) -> Optional[List[Optional[str]]]:
        """Flatten a ``self``-rooted receiver to attribute names.

        ``None`` marks a subscript, whose index is irrelevant: every element of
        a register array has the same value type, which is the only thing being
        looked up.
        """
        out: List[Optional[str]] = []
        while True:
            cn = _dt_name(e)
            if cn == "TypeExprRefSelf":
                out.reverse()
                return out
            if cn == "ExprAttribute":
                out.append(e.attr)
                e = e.value
                continue
            if cn == "ExprSubscript":
                out.append(None)
                e = e.value
                continue
            return None

    def _register(self, recv):
        """The ``DataTypeRegister`` a receiver expression denotes, or ``None``."""
        steps = self._steps(recv)
        if not steps:
            return None
        dtype = self._comp
        for step in steps:
            if step is None:
                dtype = _element_of(dtype)
            else:
                dtype = _field_type(dtype, step, self._resolve_name)
            if dtype is None:
                return None
        return dtype if _dt_name(dtype) == _DT_REGISTER else None

    def _layout(self, reg) -> Optional[Tuple[str, List[FieldSlice]]]:
        key = id(reg)
        if key in self._layout_cache:
            return self._layout_cache[key]
        vs = value_struct(reg, self._resolve_name)
        out = None
        if vs is not None:
            slices = [fs for fs in field_layout(reg, self._resolve_name) if fs.width]
            if slices:
                out = (_strip_pkg(vs.name), slices)
        self._layout_cache[key] = out
        return out

    # -- public ------------------------------------------------------------

    def size_bits(self, recv) -> Optional[int]:
        reg = self._register(recv)
        if reg is None:
            return None
        from ...reg_field_resolve import reg_size_bits
        return reg_size_bits(reg)

    def fields_for(self, recv, mask: int) -> Optional[List[FieldRef]]:
        """The declared fields whose bits are exactly ``mask``, or ``None``.

        Exact set equality, not "covers": a mask that spans part of a field is
        not that field, and naming it as though it were would be a lie in
        generated code. Fields are returned LSB-first, which makes the emitted
        list order stable across runs regardless of how the mask was written.
        """
        reg = self._register(recv)
        if reg is None:
            return None
        layout = self._layout(reg)
        if layout is None:
            return None
        struct_name, slices = layout
        hits, acc = [], 0
        for fs in slices:
            if mask & fs.mask:
                if mask & fs.mask != fs.mask:
                    return None       # partial overlap: not this field
                hits.append(FieldRef(slice=fs, const=const_name(struct_name, fs.name)))
                acc |= fs.mask
        if not hits or acc != mask:
            return None               # mask has bits belonging to no field
        return hits


def _field_type(dtype, name: str, resolve_name):
    for f in getattr(dtype, "fields", []) or []:
        if f.name == name:
            ft = f.datatype
            if _dt_name(ft) == "DataTypeRef":
                ft = resolve_name(getattr(ft, "ref_name", None)) or ft
            return ft
    return None


def _element_of(dtype):
    for attr in ("element_type", "elem_type"):
        et = getattr(dtype, attr, None)
        if et is not None:
            return et
    return None
