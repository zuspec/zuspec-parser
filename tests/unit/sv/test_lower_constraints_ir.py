"""Tests for structured constraint lowering (plan task E1).

`lower_constraint_func_ir` converts an IR constraint Function into a core
ConstraintBlock (D3); rendered here through the be-sv SVConstraintEmitter (D4)
to confirm the structured path reproduces the expected SV.
"""
import pytest
from zuspec.dataclasses import ir

from pssc.targets.sv.context import LoweringContext
from pssc.targets.sv.lower_constraints import lower_constraint_func_ir
from zuspec.be.sv.ir.constraint_emit import SVConstraintEmitter


@pytest.fixture
def ctx():
    return LoweringContext()


def _mk(name, body):
    return ir.Function(name=name, body=body, metadata={"_is_constraint": True})


def _lines(blk):
    return SVConstraintEmitter().emit_items(blk.items)


def test_returns_constraint_block(ctx):
    blk = lower_constraint_func_ir(ctx, _mk("c0", [
        ir.StmtExpr(expr=ir.ExprCompare(
            left=ir.ExprRefLocal(name="addr"), ops=[ir.CmpOp.GtE],
            comparators=[ir.ExprConstant(value=4096)])),
    ]))
    assert isinstance(blk, ir.ConstraintBlock)
    assert blk.name == "c0"
    assert isinstance(blk.items[0], ir.ConstraintExpr)
    assert _lines(blk) == ["(addr >= 4096);"]


def test_if_else(ctx):
    blk = lower_constraint_func_ir(ctx, _mk("c0", [
        ir.StmtIf(test=ir.ExprRefLocal(name="mode"),
                  body=[ir.StmtExpr(expr=ir.ExprRefLocal(name="x"))],
                  orelse=[ir.StmtExpr(expr=ir.ExprRefLocal(name="y"))]),
    ]))
    assert isinstance(blk.items[0], ir.ConstraintIfElse)
    assert _lines(blk) == ["if (mode) {", "  x;", "} else {", "  y;", "}"]


def test_foreach(ctx):
    blk = lower_constraint_func_ir(ctx, _mk("c0", [
        ir.StmtForeach(target=ir.ExprRefLocal(name="i"),
                       iter=ir.ExprRefLocal(name="data"),
                       body=[ir.StmtExpr(expr=ir.ExprIn(
                           value=ir.ExprSubscript(value=ir.ExprRefLocal(name="data"),
                                                  slice=ir.ExprRefLocal(name="i")),
                           container=ir.ExprRangeList(ranges=[
                               ir.ExprRange(lower=ir.ExprConstant(value=0),
                                            upper=ir.ExprConstant(value=9))])))]),
    ]))
    assert isinstance(blk.items[0], ir.ConstraintForeach)
    assert blk.items[0].index_var == "i"
    assert _lines(blk) == ["foreach (data[i]) {", "  data[i] inside {[0:9]};", "}"]


def test_unique(ctx):
    blk = lower_constraint_func_ir(ctx, _mk("c0", [ir.StmtUnique(vars=["a", "b", "c"])]))
    assert isinstance(blk.items[0], ir.ConstraintUnique)
    assert _lines(blk) == ["unique {a, b, c};"]


def test_implication_passthrough(ctx):
    blk = lower_constraint_func_ir(ctx, _mk("c0", [
        ir.StmtExpr(expr=ir.ExprCall(
            func=ir.ExprRefUnresolved(name="implies"),
            args=[ir.ExprRefLocal(name="mode"),
                  ir.ExprCompare(left=ir.ExprRefLocal(name="addr"),
                                 ops=[ir.CmpOp.Eq],
                                 comparators=[ir.ExprConstant(value=0)])])),
    ]))
    assert _lines(blk) == ["(mode -> (addr == 0));"]


def test_non_constraint_returns_none(ctx):
    assert lower_constraint_func_ir(ctx, ir.Function(name="body", body=[], metadata={})) is None


def test_unknown_field_filter_skips(ctx):
    # references self.bogus, not in known set -> skipped (None)
    func = _mk("c0", [
        ir.StmtExpr(expr=ir.ExprBin(
            lhs=ir.ExprAttribute(value=ir.TypeExprRefSelf(), attr="bogus"),
            op=ir.BinOp.Eq, rhs=ir.ExprConstant(value=0))),
    ])
    assert lower_constraint_func_ir(ctx, func, known_field_names=["addr"]) is None
