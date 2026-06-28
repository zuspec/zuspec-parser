"""Tests for native covergroup parsing -> IR (no text scanner / annotations).

``covergroup { coverpoint ...; cross ...; } name;`` is parsed by pssparser into
a ``Covergroup`` AST node (with ``CovergroupCoverpoint`` / ``CovergroupCross``
children) and lowered by ast2ir into ``PssCoverGroup``. There is no longer a
``_remove_covergroup_blocks`` text strip or a PssAnnotation side-channel.
"""
import pytest
from pssc import Parser, AstToIrTranslator, load_pss

pytestmark = pytest.mark.filterwarnings("ignore::UserWarning")


def _action_ir(pss: str, qual: str, short: str):
    parser = Parser()
    parser.parses([("t.pss", pss)])
    root = parser.link()
    ctx = AstToIrTranslator().translate(root)
    return parser, ctx, (ctx.type_map.get(qual) or ctx.type_map.get(short))


CG_PSS = """
component pss_top {
    action draw_shape {
        rand bit[2] color;
        rand bit[2] shape;
        covergroup {
            coverpoint color;
            coverpoint shape;
            cross_color : cross color, shape;
        } cXs_cg;
    }
}
"""


def test_covergroup_not_an_annotation():
    """covergroup is parsed natively; there is no annotation side-channel."""
    parser = Parser()
    parser.parses([("t.pss", CG_PSS)])
    assert not hasattr(parser, "annotations")


def test_covergroup_lowers_to_ir():
    """The covergroup reaches the action IR with correct name/coverpoints/cross."""
    _p, _ctx, action_ir = _action_ir(CG_PSS, "pss_top::draw_shape", "draw_shape")
    assert action_ir is not None
    assert len(action_ir.covergroups) == 1
    cg = action_ir.covergroups[0]
    assert cg.instance_name == "cXs_cg"
    cp_names = sorted(cp.name for cp in cg.coverpoints)
    assert cp_names == ["color", "shape"]
    assert len(cg.crosses) == 1
    cx = cg.crosses[0]
    assert cx.name == "cross_color"
    assert set(cx.coverpoint_names) == {"color", "shape"}


def test_covergroup_labeled_coverpoint():
    """A labeled coverpoint uses its label as the coverpoint name."""
    pss = """
    component pss_top {
        action a {
            rand bit[2] x;
            covergroup { cp_x : coverpoint x; } cg;
        }
    }
    """
    _p, _ctx, action_ir = _action_ir(pss, "pss_top::a", "a")
    assert action_ir is not None and len(action_ir.covergroups) == 1
    assert [cp.name for cp in action_ir.covergroups[0].coverpoints] == ["cp_x"]


def test_covergroup_parse_succeeds_with_cross():
    """End-to-end load_pss with a covergroup+cross parses + builds a class."""
    ns = load_pss(CG_PSS)
    assert any("draw_shape" in k for k in ns.keys())
