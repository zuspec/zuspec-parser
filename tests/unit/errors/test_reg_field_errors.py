"""Masked register writes that must be rejected rather than silently lowered.

Two of these are the plan of record for pssc; the rest are backstops.

The **zero-mask** case is pssc's own, because it is a statement about folded
bits rather than about a name (plan §1.2). It exists because of pssparser defect
D5: `AstBuilderInt::visitExpression` discards the operator of a unary
expression, so `~0` reaches the compiler as `0`. That turns the LRM's own mask
idiom -- Example356's `{.mode=~0}` -- into a write that selects no bits. Folding
it would emit a silent no-op; refusing it is the only safe answer while D5 is
open.

The **unreduced-call** case is the guarantee that nothing gets through: the
reduction only follows `self`-rooted paths into the enclosing component's own
register model, and anything it could not follow is reported here rather than
reaching a backend, where an unrecognised register method becomes a generic call
that compiles and is wrong.

Name-level errors -- unknown field, aggregate field, non-literal name -- are the
front end's to report, with a source location (plan phase 1, now landed). pssc
still checks them, as a backstop against a front end that let one through, but
those checks are no longer reachable from source: pssparser rejects the model
at `link()` before `translate()` runs. The cases below therefore assert the
*link* failure, which is what a pssc user actually sees.
"""
import pytest

from pssc import Parser
from pssc.ast2ir import AstToIrTranslator


_SRC = """
package p {
    import std_pkg::*;
    import addr_reg_pkg::*;
    struct inner_s : packed_s<> { rand bit[4] a; rand bit[4] b; }
    struct csr_s : packed_s<> {
        rand bit[1]  ch_en;
        rand bit[3]  prio;
        rand bit[28] rsvd;
    }
    pure component csr_r : reg_c<csr_s, READWRITE, 32> {}
    pure component wo_r  : reg_c<csr_s, WRITEONLY, 32> {}
    pure component grp_c : reg_group_c { csr_r csr; wo_r wo; }
    component top_c {
        grp_c regs;
%s
    }
}
"""


def errors_for(body: str):
    parser = Parser()
    parser.parses([("test.pss", _SRC % body)])
    return AstToIrTranslator(debug=False).translate(parser.link()).errors


def one_error(body: str) -> str:
    errs = errors_for(f"target function void f() {{ {body} }}")
    assert len(errs) == 1, f"expected exactly one error, got {errs}"
    return errs[0]


# --- the D5 zero-mask trap ------------------------------------------------

def test_the_lrm_mask_idiom_is_rejected_not_folded():
    """`{.ch_en=~0}` is the spec's own spelling and currently folds to 0."""
    msg = one_error("regs.csr.write_masked({.ch_en=~0}, {.ch_en=1});")
    assert "zero mask" in msg
    assert "'ch_en'" in msg
    assert "D5" in msg, "the message must say why ~0 vanished"
    assert "write_field" in msg, "the message must offer the form that works"


def test_explicit_zero_mask_is_rejected_too():
    """Not special-cased to `~0`: a field named in the mask that selects none of
    its bits is meaningless however it was spelled."""
    assert "zero mask" in one_error("regs.csr.write_masked({.prio=0}, {.prio=2});")


def test_a_nonzero_mask_is_accepted():
    """The guard must not reject the working form."""
    assert errors_for(
        "target function void f() { regs.csr.write_masked({.prio=7}, {.prio=2}); }"
    ) == []


# --- access mode ----------------------------------------------------------

def test_masked_write_on_a_writeonly_register():
    """§21.14.1 defines the masked forms as read-modify-write, so they need a
    read the register does not offer."""
    msg = one_error('regs.wo.write_field("ch_en", 1);')
    assert "WRITEONLY" in msg
    assert "read-modify-write" in msg


# --- the front end owns these now -----------------------------------------
#
# These were pssc diagnostics until the resolution moved into pssparser's
# `TaskResolveRefs` (plan phase 1). They are asserted here as *link* failures
# rather than deleted, because what matters to a pssc user is that the error
# arrives at all, and this is the file that says so. pssc keeps its own copies
# as unreachable backstops -- see the module docstring.

import pytest as _pytest
from pssparser import ParseException


def link_error(body: str) -> str:
    """The message from linking a model whose masked write is malformed."""
    parser = Parser()
    parser.parses([("test.pss", _SRC % f"target function void f() {{ {body} }}")])
    with _pytest.raises(ParseException) as e:
        parser.link()
    return str(e.value)


def test_unknown_field_name():
    msg = link_error('regs.csr.write_field("chan_en", 1);')
    assert "chan_en" in msg
    assert "did you mean 'ch_en'?" in msg
    assert "test.pss:" in msg, "the front end must give a source location"


def test_aggregate_field_is_rejected():
    parser = Parser()
    parser.parses([("test.pss", """
        package p {
            import std_pkg::*;
            import addr_reg_pkg::*;
            struct inner_s : packed_s<> { rand bit[4] a; rand bit[4] b; }
            struct outer_s : packed_s<> { rand bit[1] en; inner_s sub; rand bit[23] pad; }
            pure component r_c : reg_c<outer_s, READWRITE, 32> {}
            pure component grp_c : reg_group_c { r_c r; }
            component top_c {
                grp_c regs;
                target function void f() { regs.r.write_field("sub", 1); }
            }
        }
    """)])
    with _pytest.raises(ParseException) as e:
        parser.link()
    assert "composite type" in str(e.value)


def test_non_literal_field_name():
    assert "string literal" in link_error("string n; regs.csr.write_field(n, 1);")


def test_hierarchical_field_name():
    """§21.14.1(b): top-level fields only."""
    assert "hierarchical" in link_error('regs.csr.write_field("a.b", 1);')


def test_duplicate_names_in_write_fields():
    msg = link_error('regs.csr.write_fields({"prio","prio"}, {1,2});')
    assert "duplicate" in msg
    assert "'prio'" in msg


def test_names_values_length_mismatch():
    assert "2 field name(s) but 1 value(s)" in \
        link_error('regs.csr.write_fields({"ch_en","prio"}, {1});')


def test_unknown_field_in_a_write_masked_literal():
    """The struct-literal spelling is checked too -- it names fields just as
    directly, and linked clean before phase 1."""
    msg = link_error('regs.csr.write_masked({.nosuch=1}, {.nosuch=1});')
    assert "nosuch" in msg


def test_legal_shapes_still_link():
    """The regression that matters most: the checks must not reject the model.

    `src/pss` uses `write_field` at five sites; a false positive here is a
    device model that no longer compiles.
    """
    for body in ('regs.csr.write_field("ch_en", 1);',
                 'regs.csr.write_fields({"ch_en","prio"}, {1,2});',
                 'regs.csr.write_masked({.prio=7}, {.prio=2});'):
        parser = Parser()
        parser.parses([("test.pss",
                        _SRC % f"target function void f() {{ {body} }}")])
        parser.link()      # must not raise


def test_an_action_exec_body_reduces():
    """An exec body reaching registers through `comp` is ordinary PSS.

    The reduction follows `self`-rooted paths, and an action's path is rooted at
    the action while the registers belong to its component. Getting this wrong
    does not produce wrong code -- `check_reduced` turns it into a compile error
    -- but it would reject a legal model, so it is pinned.
    """
    parser = Parser()
    parser.parses([("test.pss", _SRC % """
        action A { exec body { comp.regs.csr.write_field("ch_en", 1); } }
    """)])
    ctx = AstToIrTranslator(debug=False).translate(parser.link())
    assert ctx.errors == []
    body = ctx.type_map["p::top_c::A"].functions[0].body
    assert body[0].expr.func.attr == "write_val_masked"
    assert [a.value for a in body[0].expr.args] == [1, 1]


def test_an_unreducible_call_is_an_error_not_a_pass_through():
    """A masked call the reduction could not follow must never reach a backend.

    There is deliberately no PSS source here. Every shape reachable from source
    today *does* reduce -- which is the point -- so exercising the backstop
    means handing it IR it cannot resolve. What is being pinned is the
    guarantee, not a way for a user to trip it: if a future front-end or IR
    change opens a path the reduction cannot follow, the result must be a
    compile error rather than a `write_field` call reaching a backend, where an
    unrecognised register method becomes a generic call that compiles and is
    wrong.
    """
    import zuspec.ir.core as zir
    from pssc import reg_rmw

    parser = Parser()
    parser.parses([("test.pss", _SRC % "")])
    ctx = AstToIrTranslator(debug=False).translate(parser.link())
    assert ctx.errors == []

    top = ctx.type_map["p::top_c"]
    top.functions.append(zir.Function(
        name="smuggled", args=zir.Arguments(args=[]), returns=None,
        body=[zir.StmtExpr(expr=zir.ExprCall(
            func=zir.ExprAttribute(
                value=zir.ExprAttribute(
                    value=zir.TypeExprRefSelf(), attr="nonesuch"),
                attr="write_field"),
            args=[zir.ExprConstant(value="ch_en"), zir.ExprConstant(value=1)]))]))

    reg_rmw.check_reduced(ctx)
    assert any("could not be resolved" in e for e in ctx.errors), ctx.errors
