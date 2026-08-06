"""Which `solve function` is the constructor (design §3D).

The generator folds the root's constructor into the generated class: its
arguments become the factory's arguments and its first argument is the base
address the register model is built against. Recognition was hard-coded to the
name `ctor`.

A model whose constructor is called `init` -- the PSS coding guidelines' name,
written `\\init` because `init` is reserved -- had it classified as an ordinary
export function instead. The generated class then read

    m_regs = new(this, base);

with no `base` in scope: output that looks right and does not compile. That is
the failure mode this file exists to prevent, so the tests assert the *kind*,
not that generation succeeded.
"""
import pytest

from pssc import Parser
from pssc.ast2ir import AstToIrTranslator
from pssc.targets.progseq_model import func_kind, FuncKind, set_ctor_name


def translate(pss_code: str):
    """Translate ``pss_code`` and return its type map."""
    parser = Parser()
    parser.parses([("test.pss", pss_code)])
    return AstToIrTranslator(debug=False).translate(parser.link()).type_map


def _kinds(comp):
    return {fn.name: func_kind(fn) for fn in comp.functions}


@pytest.fixture(autouse=True)
def _restore_default_ctor_names():
    yield
    set_ctor_name(None)


_MODEL = """
import addr_reg_pkg::*;
component c_c {
    int x;
    solve function void %s(addr_handle_t base) { x = 1; }
    solve function void configure(int n) { x = n; }
    function void op() { x = 2; }
}
"""


def test_ctor_recognized():
    assert _kinds(translate(_MODEL % "ctor")["c_c"])["ctor"] is FuncKind.CONSTRUCTOR


def test_init_recognized_as_ctor():
    kinds = _kinds(translate(_MODEL % r"\init ")["c_c"])
    assert kinds["init"] is FuncKind.CONSTRUCTOR


def test_other_solve_functions_are_not_constructors():
    """Only the constructor is folded away; every other solve function is still
    part of the exported API and must keep being emitted."""
    kinds = _kinds(translate(_MODEL % "ctor")["c_c"])
    assert kinds["configure"] is FuncKind.EXPORT_SOLVE
    assert kinds["op"] is FuncKind.EXPORT_OP


def test_ctor_name_override():
    """`--ctor-name` narrows recognition to exactly one name, for a model that
    uses `init` as an ordinary API function."""
    set_ctor_name("ctor")
    kinds = _kinds(translate(_MODEL % r"\init ")["c_c"])
    assert kinds["init"] is FuncKind.EXPORT_SOLVE
