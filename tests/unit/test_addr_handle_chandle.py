"""`addr_handle_t` reaches the IR as a chandle, and every projection maps it.

`addr_reg_pkg` spells the address handle `typedef chandle addr_handle_t`. A
typedef leaves no name behind in the IR, so an argument declared
`addr_handle_t head` arrives as a bare `DataTypeChandle` -- the projections
cannot recognize it by name.

Before this was handled, every programming-sequence target raised
`unsupported <lang> type for DataTypeChandle` on any operation taking an
address, which is most of them. The stdlib previously used a placeholder
`struct addr_handle_t`, so the name-based path is still exercised too; both
spellings must land on the same handle type.
"""
import pytest

from pssc.targets.sv.lower_progseq import sv_type
from pssc.targets.c.lower_progseq import c_type
from pssc.targets.cpp.lower_progseq import cpp_type


# The projections dispatch on `type(dt).__name__`, so the stand-ins must carry
# the IR class names rather than merely quack like the IR nodes.
Chandle = type("DataTypeChandle", (), {"name": None})
Struct = type("DataTypeStruct", (), {})


def _chandle():
    return Chandle()


def _addr_struct():
    """The pre-2026-08 placeholder spelling: a named, field-less struct."""
    dt = Struct()
    dt.name = "addr_reg_pkg::addr_handle_t"
    dt.fields = []
    return dt


@pytest.mark.parametrize("fn,expected", [
    (sv_type, "addr_handle_t"),
    (c_type, "pssc_addr_t"),
    (cpp_type, "pssc::addr_t"),
], ids=["sv", "c", "cpp"])
def test_chandle_maps_to_the_address_handle(fn, expected):
    assert fn(_chandle()) == expected


@pytest.mark.parametrize("fn", [sv_type, c_type, cpp_type], ids=["sv", "c", "cpp"])
def test_both_spellings_agree(fn):
    """A stdlib that declares the handle either way generates the same API."""
    assert fn(_chandle()) == fn(_addr_struct())
