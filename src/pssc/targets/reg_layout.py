"""Where every register sits, with the address arithmetic already folded.

`progseq_model` answers one question at a time ("what is this instance's
offset?"). This is the walk that asks all of them: it descends a component's
register subtree and returns one :class:`RegAccessor` per reachable register,
carrying the constant byte offset from the component's base and one stride per
array index between the component and the register.

It was `c/lower_reg_model._collect_accessors`, and it is here because it is the
first thing a SECOND backend needs and the last thing it should write for
itself. Nothing in the walk is C: it reads the PSS tree and does arithmetic.
What is C -- the accessor's spelling, its value type, whether it is emitted as
an inline function or a macro -- stays in the C backend, which builds its own
`_Acc` from these.

An address is the one thing in a generated programming API that a golden
snapshot cannot check (see `conformance.py`): a wrong offset frozen into a
snapshot stays green forever. Two backends computing offsets two ways is
therefore the worst kind of duplication available here, and this is the answer
to it.

Design: docs/generator-style-extensions-design.md; plan P8.T1.
"""
from __future__ import annotations

import dataclasses as dc
from typing import Any, List, Optional, Tuple

from .progseq_model import (_dt_name, array_element_type, array_base_stride,
                            field_is_array, field_is_reg_group,
                            field_is_register, scalar_offset)

__all__ = ["RegAccessor", "collect_accessors", "is_reserved", "prim_bits",
           "value_bits", "value_struct"]

_DT_REGISTER = "DataTypeRegister"
_DT_REGISTER_GROUP = "DataTypeRegisterGroup"
_DT_STRUCT = "DataTypeStruct"


def is_reserved(field) -> bool:
    """Is *field* a reserved placeholder -- a leading underscore?

    Reserved gaps hold the address space open and are never surfaced in a
    generated API. Their space is already accounted for in the following
    siblings' offsets, so skipping them changes no address.
    """
    return getattr(field, "name", "").startswith("_")


def prim_bits(bits: int) -> int:
    """The bus transaction width a register of *bits* is accessed at."""
    for w in (8, 16, 32, 64):
        if bits <= w:
            return w
    return 64


def value_struct(reg_dtype) -> Optional[Any]:
    """The register's value STRUCT, or ``None`` if its value is a plain scalar."""
    vt = getattr(reg_dtype, "register_value_type", None)
    return vt if _dt_name(vt) == _DT_STRUCT else None


def value_bits(reg_dtype) -> int:
    """How many bits the register's value occupies.

    `size_bits` when the model states one -- `reg_c<dma_csr_s, READWRITE, 32>`
    says 32 and means it, even where the fields sum to less.
    """
    sb = getattr(reg_dtype, "size_bits", None)
    if sb:
        return int(sb)
    vs = value_struct(reg_dtype)
    if vs is not None:
        return sum(int(f.datatype.bits) for f in vs.fields)
    vt = getattr(reg_dtype, "register_value_type", None)
    return int(getattr(vt, "bits", 32) or 32)


@dc.dataclass(frozen=True)
class RegAccessor:
    """One reachable register, with its address arithmetic folded.

    The address is ``base + const_off + sum(index[k] * strides[k])``: everything
    a generation can know is a constant here, and the only runtime terms are the
    component's base and the array indices, in the order the path crosses them.
    """

    #: Group / array field names between the component and the register.
    segs: Tuple[str, ...]
    #: The register instance's own name.
    name: str
    #: The `DataTypeRegister`, for anything a backend needs that is not here.
    dtype: Any
    #: Its value struct, or ``None`` for a scalar-valued register.
    value_struct: Optional[Any]
    #: Value width in bits, and the transaction width it rounds up to.
    value_bits: int
    prim_bits: int
    #: ``READWRITE`` / ``READONLY`` / ``WRITEONLY``.
    access: str
    #: Constant byte offset from the component's base.
    const_off: int
    #: One stride per array index crossed, outermost first.
    strides: Tuple[int, ...]

    @property
    def is_struct(self) -> bool:
        return self.value_struct is not None

    @property
    def readable(self) -> bool:
        return self.access != "WRITEONLY"

    @property
    def writable(self) -> bool:
        return self.access != "READONLY"

    @property
    def path(self) -> Tuple[str, ...]:
        """The full instance path, register included. `("regs", "channels", "CSR")`."""
        return tuple(self.segs) + (self.name,)


def collect_accessors(comp_dtype) -> List[RegAccessor]:
    """Every register reachable from *comp_dtype*, in declaration order.

    Depth-first at the point of the field, so a nested group's registers appear
    where the group is declared rather than after all of the outer group's --
    which is the order the C backend has emitted accessors in since it had them,
    and the order a reader of the PSS source expects.

    An array of GROUPS contributes a stride and keeps descending; an array of
    REGISTERS is one accessor with a stride. Both cases exist in the worked
    example (`channels[31]` is the first, and models with `reg_c ... [n]` are
    the second).
    """
    accs: List[RegAccessor] = []

    def visit(group_dt, segs: List[str], const_off: int, strides: List[int]):
        for f in group_dt.fields:
            if is_reserved(f):
                continue
            if field_is_register(f):
                accs.append(_mk(segs, f.name, f.datatype,
                                const_off + scalar_offset(group_dt, f.name),
                                strides))
            elif field_is_reg_group(f):
                visit(f.datatype, segs + [f.name],
                      const_off + scalar_offset(group_dt, f.name), strides)
            elif field_is_array(f):
                elem = array_element_type(f)
                base, stride = array_base_stride(group_dt, f.name)
                if _dt_name(elem) == _DT_REGISTER:
                    accs.append(_mk(segs, f.name, elem, const_off + base,
                                    strides + [stride]))
                elif _dt_name(elem) == _DT_REGISTER_GROUP:
                    visit(elem, segs + [f.name], const_off + base,
                          strides + [stride])

    for f in getattr(comp_dtype, "fields", []) or []:
        if field_is_reg_group(f):
            visit(f.datatype, [f.name], 0, [])
        elif (field_is_array(f)
                and _dt_name(array_element_type(f)) == _DT_REGISTER_GROUP):
            base, stride = array_base_stride(comp_dtype, f.name)
            visit(array_element_type(f), [f.name], base, [stride])
    return accs


def _mk(segs, name, reg_dtype, const_off, strides) -> RegAccessor:
    return RegAccessor(
        segs=tuple(segs),
        name=name,
        dtype=reg_dtype,
        value_struct=value_struct(reg_dtype),
        value_bits=value_bits(reg_dtype),
        prim_bits=prim_bits(value_bits(reg_dtype)),
        access=getattr(reg_dtype, "access_mode", "READWRITE") or "READWRITE",
        const_off=const_off,
        strides=tuple(strides),
    )
