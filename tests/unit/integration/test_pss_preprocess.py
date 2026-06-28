"""Tests for the native built-in state/resource fields.

The LRM built-in fields ``initial`` (state) and ``instance_id`` (resource) are
injected natively by pssparser (``AstBuilderInt::addStructBuiltinField``); there
is no source pre-processing. These tests assert the fields reach the IR and that
the constraint references link.
"""
from __future__ import annotations
import os
import tempfile
import pytest

from pssc import Parser, AstToIrTranslator

pytestmark = pytest.mark.filterwarnings("ignore::UserWarning")


def _translate(pss_src: str):
    """Parse + link + translate a PSS snippet, returning the IR context."""
    with tempfile.NamedTemporaryFile(suffix='.pss', mode='w', delete=False) as f:
        f.write(pss_src)
        fname = f.name
    try:
        p = Parser()
        p.parse([fname])
        root = p.link()
        return AstToIrTranslator().translate(root)
    finally:
        try:
            os.unlink(fname)
        except OSError:
            pass


def _field_names(type_ir):
    return [fld.name for fld in type_ir.fields]


# ------------------------------------------------------------------
# Native built-in injection (no source rewriting)
# ------------------------------------------------------------------

def test_state_gets_initial_field():
    ctx = _translate("component pss_top { state s { rand bit[8] x; } }")
    assert "initial" in _field_names(ctx.type_map["s"])


def test_resource_gets_instance_id_field():
    ctx = _translate("component pss_top { resource r { rand bit[4] mode; } }")
    assert "instance_id" in _field_names(ctx.type_map["r"])


def test_no_double_injection_initial():
    ctx = _translate(
        "component pss_top { state s { rand bool initial; rand int x; } }")
    assert _field_names(ctx.type_map["s"]).count("initial") == 1


def test_no_double_injection_instance_id():
    ctx = _translate(
        "component pss_top { resource r { int instance_id; rand bit[4] cfg; } }")
    assert _field_names(ctx.type_map["r"]).count("instance_id") == 1


def test_no_injection_into_struct():
    ctx = _translate("component pss_top { struct s { rand int y; } }")
    names = _field_names(ctx.type_map["s"])
    assert "initial" not in names
    assert "instance_id" not in names


# ------------------------------------------------------------------
# Full parse + link + IR for constraint references
# ------------------------------------------------------------------

def test_state_constraint_initial_parseable():
    """`constraint initial -> val == 0;` links and reaches the IR."""
    ctx = _translate("""\
state power_s {
    rand bit[8] val;
    constraint initial -> val == 0;
}
component pss_top {
    pool power_s p;
    bind p *;
    action step { input power_s a; output power_s b; }
}
""")
    st_ir = ctx.type_map.get("power_s")
    assert st_ir is not None
    assert "initial" in _field_names(st_ir)
    assert st_ir.has_initial_constraint


def test_resource_constraint_instance_id_parseable():
    """`constraint instance_id < 2;` links and reaches the IR."""
    ctx = _translate("""\
resource ch_r {
    constraint instance_id < 2;
}
component pss_top {
    pool ch_r ch;
    bind ch *;
    action xfer { lock ch_r c; }
}
""")
    ch_ir = ctx.type_map.get("ch_r")
    assert ch_ir is not None
    assert "instance_id" in _field_names(ch_ir)
