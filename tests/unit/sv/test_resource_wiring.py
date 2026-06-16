"""Unit tests for resource acquire/release wiring in activity lowering (Phase 5, T5.1-T5.3).

Tests that lock/share resource claims on action fields generate the correct
pool.lock() / pool.unlock() calls around the action's lifecycle.
"""
from __future__ import annotations

import pytest
from zuspec.dataclasses import ir
from zuspec.ir.core.fields import FieldKind
from zuspec.ir.core import expr as ir_expr

from pssc.targets.sv.context import LoweringContext
from pssc.targets.sv.lower_activities import (
    _lower_anon_traversal,
    _get_resource_claims,
)


# ------------------------------------------------------------------ #
# Helpers                                                              #
# ------------------------------------------------------------------ #

def _make_action_type_with_resource(lock: bool = True):
    """Build a DataTypeClass IR with one resource field (Lock or Share)."""
    kind = FieldKind.Lock if lock else FieldKind.Share
    return ir.DataTypeClass(
        name="top_c::xfer_a",
        super=None,
        py_type=None,
        fields=[
            ir.Field(
                name="channel",
                datatype=ir.DataTypeRef(ref_name="channel_r"),
                kind=kind,
            ),
        ],
        functions=[],
        is_abstract=False,
        flow_kind=None,
        has_initial_constraint=False,
        covergroups=[],
        activity_ir=None,
    )


def _make_ctx_with_type(action_type_name, dtype):
    """Build a LoweringContext with one type registered."""
    from pssc.ast2ir import AstToIrContext
    ir_ctx = AstToIrContext()
    ir_ctx.add_type(action_type_name, dtype)
    return LoweringContext(ir_ctx=ir_ctx)


def _make_anon(action_type, label=None):
    return ir.ActivityAnonTraversal(
        action_type=action_type,
        label=label,
        inline_constraints=[],
        action_type_cls=None,
        comp_expr=None,
        init_bindings=[],
    )


# ------------------------------------------------------------------ #
# Tests: _get_resource_claims                                          #
# ------------------------------------------------------------------ #

def test_get_resource_claims_lock():
    """Lock field detected as a resource claim."""
    dtype = _make_action_type_with_resource(lock=True)
    ctx = _make_ctx_with_type("top_c::xfer_a", dtype)
    claims = _get_resource_claims(ctx, "act", "top_c::xfer_a")
    assert len(claims) == 1
    assert claims[0].claim_kind == "lock"
    assert claims[0].field_name == "channel"


def test_get_resource_claims_share():
    """Share field detected as a resource claim."""
    dtype = _make_action_type_with_resource(lock=False)
    ctx = _make_ctx_with_type("top_c::xfer_a", dtype)
    claims = _get_resource_claims(ctx, "act", "top_c::xfer_a")
    assert len(claims) == 1
    assert claims[0].claim_kind == "share"


def test_get_resource_claims_no_resources():
    """Action without resource fields returns empty list."""
    dtype = ir.DataTypeClass(
        name="top_c::simple_a",
        super=None, py_type=None,
        fields=[ir.Field(name="val", datatype=ir.DataTypeInt(bits=8, signed=False))],
        functions=[], is_abstract=False, flow_kind=None,
        has_initial_constraint=False, covergroups=[], activity_ir=None,
    )
    ctx = _make_ctx_with_type("top_c::simple_a", dtype)
    claims = _get_resource_claims(ctx, "act", "top_c::simple_a")
    assert claims == []


def test_get_resource_claims_no_ir_ctx():
    """No ir_ctx returns empty list (graceful degradation)."""
    ctx = LoweringContext()
    claims = _get_resource_claims(ctx, "act", "top_c::xfer_a")
    assert claims == []


# ------------------------------------------------------------------ #
# Tests: resource acquire/release in traversal                         #
# ------------------------------------------------------------------ #

def test_lock_acquire_emitted_before_body():
    """Lock acquire (pool.lock) is emitted after pre_solve, before body."""
    dtype = _make_action_type_with_resource(lock=True)
    ctx = _make_ctx_with_type("top_c::xfer_a", dtype)

    trav = _make_anon("top_c::xfer_a", "act_x")
    lines = _lower_anon_traversal(ctx, trav, "comp", None)
    joined = "\n".join(lines)

    print(joined)  # for debugging

    assert ".lock(" in joined, f"No lock call in:\n{joined}"

    # lock must come AFTER randomize (so instance_id is determined) and BEFORE body
    rand_idx = joined.index("randomize()")
    lock_idx = joined.index(".lock(")
    body_idx = joined.index(".body()")

    assert rand_idx < lock_idx < body_idx, (
        f"Expected: randomize({rand_idx}) < lock({lock_idx}) < body({body_idx})"
    )


def test_lock_release_emitted_after_body():
    """Lock release (pool.unlock) is emitted after body()."""
    dtype = _make_action_type_with_resource(lock=True)
    ctx = _make_ctx_with_type("top_c::xfer_a", dtype)

    trav = _make_anon("top_c::xfer_a", "act_x")
    lines = _lower_anon_traversal(ctx, trav, "comp", None)
    joined = "\n".join(lines)

    assert ".unlock(" in joined, f"No unlock call in:\n{joined}"

    body_idx = joined.index(".body()")
    unlock_idx = joined.index(".unlock(")

    assert body_idx < unlock_idx, (
        f"Expected: body({body_idx}) < unlock({unlock_idx})"
    )


def test_share_acquire_emitted():
    """Share claim emits try_share (non-blocking)."""
    dtype = _make_action_type_with_resource(lock=False)
    ctx = _make_ctx_with_type("top_c::xfer_a", dtype)

    trav = _make_anon("top_c::xfer_a", "act_x")
    lines = _lower_anon_traversal(ctx, trav, "comp", None)
    joined = "\n".join(lines)

    # share acquire: try_share or share
    has_share = "share" in joined or "try_share" in joined
    assert has_share, f"No share call in:\n{joined}"
    assert "unshare(" in joined, f"No unshare call in:\n{joined}"


def test_no_resource_no_lock_calls():
    """Action with no resource fields has no lock/unlock calls."""
    dtype = ir.DataTypeClass(
        name="top_c::simple_a",
        super=None, py_type=None,
        fields=[ir.Field(name="val", datatype=ir.DataTypeInt(bits=8, signed=False))],
        functions=[], is_abstract=False, flow_kind=None,
        has_initial_constraint=False, covergroups=[], activity_ir=None,
    )
    ctx = _make_ctx_with_type("top_c::simple_a", dtype)

    trav = _make_anon("top_c::simple_a", "act_s")
    lines = _lower_anon_traversal(ctx, trav, "comp", None)
    joined = "\n".join(lines)

    assert ".lock(" not in joined
    assert ".unlock(" not in joined
    assert ".randomize()" in joined  # lifecycle still present
