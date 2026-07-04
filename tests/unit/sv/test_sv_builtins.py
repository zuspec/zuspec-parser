"""PSS exec built-ins -> SV system tasks (WS1 increment 2).

The mapping is delivered as an SVExprEmitter call_hook, so it applies wherever a
call is rendered — standalone and inside statements.
"""
import zuspec.ir.core as ir
from zuspec.be.sv.ir.stmt_emit import SVStmtEmitter
from zuspec.be.sv.ir.stmt import SVStmtExpr

from pssc.targets.sv.sv_builtins import make_sv_expr_emitter


def _call(name, *args):
    return ir.ExprCall(func=ir.ExprRefUnresolved(name=name), args=list(args))


def _c(v):
    return ir.ExprConstant(value=v)


def test_message_maps_to_display_dropping_verbosity():
    e = make_sv_expr_emitter()
    out = e.emit(_call("message", _c("HIGH"), _c("hello %0d"), ir.ExprRefLocal(name="x")))
    assert out == '$display("hello %0d", x)'


def test_message_no_args():
    e = make_sv_expr_emitter()
    assert e.emit(_call("message")) == "$display()"


def test_print_maps_to_write():
    e = make_sv_expr_emitter()
    assert e.emit(_call("print", _c("x"))) == '$write("x")'


def test_error_and_fatal():
    e = make_sv_expr_emitter()
    assert e.emit(_call("error", _c("bad"))) == '$error("bad")'
    assert e.emit(_call("fatal", _c(1), _c("dead"))) == '$fatal(1, "dead")'


def test_yield_call_is_comment():
    e = make_sv_expr_emitter()
    assert e.emit(_call("yield")) == "// yield (no-op in SV class execution)"


def test_non_builtin_falls_through():
    e = make_sv_expr_emitter()
    assert e.emit(_call("do_thing", _c(1))) == "do_thing(1)"


def test_builtin_via_attribute_target():
    # self.message(...) form is also recognized
    e = make_sv_expr_emitter()
    call = ir.ExprCall(
        func=ir.ExprAttribute(value=ir.TypeExprRefSelf(), attr="message"),
        args=[_c(1), _c("hi")])
    assert e.emit(call) == '$display("hi")'


def test_builtin_in_statement_context_gets_semicolon():
    e = make_sv_expr_emitter()
    se = SVStmtEmitter(e)
    stmt = SVStmtExpr(expr=_call("message", _c(1), _c("hi")))
    assert se.emit_stmts([stmt], indent="") == ['$display("hi");']
