"""Tests for Phase 5 features: resource pools, instance_id fields, trace,
coverage, head-action solve, and ActivityReplicate.
"""
import pytest
from zuspec.dataclasses import ir
from zuspec.ir.core.fields import FieldKind
from zuspec.be.sv.ir.sv_emit import SVEmitter

from pssc.targets.sv.context import LoweringContext
from pssc.targets.sv.lower_components import lower_component
from pssc.targets.sv.lower_actions import lower_action
from pssc.targets.sv.lower_activities import (
    lower_activity,
    _lower_activity_stmt,
    _lower_replicate,
)
from pssc.targets.sv.lower_coverage import lower_action_covergroups
from pssc.targets.sv.lower_stmts import lower_stmt


@pytest.fixture
def ctx():
    return LoweringContext()


@pytest.fixture
def emitter():
    return SVEmitter()


# --------------------------------------------------------------------------- #
# 5.1c: Resource pool fields on component classes                             #
# --------------------------------------------------------------------------- #

class TestResourcePoolComponent:
    def test_pool_field_emitted(self, ctx, emitter):
        comp = ir.DataTypeComponent(
            name="dma_c",
            super=None,
            fields=[],
            pools=[
                ir.Pool(name="channel_pool", element_type_name="channel_r",
                        element_type=None, capacity=4),
            ],
        )
        sv = lower_component(ctx, comp)
        text = emitter.emit_one(sv)
        assert "zsp_resource_pool #(channel_r) channel_pool;" in text

    def test_pool_constructor_call(self, ctx, emitter):
        comp = ir.DataTypeComponent(
            name="dma_c",
            super=None,
            fields=[],
            pools=[
                ir.Pool(name="ch_pool", element_type_name="ch_r",
                        element_type=None, capacity=2),
            ],
        )
        sv = lower_component(ctx, comp)
        text = emitter.emit_one(sv)
        assert 'ch_pool = new(2);' in text

    def test_multiple_pools(self, ctx, emitter):
        comp = ir.DataTypeComponent(
            name="top_c",
            super=None,
            fields=[],
            pools=[
                ir.Pool(name="pool_a", element_type_name="res_a",
                        element_type=None, capacity=2),
                ir.Pool(name="pool_b", element_type_name="res_b",
                        element_type=None, capacity=8),
            ],
        )
        sv = lower_component(ctx, comp)
        text = emitter.emit_one(sv)
        assert "zsp_resource_pool #(res_a) pool_a;" in text
        assert "zsp_resource_pool #(res_b) pool_b;" in text

    def test_no_pools_no_pool_fields(self, ctx, emitter):
        comp = ir.DataTypeComponent(name="simple_c", super=None, fields=[])
        sv = lower_component(ctx, comp)
        text = emitter.emit_one(sv)
        assert "zsp_resource_pool" not in text

    def test_pool_capacity_one_default(self, ctx, emitter):
        comp = ir.DataTypeComponent(
            name="t_c",
            super=None,
            fields=[],
            pools=[
                ir.Pool(name="p", element_type_name="r_t",
                        element_type=None, capacity=0),  # 0 -> default to 1
            ],
        )
        sv = lower_component(ctx, comp)
        text = emitter.emit_one(sv)
        assert "zsp_resource_pool #(r_t) p;" in text


# --------------------------------------------------------------------------- #
# 5.1d: instance_id rand fields in action lowering                            #
# --------------------------------------------------------------------------- #

class TestInstanceIdFields:
    def test_lock_field_gets_instance_id(self, ctx, emitter):
        ch_field = ir.Field(
            name="ch",
            datatype=ir.DataTypeRef(ref_name="channel_r"),
            kind=FieldKind.Lock,
        )
        act = ir.DataTypeClass(
            name="write_a",
            super=None,
            fields=[ch_field],
            functions=[],
        )
        sv = lower_action(ctx, act)
        text = emitter.emit_one(sv)
        assert "rand int unsigned ch_instance_id;" in text

    def test_share_field_gets_instance_id(self, ctx, emitter):
        ch_field = ir.Field(
            name="mem",
            datatype=ir.DataTypeRef(ref_name="mem_r"),
            kind=FieldKind.Share,
        )
        act = ir.DataTypeClass(
            name="read_a",
            super=None,
            fields=[ch_field],
            functions=[],
        )
        sv = lower_action(ctx, act)
        text = emitter.emit_one(sv)
        assert "rand int unsigned mem_instance_id;" in text

    def test_plain_field_no_instance_id(self, ctx, emitter):
        plain = ir.Field(
            name="addr",
            datatype=ir.DataTypeInt(bits=32, signed=False),
            kind=FieldKind.Field,
        )
        act = ir.DataTypeClass(
            name="addr_a",
            super=None,
            fields=[plain],
            functions=[],
        )
        sv = lower_action(ctx, act)
        text = emitter.emit_one(sv)
        assert "instance_id" not in text

    def test_multiple_resource_fields(self, ctx, emitter):
        ch_field = ir.Field(
            name="ch",
            datatype=ir.DataTypeRef(ref_name="ch_r"),
            kind=FieldKind.Lock,
        )
        mem_field = ir.Field(
            name="mem",
            datatype=ir.DataTypeRef(ref_name="mem_r"),
            kind=FieldKind.Share,
        )
        act = ir.DataTypeClass(
            name="dual_a",
            super=None,
            fields=[ch_field, mem_field],
            functions=[],
        )
        sv = lower_action(ctx, act)
        text = emitter.emit_one(sv)
        assert "rand int unsigned ch_instance_id;" in text
        assert "rand int unsigned mem_instance_id;" in text


# --------------------------------------------------------------------------- #
# 5.1e: Trace macro injection                                                 #
# --------------------------------------------------------------------------- #

class TestTraceMacros:
    def test_traversal_has_trace_action(self, ctx):
        trav = ir.ActivityTraversal(handle="a1")
        lines = _lower_activity_stmt(ctx, trav, "comp")
        text = "\n".join(lines)
        assert "`ZSP_TRACE_ACTION" in text

    def test_anon_traversal_has_trace_action(self, ctx):
        trav = ir.ActivityAnonTraversal(action_type="WriteAction")
        lines = _lower_activity_stmt(ctx, trav, "comp")
        text = "\n".join(lines)
        assert "`ZSP_TRACE_ACTION" in text

    def test_parallel_has_trace(self, ctx):
        par = ir.ActivityParallel(stmts=[
            ir.ActivityTraversal(handle="a1"),
            ir.ActivityTraversal(handle="a2"),
        ])
        lines = _lower_activity_stmt(ctx, par, "comp")
        text = "\n".join(lines)
        assert "`ZSP_TRACE" in text
        assert "parallel" in text

    def test_select_has_trace(self, ctx):
        sel = ir.ActivitySelect(branches=[
            ir.SelectBranch(body=[ir.ActivityTraversal(handle="a1")]),
        ])
        lines = _lower_activity_stmt(ctx, sel, "comp")
        text = "\n".join(lines)
        assert "`ZSP_TRACE" in text
        assert "select" in text

    def test_schedule_has_trace(self, ctx):
        sched = ir.ActivitySchedule(stmts=[
            ir.ActivityAnonTraversal(action_type="WriteAction"),
        ])
        lines = _lower_activity_stmt(ctx, sched, "comp")
        text = "\n".join(lines)
        assert "`ZSP_TRACE" in text
        assert "schedule" in text


# --------------------------------------------------------------------------- #
# 5.1f: Coverage lowering                                                     #
# --------------------------------------------------------------------------- #

class TestCoverageLowering:
    def test_action_with_no_covergroups(self, ctx):
        act = ir.DataTypeClass(
            name="simple_a",
            super=None,
            fields=[],
            functions=[],
            covergroups=[],
        )
        lines = lower_action_covergroups(ctx, "simple_a", act)
        assert lines == []

    def test_action_with_rand_fields_gets_covergroup(self, ctx):
        act = ir.DataTypeClass(
            name="write_a",
            super=None,
            fields=[
                ir.Field(name="addr", datatype=ir.DataTypeInt(bits=32, signed=False),
                         rand_kind="rand"),
            ],
            functions=[],
            covergroups=[object()],  # non-empty -> trigger covergroup emission
        )
        lines = lower_action_covergroups(ctx, "write_a", act)
        text = "\n".join(lines)
        assert "covergroup" in text
        assert "cp_addr" in text
        assert "coverpoint addr" in text
        assert "endgroup" in text
        assert "cg_inst" in text

    def test_stmt_cover_lower(self, ctx):
        stmt = ir.StmtCover(
            test=ir.ExprConstant(value=1),
            msg=None,
        )
        lines = lower_stmt(ctx, stmt)
        text = "\n".join(lines)
        assert "cover" in text

    def test_stmt_cover_with_msg(self, ctx):
        stmt = ir.StmtCover(
            test=ir.ExprConstant(value=1),
            msg=ir.ExprConstant(value=42),
        )
        lines = lower_stmt(ctx, stmt)
        text = "\n".join(lines)
        assert "`ZSP_TRACE" in text
        assert "cover" in text


# --------------------------------------------------------------------------- #
# 5.1g: ActivityReplicate                                                     #
# --------------------------------------------------------------------------- #

class TestActivityReplicate:
    def test_replicate_emits_fork(self, ctx):
        repl = ir.ActivityReplicate(
            count=ir.ExprConstant(value=4),
            body=[ir.ActivityAnonTraversal(action_type="WriteAction")],
        )
        lines = _lower_replicate(ctx, repl, "comp")
        text = "\n".join(lines)
        assert "fork" in text
        assert "join" in text

    def test_replicate_uses_count(self, ctx):
        repl = ir.ActivityReplicate(
            count=ir.ExprConstant(value=3),
            body=[ir.ActivityAnonTraversal(action_type="ReadAction")],
        )
        lines = _lower_replicate(ctx, repl, "comp")
        text = "\n".join(lines)
        assert "3" in text

    def test_replicate_via_lower_activity_stmt(self, ctx):
        repl = ir.ActivityReplicate(
            count=ir.ExprConstant(value=2),
            body=[ir.ActivityAnonTraversal(action_type="Tx")],
        )
        lines = _lower_activity_stmt(ctx, repl, "comp")
        text = "\n".join(lines)
        assert "fork" in text
        assert "Tx" in text

    def test_replicate_with_index_var(self, ctx):
        repl = ir.ActivityReplicate(
            count=ir.ExprConstant(value=4),
            index_var="idx",
            body=[ir.ActivityAnonTraversal(action_type="ReadAction")],
        )
        lines = _lower_replicate(ctx, repl, "comp")
        text = "\n".join(lines)
        assert "idx" in text
        assert "4" in text

    def test_replicate_body_executed_in_fork(self, ctx):
        repl = ir.ActivityReplicate(
            count=ir.ExprConstant(value=2),
            body=[ir.ActivityTraversal(handle="wr")],
        )
        lines = _lower_replicate(ctx, repl, "comp")
        text = "\n".join(lines)
        assert "wr.body();" in text
        assert "fork" in text
