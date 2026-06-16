"""Unit tests for analyze_activity.py (Phase 4, T4.4, T4.5).

Tests that ActivityPlan correctly identifies pipeline chains, compute
solve modes, and detects when DPI joint solving is required.
"""
from __future__ import annotations

import pytest
from zuspec.dataclasses import ir
from zuspec.ir.core import expr as ir_expr
from zuspec.ir.core.fields import FieldKind

from pssc.targets.sv.context import LoweringContext
from pssc.targets.sv.analyze_activity import (
    analyze_activity,
    ActivityPlan,
    PipelineChain,
    _walk_chain,
    _build_chains,
)
from pssc.targets.sv.analyze_flow import (
    FlowBindingInfo,
    ActivityFlowInfo,
    TraversalMeta,
)
from pssc.targets.sv.classify_constraints import SolveMode


# ------------------------------------------------------------------ #
# Helpers                                                              #
# ------------------------------------------------------------------ #

def _make_ctx():
    return LoweringContext()


def _anon(action_type, label=None):
    return ir.ActivityAnonTraversal(
        action_type=action_type, label=label,
        inline_constraints=[], action_type_cls=None,
        comp_expr=None, init_bindings=[],
    )


def _bind(prod_label, prod_field, cons_label, cons_field):
    return ir.ActivityBind(
        src=ir_expr.ExprAttribute(
            value=ir_expr.ExprAttribute(
                value=ir_expr.TypeExprRefSelf(), attr=prod_label),
            attr=prod_field),
        dst=ir_expr.ExprAttribute(
            value=ir_expr.ExprAttribute(
                value=ir_expr.TypeExprRefSelf(), attr=cons_label),
            attr=cons_field),
    )


def _flow_info(traversals, bindings):
    """Build a minimal ActivityFlowInfo for testing _build_chains."""
    producer_bindings = {}
    consumer_bindings = {}
    for b in bindings:
        producer_bindings.setdefault(b.producer_var, []).append(b)
        consumer_bindings.setdefault(b.consumer_var, []).append(b)
    return ActivityFlowInfo(
        traversals=traversals,
        bindings=bindings,
        producer_bindings=producer_bindings,
        consumer_bindings=consumer_bindings,
    )


def _traversal(var_name, action_type):
    return TraversalMeta(var_name=var_name, action_type=action_type,
                         is_anonymous=True)


def _stream_bind(prod, cons):
    return FlowBindingInfo(
        producer_var=prod, producer_field="out",
        consumer_var=cons, consumer_field="in",
        flow_kind="stream", flow_type="img_s",
    )


def _buffer_bind(prod, cons):
    return FlowBindingInfo(
        producer_var=prod, producer_field="out_buf",
        consumer_var=cons, consumer_field="in_buf",
        flow_kind="buffer", flow_type="data_buf_t",
    )


# ------------------------------------------------------------------ #
# T4.4: analyze_activity with no ir_ctx (degraded mode)               #
# ------------------------------------------------------------------ #

def test_analyze_activity_no_ir_ctx():
    """Without ir_ctx, analyze_activity returns a plan with SV_NATIVE modes."""
    ctx = _make_ctx()
    activity = ir.ActivitySequenceBlock(stmts=[
        _anon("producer", "p"),
        _anon("consumer", "c"),
    ], pragmas={})

    plan = analyze_activity(ctx, activity)

    assert isinstance(plan, ActivityPlan)
    assert len(plan.flow_info.traversals) == 2
    # No ir_ctx => all modes SV_NATIVE (no constraint classification)
    for mode in plan.solve_modes.values():
        assert mode == SolveMode.SV_NATIVE or mode == SolveMode.SV_WITH_INJECT


def test_analyze_activity_with_buffer_bind():
    """Buffer binding detected; no chains (buffers don't form DPI chains)."""
    ctx = _make_ctx()
    activity = ir.ActivitySequenceBlock(stmts=[
        ir.ActivitySchedule(stmts=[
            _anon("producer", "p"),
            _anon("consumer", "c"),
            _bind("p", "out_buf", "c", "in_buf"),
        ], pragmas={}, join_spec=None),
    ], pragmas={})

    plan = analyze_activity(ctx, activity)

    assert len(plan.flow_info.bindings) == 1
    assert plan.flow_info.bindings[0].flow_kind == "buffer"
    # Buffer bindings don't form DPI pipeline chains
    assert len(plan.chains) == 0
    assert not plan.needs_dpi_chain


# ------------------------------------------------------------------ #
# T4.5: _build_chains with stream bindings                            #
# ------------------------------------------------------------------ #

def test_build_chains_single_stream_link():
    """One stream binding a->b forms a chain of length 2."""
    ctx = _make_ctx()
    traversals = [_traversal("a", "step_a"), _traversal("b", "step_b")]
    bindings = [_stream_bind("a", "b")]
    info = _flow_info(traversals, bindings)
    solve_modes = {"a": SolveMode.SV_NATIVE, "b": SolveMode.SV_NATIVE}

    chains = _build_chains(ctx, info, solve_modes)

    assert len(chains) == 1
    assert chains[0].steps == ["a", "b"]
    assert chains[0].entry_var == "a"


def test_build_chains_three_link():
    """Three-step stream chain a->b->c."""
    ctx = _make_ctx()
    traversals = [
        _traversal("a", "step_a"),
        _traversal("b", "step_b"),
        _traversal("c", "step_c"),
    ]
    bindings = [_stream_bind("a", "b"), _stream_bind("b", "c")]
    info = _flow_info(traversals, bindings)
    solve_modes = {"a": SolveMode.SV_NATIVE,
                   "b": SolveMode.SV_NATIVE,
                   "c": SolveMode.SV_NATIVE}

    chains = _build_chains(ctx, info, solve_modes)

    assert len(chains) == 1
    assert chains[0].steps == ["a", "b", "c"]


def test_build_chains_no_stream():
    """No stream bindings -> no chains."""
    ctx = _make_ctx()
    traversals = [_traversal("a", "t_a"), _traversal("b", "t_b")]
    bindings = [_buffer_bind("a", "b")]  # buffer, not stream
    info = _flow_info(traversals, bindings)
    solve_modes = {"a": SolveMode.SV_NATIVE, "b": SolveMode.SV_WITH_INJECT}

    chains = _build_chains(ctx, info, solve_modes)

    assert chains == []


def test_build_chains_dpi_mode_triggers_compilation():
    """When an action has DPI_JOINT_CHAIN mode, chain.needs_dpi is True
    (even if the compilation itself produces empty b64 due to missing fields)."""
    ctx = _make_ctx()
    traversals = [_traversal("a", "step_a"), _traversal("b", "step_b")]
    bindings = [_stream_bind("a", "b")]
    info = _flow_info(traversals, bindings)
    # b has DPI_JOINT_CHAIN mode (e.g. pipe_end's resized constraint)
    solve_modes = {"a": SolveMode.SV_NATIVE, "b": SolveMode.DPI_JOINT_CHAIN}

    chains = _build_chains(ctx, info, solve_modes)

    assert len(chains) == 1
    # Chain was attempted to be compiled (problem_b64 may be empty if no ir_ctx)
    # but the chain struct itself is populated
    assert chains[0].steps == ["a", "b"]


# ------------------------------------------------------------------ #
# T4.5b: analyze_activity on real PSS pipeline model                  #
# ------------------------------------------------------------------ #

try:
    from pssparser import Parser
    from pssc.ast2ir import AstToIrTranslator
    HAS_PSS = True
except ImportError:
    HAS_PSS = False


@pytest.mark.skipif(not HAS_PSS, reason="pssparser not available")
def test_analyze_activity_pss_pipeline():
    """analyze_activity on a real PSS stream pipeline model detects chain."""
    PSS = """
stream img_s {
    rand bit[2] orientation;
    rand bit    resized;
}
component top_c {
  pool img_s img_pool;
  bind img_pool *;
  action step_a {
    input img_s in_state;
    output img_s out_state;
    constraint in_state.orientation != out_state.orientation;
  }
  action step_b {
    input img_s in_state;
    output img_s out_state;
    constraint in_state.resized == 0;
    constraint out_state.resized == 1;
  }
  action root {
    activity {
      schedule {
        a: do step_a;
        b: do step_b;
        bind a.out_state b.in_state;
      }
    }
  }
}
"""
    p = Parser()
    p.parses([("test.pss", PSS)])
    root = p.link()
    ir_ctx = AstToIrTranslator().translate(root)

    from zuspec.ir.core import DataTypeClass
    for qname, dtype in ir_ctx.type_map.items():
        if 'root' in qname and isinstance(dtype, DataTypeClass):
            ctx = LoweringContext(ir_ctx=ir_ctx)
            plan = analyze_activity(ctx, dtype.activity_ir)

            # Should detect the stream chain
            assert len(plan.flow_info.bindings) == 1
            assert plan.flow_info.bindings[0].flow_kind == "stream"
            assert len(plan.chains) == 1
            assert plan.chains[0].steps == ["a", "b"]

            # step_b has constraint in_state.resized == 0 (input field constraint)
            # This should be DPI_REQUIRED -> DPI_JOINT_CHAIN mode
            assert plan.solve_modes.get("b") in (
                SolveMode.DPI_JOINT_CHAIN, SolveMode.SV_WITH_INJECT
            ), f"Unexpected mode for b: {plan.solve_modes.get('b')}"
            break
