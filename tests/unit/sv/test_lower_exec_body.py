"""Unit tests for exec block body lowering into SV task bodies (Phase 2, T2.6/2.7).

Tests that lower_actions.py correctly wires exec block IR statements
into SVTaskDecl / SVFunctionDecl body_lines, including PSS built-in
function translation.
"""
from __future__ import annotations

import pytest
from zuspec.dataclasses import ir
from pssc.targets.sv.context import LoweringContext
from pssc.targets.sv.lower_actions import lower_action
from pssc.targets.sv.lower_stmts import lower_stmt, _lower_pss_call
from pssc.targets.sv.lower_exprs import lower_expr


def _make_ctx():
    return LoweringContext()


def _make_simple_action(body_stmts=None, pre_solve_stmts=None):
    """Build a minimal DataTypeClass IR for an action."""
    functions = []
    if body_stmts is not None:
        functions.append(ir.Function(
            name="body",
            args=None,
            body=body_stmts,
            returns=None,
            is_async=False,
            metadata={},
        ))
    if pre_solve_stmts is not None:
        functions.append(ir.Function(
            name="pre_solve",
            args=None,
            body=pre_solve_stmts,
            returns=None,
            is_async=False,
            metadata={},
        ))
    return ir.DataTypeClass(
        name="top_c::test_action",
        super=None,
        py_type=None,
        fields=[],
        functions=functions,
        is_abstract=False,
        flow_kind=None,
        has_initial_constraint=False,
        covergroups=[],
        activity_ir=None,
    )


# ------------------------------------------------------------------ #
# PSS built-in call mapping                                           #
# ------------------------------------------------------------------ #

def test_message_lowered_to_display():
    """message(HIGH, "hello") -> $display("hello");"""
    ctx = _make_ctx()
    # Simulate message(HIGH=3, "hello") call
    args = [
        ir.ExprConstant(value=3, kind=None),   # HIGH
        ir.ExprConstant(value="hello", kind=None),
    ]
    result = _lower_pss_call(ctx, "message", args)
    assert result == '$display("hello")', f"Unexpected: {result!r}"


def test_message_with_format_args():
    """message(LOW, "val=%d", val) -> $display("val=%d", val);"""
    ctx = _make_ctx()
    args = [
        ir.ExprConstant(value=1, kind=None),   # LOW
        ir.ExprConstant(value="val=%d", kind=None),
        ir.ExprAttribute(value=ir.TypeExprRefSelf(), attr="val"),
    ]
    result = _lower_pss_call(ctx, "message", args)
    assert "val=%d" in result
    assert "val" in result
    assert result.startswith("$display(")


def test_yield_lowered_to_comment():
    """yield() -> // yield (no-op);"""
    ctx = _make_ctx()
    result = _lower_pss_call(ctx, "yield", [])
    assert result is not None
    assert "yield" in result.lower()


def test_unknown_builtin_returns_none():
    """Unknown PSS built-in returns None (falls back to generic lowering)."""
    ctx = _make_ctx()
    result = _lower_pss_call(ctx, "unknown_fn", [])
    assert result is None


# ------------------------------------------------------------------ #
# StmtExpr with ExprCall built-in                                     #
# ------------------------------------------------------------------ #

def test_stmt_expr_message_call():
    """StmtExpr(ExprCall(message, ...)) lowers to $display(...);"""
    ctx = _make_ctx()
    stmt = ir.StmtExpr(expr=ir.ExprCall(
        func=ir.ExprAttribute(value=ir.TypeExprRefSelf(), attr="message"),
        args=[
            ir.ExprConstant(value=3, kind=None),  # HIGH
            ir.ExprConstant(value="Test %d", kind=None),
            ir.ExprAttribute(value=ir.TypeExprRefSelf(), attr="x"),
        ],
        keywords=[],
    ))
    lines = lower_stmt(ctx, stmt)
    assert len(lines) == 1
    assert lines[0].startswith("$display(")
    assert "Test %d" in lines[0]
    assert lines[0].endswith(";")


def test_stmt_expr_yield_call():
    """StmtExpr(ExprCall(yield)) lowers to a comment statement."""
    ctx = _make_ctx()
    stmt = ir.StmtExpr(expr=ir.ExprCall(
        func=ir.ExprAttribute(value=ir.TypeExprRefSelf(), attr="yield"),
        args=[],
        keywords=[],
    ))
    lines = lower_stmt(ctx, stmt)
    assert len(lines) == 1
    assert "//" in lines[0]


# ------------------------------------------------------------------ #
# lower_action body wiring                                            #
# ------------------------------------------------------------------ #

def test_body_no_task_when_no_exec_body():
    """Action with no exec body IR produces no body task override.
    The base class zsp_action provides an empty virtual body; no override needed.
    """
    ctx = _make_ctx()
    action = _make_simple_action(body_stmts=None)
    sv_class = lower_action(ctx, action)
    body_tasks = [t for t in sv_class.tasks if t.name == "body"]
    # No exec body in PSS -> no override task emitted (base class handles it)
    assert len(body_tasks) == 0


def test_body_empty_list_gets_placeholder():
    """Action with empty exec body ([]) gets '// empty body' placeholder."""
    ctx = _make_ctx()
    action = _make_simple_action(body_stmts=[])
    sv_class = lower_action(ctx, action)
    body_tasks = [t for t in sv_class.tasks if t.name == "body"]
    assert len(body_tasks) == 1
    assert any("empty body" in line for line in body_tasks[0].body_lines)


def test_body_with_message_call():
    """Action with message() exec body gets $display(...) in body task."""
    ctx = _make_ctx()
    body_stmts = [ir.StmtExpr(expr=ir.ExprCall(
        func=ir.ExprAttribute(value=ir.TypeExprRefSelf(), attr="message"),
        args=[
            ir.ExprConstant(value=1, kind=None),
            ir.ExprConstant(value="executing", kind=None),
        ],
        keywords=[],
    ))]
    action = _make_simple_action(body_stmts=body_stmts)
    sv_class = lower_action(ctx, action)
    body_tasks = [t for t in sv_class.tasks if t.name == "body"]
    assert len(body_tasks) == 1
    assert any("$display" in line for line in body_tasks[0].body_lines)


def test_body_with_assignment():
    """Action with assignment in exec body generates assignment line."""
    ctx = _make_ctx()
    body_stmts = [ir.StmtAssign(
        targets=[ir.ExprAttribute(value=ir.TypeExprRefSelf(), attr="result")],
        value=ir.ExprConstant(value=42, kind=None),
    )]
    action = _make_simple_action(body_stmts=body_stmts)
    sv_class = lower_action(ctx, action)
    body_tasks = [t for t in sv_class.tasks if t.name == "body"]
    assert len(body_tasks) == 1
    assert any("result = 42" in line for line in body_tasks[0].body_lines)


def test_pre_solve_empty_gets_noop():
    """Empty pre_solve exec block gets // no-op."""
    ctx = _make_ctx()
    action = _make_simple_action(pre_solve_stmts=[])
    sv_class = lower_action(ctx, action)
    funcs = [f for f in sv_class.functions if f.name == "pre_solve"]
    assert len(funcs) == 1
    assert any("no-op" in line for line in funcs[0].body_lines)


def test_pre_solve_with_stmt():
    """pre_solve exec block with a statement gets lowered."""
    ctx = _make_ctx()
    pre_stmts = [ir.StmtAssign(
        targets=[ir.ExprAttribute(value=ir.TypeExprRefSelf(), attr="mode")],
        value=ir.ExprConstant(value=1, kind=None),
    )]
    action = _make_simple_action(pre_solve_stmts=pre_stmts)
    sv_class = lower_action(ctx, action)
    funcs = [f for f in sv_class.functions if f.name == "pre_solve"]
    assert len(funcs) == 1
    assert any("mode = 1" in line for line in funcs[0].body_lines)


def test_both_body_and_pre_solve():
    """Action with both body and pre_solve lowers both."""
    ctx = _make_ctx()
    body_stmts = [ir.StmtExpr(expr=ir.ExprCall(
        func=ir.ExprAttribute(value=ir.TypeExprRefSelf(), attr="message"),
        args=[ir.ExprConstant(value=3, kind=None),
              ir.ExprConstant(value="done", kind=None)],
        keywords=[],
    ))]
    pre_stmts = [ir.StmtAssign(
        targets=[ir.ExprAttribute(value=ir.TypeExprRefSelf(), attr="x")],
        value=ir.ExprConstant(value=0, kind=None),
    )]
    action = _make_simple_action(body_stmts=body_stmts, pre_solve_stmts=pre_stmts)
    sv_class = lower_action(ctx, action)
    body_tasks = [t for t in sv_class.tasks if t.name == "body"]
    pre_funcs = [f for f in sv_class.functions if f.name == "pre_solve"]
    assert len(body_tasks) == 1
    assert len(pre_funcs) == 1
    assert any("$display" in l for l in body_tasks[0].body_lines)
    assert any("x = 0" in l for l in pre_funcs[0].body_lines)
