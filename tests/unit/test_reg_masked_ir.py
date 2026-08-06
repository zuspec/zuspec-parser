"""Masked / field-wise register writes: declarations, masks, and bit order.

The mask constants here are spelled as literals rather than recomputed from the
layout helper under test. A test that asks the implementation what the answer is
and then checks the implementation against it pins nothing; these numbers were
derived by hand from the struct declaration.

Bit order is the thing most worth pinning. `packed_s<>` lays fields out in
declaration order, LSB-first -- the opposite of SystemVerilog. A layout computed
with one convention and a value packed with the other produces wrong register
bits with no diagnostic anywhere, so there is a case at bit 0, a case at the
MSB, and a multi-bit case in between.
"""
import pytest

from pssc import Parser
from pssc.ast2ir import AstToIrTranslator
from pssc.reg_field_resolve import field_layout, resolve_field
from zuspec.dataclasses import ir


_SRC = """
package p {
    import std_pkg::*;
    import addr_reg_pkg::*;
    struct csr_s : packed_s<> {
        rand bit[1]  ch_en;     // [0]
        rand bit[3]  prio;      // [3:1]
        rand bit[1]  use_ed;    // [4]
        rand bit[26] rsvd;      // [30:5]
        rand bit[1]  msb;       // [31]
    }
    pure component csr_r : reg_c<csr_s, READWRITE, 32> {}
    pure component raw_r : reg_c<bit[32], READWRITE, 32> {}
    pure component wo_r  : reg_c<csr_s, WRITEONLY, 32> {}
    pure component grp_c : reg_group_c { csr_r csr; raw_r raw; wo_r wo; }
    component top_c {
        grp_c regs;
%s
    }
}
"""


def translate(body: str = ""):
    parser = Parser()
    parser.parses([("test.pss", _SRC % body)])
    return AstToIrTranslator(debug=False).translate(parser.link())


def _body(ctx, name="f"):
    for fn in ctx.type_map["p::top_c"].functions:
        if fn.name == name:
            return fn.body
    raise AssertionError(f"no function {name}")


def _call(ctx, name="f", index=0):
    return _body(ctx, name)[index].expr


# --- declarations ---------------------------------------------------------

def test_all_four_methods_declared_on_a_struct_register():
    ctx = translate()
    names = {f.name for f in ctx.type_map["p::csr_r"].functions}
    assert {"write_val_masked", "write_masked",
            "write_field", "write_fields"} <= names


def test_field_wise_methods_absent_on_a_scalar_register():
    """`reg_c<bit[32]>` has nothing to name, so the field-wise forms are not
    declared -- an unknown method is a better answer than one that always
    fails. `write_val_masked` still applies: it names no field."""
    ctx = translate()
    names = {f.name for f in ctx.type_map["p::raw_r"].functions}
    assert "write_val_masked" in names
    assert not ({"write_masked", "write_field", "write_fields"} & names)


# --- layout ---------------------------------------------------------------

def test_layout_is_declaration_order_lsb_first():
    ctx = translate()
    reg = ctx.type_map["p::csr_r"]
    got = [(fs.name, fs.lsb, fs.width) for fs in field_layout(reg)]
    assert got == [
        ("ch_en", 0, 1),
        ("prio", 1, 3),
        ("use_ed", 4, 1),
        ("rsvd", 5, 26),
        ("msb", 31, 1),
    ]


@pytest.mark.parametrize("name,mask", [
    ("ch_en", 0x00000001),      # bit 0
    ("prio", 0x0000000e),       # multi-bit, shifted
    ("use_ed", 0x00000010),
    ("msb", 0x80000000),        # the MSB -- pins the direction
])
def test_field_masks(name, mask):
    ctx = translate()
    assert resolve_field(ctx.type_map["p::csr_r"], name).mask == mask


# --- reduction ------------------------------------------------------------

@pytest.mark.parametrize("call,mask,val", [
    ('regs.csr.write_field("ch_en", 1);', 0x1, 0x1),
    ('regs.csr.write_field("ch_en", 0);', 0x1, 0x0),
    ('regs.csr.write_field("prio", 5);', 0xe, 0xa),
    ('regs.csr.write_field("msb", 1);', 0x80000000, 0x80000000),
    ('regs.csr.write_masked({.prio=7}, {.prio=5});', 0xe, 0xa),
    ('regs.csr.write_fields({"ch_en","use_ed"}, {1,1});', 0x11, 0x11),
    ('regs.csr.write_fields({"msb","ch_en"}, {1,1});', 0x80000001, 0x80000001),
])
def test_reduces_to_expected_constants(call, mask, val):
    ctx = translate(f"target function void f() {{ {call} }}")
    assert ctx.errors == []
    c = _call(ctx)
    assert c.func.attr == "write_val_masked"
    assert [a.value for a in c.args] == [mask, val]


def test_value_is_truncated_to_the_field_width():
    """A value wider than the field must not bleed into its neighbours.

    `prio` is three bits; writing 0xff to it writes 0b111, not 0xff shifted.
    """
    ctx = translate('target function void f() { regs.csr.write_field("prio", 0xff); }')
    assert ctx.errors == []
    assert [a.value for a in _call(ctx).args] == [0xe, 0xe]


def test_non_constant_value_still_reduces():
    """The mask folds even when the value cannot: the field name is resolved at
    compile time regardless of what is being written into it."""
    ctx = translate(
        "target function void f(bit[1] en) { regs.csr.write_field(\"ch_en\", en); }")
    assert ctx.errors == []
    c = _call(ctx)
    assert c.func.attr == "write_val_masked"
    assert c.args[0].value == 0x1                     # mask folded
    assert not isinstance(c.args[1], ir.ExprConstant)  # value did not
