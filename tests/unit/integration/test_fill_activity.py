"""Tests for the (dropped) `fill` activity construct and the coverage model.

`fill { ... }` (with its companion `FILL` placeholder) is a non-LRM,
Perspec-specific extension. It is no longer supported: the parser rejects it
with an explicit diagnostic rather than silently rewriting it (detox C1). The
`PssCoverageModel` tests below are unrelated to the `fill` syntax and remain.
"""
import pytest

from pssc import Parser, ParseException
from zuspec.dataclasses import PssCoverageModel

pytestmark = pytest.mark.filterwarnings("ignore::UserWarning")


# ---------------------------------------------------------------------------
# `fill` is rejected with a diagnostic (not silently rewritten)
# ---------------------------------------------------------------------------

def test_fill_statement_rejected_with_diagnostic():
    """A `fill { ... }` activity statement raises a clear, sourced diagnostic."""
    pss = """
    component pss_top {
        action roll_dice { rand bit[3] x; }
        action test_scenario {
            activity {
                fill {
                    do roll_dice with { x == FILL; }
                }
            }
        }
    }
    """
    parser = Parser()
    with pytest.raises(ParseException) as exc:
        parser.parses([('t.pss', pss)])
    msg = str(exc.value)
    assert "fill" in msg and "not supported" in msg
    assert "t.pss:" in msg  # carries file:line


def test_fill_as_identifier_still_parses():
    """`fill` is only reserved in statement position; it stays a valid name."""
    pss = """
    component pss_top {
        action fill { rand bit[3] x; }
        action use { activity { do fill; } }
    }
    """
    parser = Parser()
    # Must not raise: `action fill` / `do fill;` are ordinary identifier uses.
    parser.parses([('t.pss', pss)])
    parser.link()


# ---------------------------------------------------------------------------
# Unit: PssCoverageModel.all_covered()  (independent of `fill` syntax)
# ---------------------------------------------------------------------------

def test_all_covered_false_when_empty():
    model = PssCoverageModel()
    assert model.all_covered() is False


def test_all_covered_false_when_incomplete():
    model = PssCoverageModel()
    # Sample only some combinations of a 2x2 cross
    model.sample('cg', 'color', 0)
    model.sample('cg', 'shape', 0)
    model.sample_cross('cg', 'cx', (0, 0))
    model.sample('cg', 'color', 1)
    model.sample('cg', 'shape', 1)
    model.sample_cross('cg', 'cx', (1, 1))
    # Still missing (0,1) and (1,0)
    assert model.all_covered() is False


def test_all_covered_true_when_complete():
    model = PssCoverageModel()
    # 2x2 cross: values {0,1} x {0,1}
    for c in (0, 1):
        for s in (0, 1):
            model.sample('cg', 'color', c)
            model.sample('cg', 'shape', s)
            model.sample_cross('cg', 'cx', (c, s))
    assert model.all_covered() is True


def test_all_covered_specific_cross():
    model = PssCoverageModel()
    model.sample('cg', 'a', 0); model.sample('cg', 'b', 0)
    model.sample_cross('cg', 'cx', (0, 0))
    model.sample('cg', 'a', 1); model.sample('cg', 'b', 1)
    model.sample_cross('cg', 'cx', (1, 1))
    model.sample('cg', 'a', 0); model.sample('cg', 'b', 1)
    model.sample_cross('cg', 'cx', (0, 1))
    model.sample('cg', 'a', 1); model.sample('cg', 'b', 0)
    model.sample_cross('cg', 'cx', (1, 0))
    cov = model.all_covered_for_cross('cg', 'cx', ['a', 'b'])
    assert cov is True
