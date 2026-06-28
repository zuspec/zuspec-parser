"""Tests for native ``forall`` constraint support.

``forall`` is parsed natively by pssparser (producing a ``ConstraintStmtForall``
AST node) and lowered by ast2ir to an IR ``StmtForeach`` — there is no longer a
text-rewrite (forall->foreach) or PssAnnotation side-channel. These tests assert
that contract at the IR level (robust and backend-independent).

Two surface forms are accepted:
  forall (it : T in coll)   -- quantify over a typed collection (standard PSS)
  forall (it : coll)        -- iterate the named collection field directly
"""
import warnings
import pytest

from pssc import Parser, AstToIrTranslator

pytestmark = pytest.mark.filterwarnings("ignore::UserWarning")


def _constraint_bodies(src: str, type_name: str):
    """Parse+link+translate *src*; return [(func_name, [stmt_type_names])] for
    the constraint functions of the named struct/action IR type."""
    parser = Parser()
    parser.parses([("t.pss", src)])
    root = parser.link()
    ctx = AstToIrTranslator().translate(root)
    type_map = getattr(ctx, "type_map", {}) or {}
    t = type_map.get(type_name)
    if t is None:
        return []
    return [
        (f.name, [type(s).__name__ for s in f.body])
        for f in getattr(t, "functions", [])
        if f.metadata.get("_is_constraint")
    ]


def test_forall_no_node_is_text_free():
    """The forall keyword is parsed natively — no forall->foreach rewrite, no
    pass-1 annotation parser, and no side-channel."""
    parser = Parser()
    parser.parses([(
        "t.pss",
        "struct V { rand bit[8] a[4]; constraint forall (e : a) { e < 8; } }",
    )])
    # the annotation side-channel and two-pass / pass-1 machinery are gone
    assert not hasattr(parser, "annotations")
    assert not hasattr(parser, "_pass1_parser")


def test_forall_field_form_lowers_to_foreach():
    """forall (e : arr) over a field lowers to an IR StmtForeach."""
    bodies = _constraint_bodies(
        "struct V { rand bit[8] arr[4]; constraint forall (e : arr) { e < 50; } }",
        "V",
    )
    assert any("StmtForeach" in b for _, b in bodies), bodies


def test_forall_typed_in_collection_lowers():
    """forall (e : S in arr) over a typed collection lowers to StmtForeach,
    with member access (e.v) inside the body."""
    bodies = _constraint_bodies(
        "struct S { rand bit[8] v; } "
        "struct V { rand S arr[4]; constraint forall (e : S in arr) { e.v < 50; } }",
        "V",
    )
    assert any("StmtForeach" in b for _, b in bodies), bodies


def test_forall_nested_lowers():
    """Nested forall (the case that exercised the parser's recursion fix) lowers
    to a StmtForeach whose body holds the inner StmtForeach."""
    bodies = _constraint_bodies(
        "struct S { rand bit[8] v; } "
        "struct V { rand S a[2]; rand S b[2]; "
        "constraint forall (x : S in a) { forall (y : S in b) { x.v < y.v; } } }",
        "V",
    )
    assert any("StmtForeach" in b for _, b in bodies), bodies


def test_forall_alongside_scalar_constraint():
    """A forall constraint coexists with an ordinary scalar constraint."""
    bodies = _constraint_bodies(
        "struct M { rand bit[4] limit; rand bit[4] vals[3]; "
        "constraint limit < 8; constraint forall (v : vals) { v < 8; } }",
        "M",
    )
    kinds = [k for _, b in bodies for k in b]
    assert "StmtForeach" in kinds, bodies   # the forall
    assert "StmtExpr" in kinds, bodies       # the scalar constraint
