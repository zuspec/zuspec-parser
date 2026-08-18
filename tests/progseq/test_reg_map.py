"""The register-group struct layout (`reg_layout.build_reg_map`).

The layout is a claim about ADDRESSES, and an address is the one thing a golden
snapshot cannot check -- a wrong offset frozen into a snapshot stays green
forever. So the offsets are asserted here against the register map as declared,
and the emitted C additionally carries a `_Static_assert` per member so the
claim is re-checked by the C compiler against the struct it actually built.

The gaps are the point. A folded per-register offset does not care what sits
between two registers; a struct member's position is decided by everything
declared before it, so an unmapped hole must be declared or every later
register silently moves.
"""
from __future__ import annotations

import pytest

from pssc.targets.reg_layout import (
    GROUP, PAD, REG, RegMapError, build_reg_map, reg_maps_for,
)


# -- stand-ins ---------------------------------------------------------------
#
# Hand-built rather than elaborated from PSS: this module is arithmetic over a
# declared layout, and a test that has to compile a model to state "0x14 is a
# three-word hole" cannot show the hole to a reader.

class _Reg:
    """A `DataTypeRegister` stand-in."""

    def __init__(self, bits=32, access="READWRITE"):
        self.size_bits = bits
        self.access_mode = access
        self.register_value_type = None


class _Group:
    """A `DataTypeRegisterGroup` stand-in with an explicit offset map."""

    def __init__(self, name, fields, offsets, arrays=None):
        self.name = name
        self.fields = fields
        self.offset_map = offsets
        self.array_map = arrays or {}


class _Field:
    def __init__(self, name, datatype):
        self.name = name
        self.datatype = datatype


class _Array:
    def __init__(self, element_type, size):
        self.element_type = element_type
        self.size = size


@pytest.fixture(autouse=True)
def _patch(monkeypatch):
    """Point the layout walk's predicates at the stand-ins above."""
    import pssc.targets.reg_layout as rl

    monkeypatch.setattr(rl, "field_is_register",
                        lambda f: isinstance(f.datatype, _Reg))
    monkeypatch.setattr(rl, "field_is_reg_group",
                        lambda f: isinstance(f.datatype, _Group))
    monkeypatch.setattr(rl, "field_is_array",
                        lambda f: isinstance(f.datatype, _Array))
    monkeypatch.setattr(rl, "array_element_type", lambda f: f.datatype.element_type)
    monkeypatch.setattr(rl, "scalar_offset", lambda g, n: g.offset_map[n])
    monkeypatch.setattr(rl, "array_base_stride", lambda g, n: g.array_map[n])
    monkeypatch.setattr(rl, "value_bits", lambda dt: dt.size_bits)
    monkeypatch.setattr(rl, "_dt_name",
                        lambda dt: ("DataTypeRegisterGroup"
                                    if isinstance(dt, _Group) else
                                    "DataTypeRegister" if isinstance(dt, _Reg)
                                    else "?"))


def _bank():
    return _Group(
        "ch_regs_c",
        [_Field(n, _Reg()) for n in ("csr", "sz", "adr0", "am0",
                                     "adr1", "am1", "desc", "swptr")],
        {n: i * 4 for i, n in enumerate(("csr", "sz", "adr0", "am0",
                                         "adr1", "am1", "desc", "swptr"))},
    )


def _top(bank):
    """The WB DMA shape: five registers, a three-word HOLE, then bank[4]."""
    return _Group(
        "regs_c",
        [_Field("csr", _Reg()), _Field("int_msk_a", _Reg()),
         _Field("int_msk_b", _Reg()), _Field("int_src_a", _Reg(32, "READONLY")),
         _Field("int_src_b", _Reg(32, "READONLY")),
         _Field("bank", _Array(bank, 4))],
        {"csr": 0x00, "int_msk_a": 0x04, "int_msk_b": 0x08,
         "int_src_a": 0x0c, "int_src_b": 0x10},
        {"bank": (0x20, 0x20)},
    )


# -- the layout --------------------------------------------------------------

def test_a_packed_bank_has_no_padding():
    m = build_reg_map(_bank())
    assert [x.name for x in m.members] == ["csr", "sz", "adr0", "am0",
                                           "adr1", "am1", "desc", "swptr"]
    assert m.size == 0x20
    assert all(x.kind == REG for x in m.members)


def test_an_unmapped_hole_becomes_a_named_pad():
    """0x14..0x1c is declared by nothing. Without a member there, `bank` would
    land at 0x14 and every channel register would be three words low."""
    m = build_reg_map(_top(_bank()))
    pads = [x for x in m.members if x.kind == PAD]
    assert len(pads) == 1
    assert pads[0].name == "_rsvd_14"
    assert (pads[0].offset, pads[0].total_size) == (0x14, 0xc)


def test_the_pad_is_named_for_its_offset_not_its_ordinal():
    """So inserting a register early in a map does not renumber every hole
    after it -- a diff of two generated maps has to stay readable in exactly
    the case (the map changed) where it most needs reading."""
    m = build_reg_map(_top(_bank()))
    assert [x.name for x in m.members if x.kind == PAD] == ["_rsvd_14"]


def test_the_array_lands_where_the_map_says():
    m = build_reg_map(_top(_bank()))
    bank = next(x for x in m.members if x.name == "bank")
    assert bank.kind == GROUP
    assert (bank.offset, bank.count, bank.stride) == (0x20, 4, 0x20)
    assert m.size == 0x20 + 4 * 0x20


def test_an_element_is_padded_up_to_its_stride():
    """A bank of 0x18 used with a 0x20 stride needs 8 trailing bytes, or C's
    own indexing and the device's disagree from bank 1 onward."""
    short = _Group("short_c", [_Field("a", _Reg()), _Field("b", _Reg())],
                   {"a": 0, "b": 4})
    m = build_reg_map(short, min_size=0x20)
    assert m.size == 0x20
    assert m.members[-1].kind == PAD
    assert m.members[-1].total_size == 0x20 - 0x8


# -- what a struct cannot express -------------------------------------------

def test_overlapping_instances_are_refused():
    bad = _Group("bad_c", [_Field("a", _Reg(64)), _Field("b", _Reg())],
                 {"a": 0x0, "b": 0x4})       # a spans 0x0..0x8, b sits inside
    with pytest.raises(RegMapError, match="overlaps"):
        build_reg_map(bad)


def test_a_stride_smaller_than_the_element_is_refused():
    bad = _Group("bad_c", [_Field("r", _Array(_Reg(), 4))], {},
                 {"r": (0x0, 0x2)})          # 4-byte registers, 2-byte stride
    with pytest.raises(RegMapError, match="overlap"):
        build_reg_map(bad)


def test_a_group_too_big_for_its_stride_is_refused():
    with pytest.raises(RegMapError, match="stride"):
        build_reg_map(_bank(), min_size=0x10)


# -- emission order ----------------------------------------------------------

def test_maps_come_back_innermost_first():
    """C has no forward reference for a struct used by value, so a bank's
    layout must be emitted before the map that embeds an array of it."""
    bank = _bank()
    order = reg_maps_for([_top(bank)])
    names = [m.dtype.name for m in order]
    assert names.index("ch_regs_c") < names.index("regs_c")
