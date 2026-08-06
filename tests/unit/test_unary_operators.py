"""Unary operators must survive to the IR (pssparser D5).

They do not. `!x` reaches pssc as `x`, and so do `-x` and `~x`: the parser's
`visitExpression` builds the operand of a unary expression and then constructs
nothing, so the operator is discarded with no diagnostic at any severity. See
`docs/pssparser-defects-2026-08-02.md`, D5.

This is the most damaging defect in the toolchain, because the output is not
wrong-looking -- it is *inverted*. Two operations in the WB DMA operation model
are guarded by `!`, and their generated SV compiles, lints clean, and does the
opposite of what the model says.

These tests are `xfail(strict=True)`: they fail the moment the parser is fixed,
which is exactly when the generated guards stop being inverted and the
operation-model plan's Phase 4 gate can be trusted again.
"""
import pytest

from pssc import Parser
from pssc.ast2ir import AstToIrTranslator
from zuspec.dataclasses import ir


def translate(pss_code: str):
    parser = Parser()
    parser.parses([("test.pss", pss_code)])
    return AstToIrTranslator(debug=False).translate(parser.link())


def _body(ctx, comp="c_c", fn="g"):
    return next(f for f in ctx.type_map[comp].functions if f.name == fn).body


_MODEL = """
component c_c {
    bit f;
    int n;
    function void g() {
        bit x;
        x = !f;
        n = -n;
        x = ~f;
    }
}
"""

_XFAIL = dict(strict=True, reason=(
    "pssparser D5: AstBuilderInt::visitExpression discards the operator of a "
    "unary expression, so !x / -x / ~x all reach the IR as x. See "
    "docs/pssparser-defects-2026-08-02.md"))


@pytest.mark.xfail(**_XFAIL)
@pytest.mark.parametrize("index,op", [(1, "Not"), (2, "USub"), (3, "Invert")])
def test_unary_operator_survives_translation(index, op):
    stmt = _body(translate(_MODEL))[index]
    assert isinstance(stmt.value, ir.ExprUnary), (
        f"expected a unary {op}; got {type(stmt.value).__name__} -- "
        f"the operator was dropped, so this statement now means its opposite")


@pytest.mark.xfail(**_XFAIL)
def test_negated_guard_is_not_the_guard():
    """The shape that actually bites: a capability guard reads back inverted.

    Asserted separately from the operator test because this is the consequence
    a reader needs to see -- `if (!caps) return;` becoming `if (caps) return;`
    is a behaviour change, not a representation detail.
    """
    ctx = translate("""
        component c_c {
            bit caps;
            function void g() { if (!caps) { return; } }
        }
    """)
    test = _body(ctx)[0].test
    assert isinstance(test, ir.ExprUnary), (
        "the guard lost its negation: the generated operation now declines to "
        "run exactly when it should run")
