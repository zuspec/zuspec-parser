"""M0 smoke tests for the pure-SV (``sv-pure``) path.

Covers plan tasks F1 (target registration) and G1 (Verilator harness): proves
the harness compiles and runs a representative hand-written golden SV exercising
the constructs the pure-SV lowering relies on (class, ``rand``, ``constraint``,
``randomize()``). Later milestones run the harness on generated output.
"""
import textwrap

import pytest

from ._verilator import HAVE_VERILATOR, verilator_build_run


def test_sv_pure_target_registered():
    """F1: the sv-pure target is registered and selectable."""
    import pssc.targets as targets
    assert "sv-pure" in targets.list_targets()
    tgt = targets.get("sv-pure")
    assert tgt.name == "sv-pure"
    # M0 stub subclasses the sv-native target.
    from pssc.targets.sv_tgt import SvTarget
    assert isinstance(tgt, SvTarget)


# Representative of the shape the incremental lowering will emit: a runtime-style
# base action, a generated action subclass with rand fields + constraints, and a
# top that randomizes, runs the body, and checks the solver honored constraints.
_GOLDEN_SV = textwrap.dedent(
    """
    package zsp_rt_pkg;
      virtual class zsp_action;
        pure virtual task body();
      endclass
    endpackage

    package zsp_gen_pkg;
      import zsp_rt_pkg::*;
      class mem_write extends zsp_action;
        rand bit [31:0] addr;
        rand bit [7:0]  size;
        constraint c_align { addr[1:0] == 2'b00; }
        constraint c_size  { size inside {[1:64]}; }
        constraint c_range { addr inside {[32'h1000:32'h1FFF]}; }
        task body();
          $display("mem_write addr=0x%08x size=%0d", addr, size);
        endtask
      endclass
    endpackage

    module top;
      import zsp_gen_pkg::*;
      initial begin
        mem_write a = new();
        for (int i = 0; i < 5; i++) begin
          if (!a.randomize())
            $fatal(1, "randomize failed");
          a.body();
          if (a.addr[1:0] !== 2'b00)
            $fatal(1, "align constraint violated: addr=0x%08x", a.addr);
          if (a.size < 1 || a.size > 64)
            $fatal(1, "size constraint violated: size=%0d", a.size);
          if (a.addr < 32'h1000 || a.addr > 32'h1FFF)
            $fatal(1, "range constraint violated: addr=0x%08x", a.addr);
        end
        $display("PASS");
        $finish;
      end
    endmodule
    """
)


@pytest.mark.skipif(not HAVE_VERILATOR, reason="verilator not available")
def test_verilator_harness_compiles_golden(tmp_path):
    """G1: the Verilator harness builds+runs a golden SV and the SV solver
    honors the emitted constraints."""
    (tmp_path / "golden.sv").write_text(_GOLDEN_SV)
    rc, log = verilator_build_run(tmp_path, top_module="top")
    assert rc == 0, f"verilator build/run failed:\n{log}"
    assert "PASS" in log, f"expected PASS in output:\n{log}"
    assert "mem_write addr=" in log, f"body() did not run:\n{log}"


def _structured_constraint_pkg():
    """Build an SV class whose constraints come from the structured constraint
    IR (zuspec.ir.core.ConstraintBlock), emitted via be-sv (C1+C2 path)."""
    import zuspec.ir.core as ir
    from zuspec.be.sv.ir.sv_emit import SVEmitter
    from zuspec.be.sv.ir.sv import SVClass, SVClassField, SVPackage, SVTaskDecl

    def _self(n):
        return ir.ExprAttribute(value=ir.TypeExprRefSelf(), attr=n)

    def _c(v):
        return ir.ExprConstant(value=v)

    align = ir.ConstraintExpr(expr=ir.ExprBin(
        lhs=ir.ExprSubscript(value=_self("addr"),
                             slice=ir.ExprSlice(lower=_c(0), upper=_c(1))),
        op=ir.BinOp.Eq, rhs=_c(0)))
    rng = ir.ConstraintExpr(expr=ir.ExprIn(
        value=_self("addr"),
        container=ir.ExprRangeList(ranges=[ir.ExprRange(lower=_c(0x1000), upper=_c(0x1FFF))])))
    implies = ir.ConstraintImplies(
        antecedent=ir.ExprBin(lhs=_self("mode"), op=ir.BinOp.Eq, rhs=_c(1)),
        body=[ir.ConstraintExpr(expr=ir.ExprIn(
            value=_self("size"),
            container=ir.ExprRangeList(ranges=[ir.ExprRange(lower=_c(1), upper=_c(16))])))])
    blk = ir.ConstraintBlock(name="c_main", items=[align, rng, implies])

    cls = SVClass(
        name="mem_write",
        fields=[
            SVClassField(name="addr", dtype="bit [31:0]", is_rand=True),
            SVClassField(name="size", dtype="bit [7:0]", is_rand=True),
            SVClassField(name="mode", dtype="bit", is_rand=True),
        ],
        constraints=[blk],
        tasks=[SVTaskDecl(name="body", args=[], body_lines=[
            '$display("mem_write addr=0x%08x size=%0d mode=%0d", addr, size, mode);'])],
    )
    pkg = SVPackage(name="zsp_gen_pkg", items=[cls])
    return SVEmitter().emit_all([pkg])


_STRUCTURED_TOP = """
module top;
  import zsp_gen_pkg::*;
  initial begin
    mem_write a = new();
    for (int i = 0; i < 8; i++) begin
      if (!a.randomize()) $fatal(1, "randomize failed");
      a.body();
      if (a.addr[1:0] !== 2'b00) $fatal(1, "align violated: 0x%08x", a.addr);
      if (a.addr < 32'h1000 || a.addr > 32'h1FFF) $fatal(1, "range violated: 0x%08x", a.addr);
      if (a.mode == 1'b1 && (a.size < 1 || a.size > 16)) $fatal(1, "implies violated: %0d", a.size);
    end
    $display("PASS");
    $finish;
  end
endmodule
"""


@pytest.mark.skipif(not HAVE_VERILATOR, reason="verilator not available")
def test_structured_constraints_compile_and_solve(tmp_path):
    """C1+C2: structured constraint IR -> be-sv SVEmitter -> SV that compiles
    and whose solutions honor align/inside/implication constraints."""
    pkg_text = _structured_constraint_pkg()
    (tmp_path / "gen.sv").write_text(pkg_text + "\n" + _STRUCTURED_TOP)
    rc, log = verilator_build_run(tmp_path, top_module="top")
    assert rc == 0, f"verilator build/run failed:\n{log}"
    assert "PASS" in log, f"expected PASS in output:\n{log}"


def _atomic_action_and_tb():
    """M2 exit: an atomic action (rand fields + structured constraint block +
    structured body task) plus a testbench whose initial block is built from
    structured statements (SVStmtFor + SVStmtRandomize + call)."""
    import zuspec.ir.core as ir
    from zuspec.be.sv.ir.sv_emit import SVEmitter
    from zuspec.be.sv.ir.sv import SVClass, SVClassField, SVPackage, SVTaskDecl, SVModuleDecl
    from zuspec.be.sv.ir import stmt as s
    from zuspec.be.sv.ir.stmt_emit import SVStmtEmitter

    def _self(n):
        return ir.ExprAttribute(value=ir.TypeExprRefSelf(), attr=n)

    def _c(v):
        return ir.ExprConstant(value=v)

    # constraint block: align + inside range
    blk = ir.ConstraintBlock(name="c_main", items=[
        ir.ConstraintExpr(expr=ir.ExprBin(
            lhs=ir.ExprSubscript(value=_self("addr"),
                                 slice=ir.ExprSlice(lower=_c(0), upper=_c(1))),
            op=ir.BinOp.Eq, rhs=_c(0))),
        ir.ConstraintExpr(expr=ir.ExprIn(
            value=_self("addr"),
            container=ir.ExprRangeList(ranges=[ir.ExprRange(lower=_c(0x1000), upper=_c(0x1FFF))]))),
    ])
    # structured body task: $display(...)
    body = SVTaskDecl(name="body", body=[
        s.SVStmtExpr(expr=ir.ExprCall(
            func=ir.ExprRefUnresolved(name="$display"),
            args=[ir.ExprConstant(value="mem_write addr=0x%08x size=%0d"),
                  _self("addr"), _self("size")]))])
    cls = SVClass(
        name="mem_write",
        fields=[SVClassField(name="addr", dtype="bit [31:0]", is_rand=True),
                SVClassField(name="size", dtype="bit [7:0]", is_rand=True)],
        constraints=[blk], tasks=[body])
    pkg_text = SVEmitter().emit_all([SVPackage(name="zsp_gen_pkg", items=[cls])])

    # testbench initial block from structured statements
    loop = s.SVStmtFor(var="i", limit=_c(8), body=[
        s.SVStmtRandomize(target=ir.ExprRefLocal(name="a"), fail_msg="randomize failed"),
        s.SVStmtExpr(expr=ir.ExprCall(
            func=ir.ExprAttribute(value=ir.ExprRefLocal(name="a"), attr="body"), args=[])),
        s.SVStmtRaw(text="if (a.addr[1:0] !== 2'b00) $fatal(1, \"align\");"),
        s.SVStmtRaw(text="if (a.addr < 32'h1000 || a.addr > 32'h1FFF) $fatal(1, \"range\");"),
    ])
    init_lines = SVStmtEmitter().emit_stmts([loop], indent="  ")
    tb = SVModuleDecl(name="top", body_lines=(
        ["import zsp_gen_pkg::*;", "initial begin", "  mem_write a = new();"]
        + init_lines
        + ['  $display("PASS");', "  $finish;", "end"]))
    tb_text = SVEmitter().emit_one(tb)
    return pkg_text + "\n" + tb_text


@pytest.mark.skipif(not HAVE_VERILATOR, reason="verilator not available")
def test_atomic_action_structured_body_simulates(tmp_path):
    """M2 exit: atomic action fully through structured IR (constraints + body +
    procedural testbench stmts incl. randomize) compiles and simulates."""
    (tmp_path / "gen.sv").write_text(_atomic_action_and_tb())
    rc, log = verilator_build_run(tmp_path, top_module="top")
    assert rc == 0, f"verilator build/run failed:\n{log}"
    assert "PASS" in log, f"expected PASS:\n{log}"
    assert log.count("mem_write addr=") == 8, f"body should run 8x:\n{log}"
