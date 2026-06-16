"""Unit tests for analyze_flow.py and classify_constraints.py (Phase 3, T3.1, T3.2).

Tests that flow analysis extracts correct producer/consumer pairs from
activity IR, and that constraint classification correctly distinguishes
SV_NATIVE / FLOW_PROP / DPI_REQUIRED.
"""
from __future__ import annotations

import pytest
from zuspec.dataclasses import ir
from zuspec.ir.core.fields import FieldKind
from zuspec.ir.core import expr as ir_expr

from pssc.targets.sv.context import LoweringContext
from pssc.targets.sv.analyze_flow import (
    analyze_flow,
    ActivityFlowInfo,
    FlowBindingInfo,
    _expr_attr_chain,
)
from pssc.targets.sv.classify_constraints import (
    classify_constraint,
    ConstraintClass,
    classify_action_constraints,
    determine_solve_mode,
    SolveMode,
    _collect_top_field_refs,
)


# ------------------------------------------------------------------ #
# Helpers                                                              #
# ------------------------------------------------------------------ #

def _self_attr(field: str) -> ir_expr.ExprAttribute:
    return ir_expr.ExprAttribute(value=ir_expr.TypeExprRefSelf(), attr=field)


def _self_subattr(field: str, sub: str) -> ir_expr.ExprAttribute:
    return ir_expr.ExprAttribute(
        value=ir_expr.ExprAttribute(value=ir_expr.TypeExprRefSelf(), attr=field),
        attr=sub,
    )


def _bind_expr(label: str, field: str) -> ir_expr.ExprAttribute:
    """Build expr for label.field (as in ActivityBind src/dst)."""
    return ir_expr.ExprAttribute(
        value=ir_expr.ExprAttribute(value=ir_expr.TypeExprRefSelf(), attr=label),
        attr=field,
    )


def _make_activity(stmts):
    return ir.ActivitySequenceBlock(stmts=stmts, pragmas={})


def _make_anon(action_type: str, label: str = None):
    return ir.ActivityAnonTraversal(
        action_type=action_type,
        label=label,
        inline_constraints=[],
        action_type_cls=None,
        comp_expr=None,
        init_bindings=[],
    )


def _make_bind(prod_label, prod_field, cons_label, cons_field):
    return ir.ActivityBind(
        src=_bind_expr(prod_label, prod_field),
        dst=_bind_expr(cons_label, cons_field),
    )


def _make_ctx():
    return LoweringContext()


# ------------------------------------------------------------------ #
# Tests: _expr_attr_chain                                              #
# ------------------------------------------------------------------ #

def test_expr_attr_chain_two_level():
    expr = _bind_expr("p", "out_b")
    result = _expr_attr_chain(expr)
    assert result == ("p", "out_b")


def test_expr_attr_chain_single_level():
    expr = _self_attr("out_b")
    result = _expr_attr_chain(expr)
    assert result == ("", "out_b")


def test_expr_attr_chain_non_attr():
    from zuspec.ir.core.expr import ExprConstant
    result = _expr_attr_chain(ExprConstant(value=42, kind=None))
    assert result is None


# ------------------------------------------------------------------ #
# Tests: analyze_flow                                                  #
# ------------------------------------------------------------------ #

def test_analyze_flow_single_bind():
    """Simple schedule with one explicit bind."""
    ctx = _make_ctx()
    activity = _make_activity([
        ir.ActivitySchedule(stmts=[
            _make_anon("producer", label="p"),
            _make_anon("consumer", label="c"),
            _make_bind("p", "out_b", "c", "in_b"),
        ], pragmas={}, join_spec=None),
    ])
    info = analyze_flow(ctx, activity)
    assert len(info.traversals) == 2
    assert info.traversals[0].var_name == "p"
    assert info.traversals[1].var_name == "c"
    assert len(info.bindings) == 1
    b = info.bindings[0]
    assert b.producer_var == "p"
    assert b.producer_field == "out_b"
    assert b.consumer_var == "c"
    assert b.consumer_field == "in_b"


def test_analyze_flow_producer_consumer_index():
    """Producer bindings indexed by var_name."""
    ctx = _make_ctx()
    activity = _make_activity([
        ir.ActivitySchedule(stmts=[
            _make_anon("src", label="s"),
            _make_anon("dst", label="d"),
            _make_bind("s", "out_buf", "d", "in_buf"),
        ], pragmas={}, join_spec=None),
    ])
    info = analyze_flow(ctx, activity)
    assert "s" in info.producer_bindings
    assert "d" in info.consumer_bindings
    assert len(info.producer_bindings["s"]) == 1
    assert len(info.consumer_bindings["d"]) == 1


def test_analyze_flow_no_binds():
    """Activity with no binds produces empty binding list."""
    ctx = _make_ctx()
    activity = _make_activity([
        _make_anon("action_a", label="a"),
        _make_anon("action_b", label="b"),
    ])
    info = analyze_flow(ctx, activity)
    assert len(info.bindings) == 0
    assert len(info.traversals) == 2


def test_analyze_flow_multiple_binds():
    """Multiple binds detected."""
    ctx = _make_ctx()
    activity = _make_activity([
        ir.ActivitySchedule(stmts=[
            _make_anon("step1", label="a"),
            _make_anon("step2", label="b"),
            _make_anon("step3", label="c"),
            _make_bind("a", "out1", "b", "in1"),
            _make_bind("b", "out2", "c", "in2"),
        ], pragmas={}, join_spec=None),
    ])
    info = analyze_flow(ctx, activity)
    assert len(info.bindings) == 2
    assert info.bindings[0].producer_var == "a"
    assert info.bindings[1].producer_var == "b"


def test_analyze_flow_anonymous_label():
    """AnonTraversal without a label gets a generated name."""
    ctx = _make_ctx()
    activity = _make_activity([_make_anon("some_action")])
    info = analyze_flow(ctx, activity)
    assert len(info.traversals) == 1
    assert info.traversals[0].var_name.startswith("_anon_")


# ------------------------------------------------------------------ #
# Tests: _collect_top_field_refs                                       #
# ------------------------------------------------------------------ #

def test_collect_refs_simple_field():
    """self.val -> {'val'}"""
    expr = _self_attr("val")
    refs = _collect_top_field_refs(expr)
    assert refs == {"val"}


def test_collect_refs_nested_field():
    """self.in_buf.x -> {'in_buf'}"""
    expr = _self_subattr("in_buf", "x")
    refs = _collect_top_field_refs(expr)
    assert refs == {"in_buf"}


def test_collect_refs_binary_expr():
    """self.a + self.b -> {'a', 'b'}"""
    from zuspec.ir.core.expr import BinOp
    expr = ir_expr.ExprBin(
        lhs=_self_attr("a"),
        op=BinOp.Add,
        rhs=_self_attr("b"),
    )
    refs = _collect_top_field_refs(expr)
    assert "a" in refs
    assert "b" in refs


def test_collect_refs_constant():
    """ExprConstant -> {}"""
    from zuspec.ir.core.expr import ExprConstant
    refs = _collect_top_field_refs(ExprConstant(value=42, kind=None))
    assert refs == set()


# ------------------------------------------------------------------ #
# Tests: classify_constraint                                           #
# ------------------------------------------------------------------ #

def _make_eq_stmt(lhs_expr, rhs_expr):
    from zuspec.ir.core.expr import BinOp
    return ir.StmtExpr(expr=ir_expr.ExprBin(lhs=lhs_expr, op=BinOp.Eq, rhs=rhs_expr))


def _make_gt_stmt(lhs_expr, rhs_expr):
    from zuspec.ir.core.expr import BinOp
    return ir.StmtExpr(expr=ir_expr.ExprBin(lhs=lhs_expr, op=BinOp.Gt, rhs=rhs_expr))


def test_classify_no_flow_refs():
    """Constraint on local field only -> SV_NATIVE."""
    ctx = _make_ctx()
    # constraint val > 0
    body = [_make_gt_stmt(_self_attr("val"), ir_expr.ExprConstant(value=0, kind=None))]
    result = classify_constraint(ctx, "top::act", body, set(), set())
    assert result == ConstraintClass.SV_NATIVE


def test_classify_input_to_output_coupling():
    """constraint in_s.x == out_s.x -> FLOW_PROP (coupling, safe with inject)."""
    ctx = _make_ctx()
    body = [_make_eq_stmt(_self_subattr("in_s", "x"), _self_subattr("out_s", "x"))]
    result = classify_constraint(ctx, "top::act", body, {"in_s"}, {"out_s"})
    assert result == ConstraintClass.FLOW_PROP


def test_classify_input_eq_constant():
    """constraint in_s.resized == true -> DPI_REQUIRED (constrains input value)."""
    ctx = _make_ctx()
    body = [_make_eq_stmt(
        _self_subattr("in_s", "resized"),
        ir_expr.ExprConstant(value=1, kind=None)
    )]
    result = classify_constraint(ctx, "top::act", body, {"in_s"}, set())
    assert result == ConstraintClass.DPI_REQUIRED


def test_classify_input_only_ref_no_output():
    """Constraint refs only input field, no output coupling -> DPI_REQUIRED."""
    ctx = _make_ctx()
    # constraint in_b.value > 0  (no output field referenced)
    body = [_make_gt_stmt(
        _self_subattr("in_b", "value"),
        ir_expr.ExprConstant(value=0, kind=None)
    )]
    result = classify_constraint(ctx, "top::act", body, {"in_b"}, {"out_b"})
    assert result == ConstraintClass.DPI_REQUIRED


def test_classify_empty_body():
    """Empty body -> SV_NATIVE."""
    ctx = _make_ctx()
    result = classify_constraint(ctx, "top::act", [], {"in_b"}, {"out_b"})
    assert result == ConstraintClass.SV_NATIVE


# ------------------------------------------------------------------ #
# Tests: determine_solve_mode                                          #
# ------------------------------------------------------------------ #

def test_solve_mode_no_consumer_bindings():
    """No consumer bindings -> SV_NATIVE."""
    ctx = _make_ctx()
    mode = determine_solve_mode(ctx, "top::producer", has_consumer_bindings=False)
    assert mode == SolveMode.SV_NATIVE


def test_solve_mode_consumer_but_no_ir_ctx():
    """Consumer bindings but no ir_ctx -> SV_WITH_INJECT (safe default)."""
    ctx = _make_ctx()  # no ir_ctx
    mode = determine_solve_mode(ctx, "top::consumer", has_consumer_bindings=True)
    assert mode == SolveMode.SV_WITH_INJECT
