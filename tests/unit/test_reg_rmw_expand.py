"""``--reg-rmw=expand``: the masked write spelled as what it is defined to be.

§21.14.1 defines the masked forms as a read-modify-write --

    REG_VAL(new) = (REG_VAL(current) & ~mask) | (val & mask)

-- so a backend with no RMW primitive can still carry the construct on the
``read_val`` / ``write_val`` it already implements. That is the whole of the
difference between the two modes: same bus traffic, different spelling. It is
what lets a model adopt the field-wise forms before any backend has been taught
`write_val_masked`.

The read is not an implementation detail that expansion introduces. It is in the
LRM's own definition, and on this device it matters: a channel CSR read clears
the ERR and interrupt-source bits. Neither mode removes it.
"""
import pytest

from pssc import Parser
from pssc.ast2ir import AstToIrTranslator
from pssc import reg_rmw
from zuspec.dataclasses import ir


_SRC = """
package p {
    import std_pkg::*;
    import addr_reg_pkg::*;
    struct csr_s : packed_s<> { rand bit[1] ch_en; rand bit[3] prio; rand bit[28] rsvd; }
    pure component csr_r : reg_c<csr_s, READWRITE, 32> {}
    pure component grp_c : reg_group_c { csr_r csr; }
    component top_c {
        grp_c regs;
        target function void f() { regs.csr.write_field("ch_en", 1); }
    }
}
"""


def translate(expand: bool):
    parser = Parser()
    parser.parses([("test.pss", _SRC)])
    ctx = AstToIrTranslator(debug=False).translate(parser.link())
    assert ctx.errors == []
    if expand:
        reg_rmw.expand_all(ctx)
    return ctx


def body(ctx):
    for fn in ctx.type_map["p::top_c"].functions:
        if fn.name == "f":
            return fn.body
    raise AssertionError("no f")


def test_native_leaves_the_primitive_alone():
    b = body(translate(expand=False))
    assert len(b) == 1
    assert b[0].expr.func.attr == "write_val_masked"


def test_expand_produces_a_declaration_a_read_and_a_write():
    """Three statements, in that order, and *nothing else*.

    An extra call would change the bus traffic, which is exactly what must not
    differ between the two modes.

    The declaration is hoisted to the top of the body rather than left at the
    expansion site: SystemVerilog permits a variable declaration only at the
    start of a block, so a temporary declared where the masked write happened to
    sit is illegal as soon as any statement precedes it -- or as soon as the
    write is inside an `if` arm.
    """
    b = body(translate(expand=True))
    assert len(b) == 3, [type(s).__name__ for s in b]

    decl, read, write = b
    assert isinstance(decl, ir.StmtAnnAssign)
    assert decl.value is None
    assert decl.annotation.bits == 32

    assert isinstance(read, ir.StmtAssign)
    assert read.value.func.attr == "read_val"
    assert read.value.args == []
    assert read.targets[0].name == decl.target.name

    assert isinstance(write, ir.StmtExpr)
    assert write.expr.func.attr == "write_val"
    assert len(write.expr.args) == 1


def test_expanded_expression_is_the_lrm_equation():
    """``(cur & ~mask) | (val & mask)``, with the constants folded.

    mask = 0x1, so ~mask over 32 bits is 0xfffffffe and ``val & mask`` is 1.
    """
    write = body(translate(expand=True))[-1]
    e = write.expr.args[0]
    assert e.op == ir.BinOp.BitOr

    keep, set_ = e.lhs, e.rhs
    assert keep.op == ir.BinOp.BitAnd
    assert isinstance(keep.lhs, ir.ExprRefLocal)          # the value just read
    assert keep.rhs.value == 0xfffffffe                   # ~mask, width-limited
    assert set_.value == 0x1                              # val & mask, folded


def test_the_temporary_is_the_one_that_was_read():
    """The write must consume the value the read produced, not a fresh name."""
    _, read, write = body(translate(expand=True))
    assert write.expr.args[0].lhs.lhs.name == read.targets[0].name


def test_no_masked_call_survives_expansion():
    """After expansion a backend sees only read_val / write_val."""
    for s in body(translate(expand=True)):
        for call in (getattr(s, "value", None), getattr(s, "expr", None)):
            if isinstance(call, ir.ExprCall):
                assert call.func.attr in ("read_val", "write_val")
