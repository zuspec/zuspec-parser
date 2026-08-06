"""Named register types must reach the IR as registers (design §3B / §4.2).

    pure component wb_dma_gcsr_r : reg_c<wb_dma_gcsr_s, READWRITE, 32> {}

is how a register gets a name it can be referred to by, and it is what the PSS
coding guidelines use. It used to translate to an ordinary, empty
`DataTypeComponent`: the super was recorded as the bare name `reg_c` and the
template arguments -- the entire content of the declaration -- were discarded.

Nothing failed. The register file simply came out empty, and each register type
came out as an *operation-bearing component*, which is why a generated package
contained `interface class wb_dma_gcsr_r_if` with no methods in it.

The parity test at the bottom is the one that would have caught this on day one.
"""
import pytest

from pssc import Parser
from pssc.ast2ir import AstToIrTranslator
from zuspec.dataclasses import ir


def translate(pss_code: str):
    parser = Parser()
    parser.parses([("test.pss", pss_code)])
    return AstToIrTranslator(debug=False).translate(parser.link())


_NAMED = """
package p {
    import std_pkg::*;
    import addr_reg_pkg::*;
    struct s_t : packed_s<> { rand bit[3] a; rand bit[29] b; }
    pure component r_c  : reg_c<s_t, READWRITE, 32> {}
    pure component ro_c : reg_c<bit[32], READONLY, 32> {}
    pure component grp_c : reg_group_c {
        r_c  x;
        ro_c y;
    }
}
"""

_INLINE = """
package p {
    import std_pkg::*;
    import addr_reg_pkg::*;
    struct s_t : packed_s<> { rand bit[3] a; rand bit[29] b; }
    pure component grp_c : reg_group_c {
        reg_c<s_t, READWRITE, 32> x;
        reg_c<bit[32], READONLY, 32> y;
    }
}
"""


def test_named_reg_becomes_DataTypeRegister():
    ctx = translate(_NAMED)
    r = ctx.type_map["p::r_c"]
    assert isinstance(r, ir.DataTypeRegister), type(r).__name__


def test_named_reg_carries_template_args():
    ctx = translate(_NAMED)
    r = ctx.type_map["p::r_c"]
    assert r.register_value_type.name.split("::")[-1] == "s_t"
    assert r.access_mode == "READWRITE"
    assert r.size_bits == 32

    ro = ctx.type_map["p::ro_c"]
    assert ro.access_mode == "READONLY", (
        "access mode lost -- a read-only register would be given a write accessor")


def test_named_reg_used_as_a_field_is_a_register():
    """The consequence that matters: a group holding named register types has
    register fields, and therefore an address map."""
    ctx = translate(_NAMED)
    grp = ctx.type_map["p::grp_c"]
    assert isinstance(grp, ir.DataTypeRegisterGroup)
    assert [type(f.datatype).__name__ for f in grp.fields] == \
        ["DataTypeRegister", "DataTypeRegister"]
    assert grp.offset_map == {"x": 0, "y": 4}


def _reg_shape(reg):
    return (type(reg).__name__,
            reg.register_value_type.name.split("::")[-1]
            if hasattr(reg.register_value_type, "name") and reg.register_value_type.name
            else type(reg.register_value_type).__name__,
            reg.access_mode,
            reg.size_bits,
            [f.name for f in reg.fields])


def test_named_and_inline_reg_agree():
    """The parity test: `pure component r : reg_c<T,A,W> {}` + `r x;` must
    produce the same register IR as an inline `reg_c<T,A,W> x;`.

    These are two spellings of one thing. They diverged completely -- one
    produced a register, the other produced an empty component -- and no test
    compared them.
    """
    named = translate(_NAMED).type_map["p::grp_c"]
    inline = translate(_INLINE).type_map["p::grp_c"]

    assert [f.name for f in named.fields] == [f.name for f in inline.fields]
    for nf, inf in zip(named.fields, inline.fields):
        assert _reg_shape(nf.datatype) == _reg_shape(inf.datatype), nf.name
    assert named.offset_map == inline.offset_map


def test_derived_reg_group_recognized():
    """A group two levels from `reg_group_c` is still a register group.

    Recognition walks the super chain through the type map rather than matching
    the immediate super's spelling, so a project base class between the two does
    not silently turn the group back into a plain component -- which would drop
    its whole address map.
    """
    ctx = translate("""
        package p {
            import std_pkg::*;
            import addr_reg_pkg::*;
            pure component base_grp_c : reg_group_c { }
            pure component grp_c : base_grp_c {
                reg_c<bit[32], READWRITE, 32> x;
            }
        }
    """)
    assert isinstance(ctx.type_map["p::grp_c"], ir.DataTypeRegisterGroup)


def test_plain_component_is_not_a_register():
    """Guard against over-eager classification: an ordinary component with an
    ordinary super stays an ordinary component."""
    ctx = translate("component b_c { } component d_c : b_c { int x; }")
    assert isinstance(ctx.type_map["d_c"], ir.DataTypeComponent)
    assert not isinstance(ctx.type_map["d_c"], ir.DataTypeRegisterGroup)
