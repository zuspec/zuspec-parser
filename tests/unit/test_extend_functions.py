"""`extend component` bodies must reach the IR (operation-model design §3A).

This is the defect that emptied the whole operation model: `_translate_extend`
handled `Field`, `ExecBlock` and `ConstraintBlock` and silently ignored
everything else, while `_translate_component` handled six kinds. A model that
follows the PSS coding guidelines declares every operation and every action in
an `extend component` file, so all of them vanished -- and translation still
reported success, so nothing failed until a backend emitted an empty API.

The assertions here are therefore about **presence and count**, never about
"translation succeeded". Success was never in doubt; it was the wrong signal.
"""
import pytest

from pssc import Parser
from pssc.ast2ir import AstToIrTranslator
from zuspec.dataclasses import ir


def translate(pss_code: str):
    parser = Parser()
    parser.parses([("test.pss", pss_code)])
    return AstToIrTranslator(debug=False).translate(parser.link())


def _fn(comp, name):
    return next((f for f in comp.functions if f.name == name), None)


# --- functions -------------------------------------------------------------

def test_extend_adds_function():
    ctx = translate("""
        component C { int x; }
        extend component C {
            function int add(int a, int b) { return a; }
        }
    """)
    fn = _fn(ctx.type_map["C"], "add")
    assert fn is not None, "function declared in `extend component` was dropped"
    assert [a.arg for a in fn.args.args] == ["a", "b"]
    assert isinstance(fn.returns, ir.DataTypeInt)


def test_extend_adds_target_function():
    """The shape the operation model actually uses: `target function` with a
    body, one per file, each in its own `extend component`."""
    ctx = translate("""
        component C { int x; }
        extend component C { target function void op_a() { x = 1; } }
        extend component C { target function void op_b() { x = 2; } }
    """)
    comp = ctx.type_map["C"]
    names = [f.name for f in comp.functions]
    assert names == ["op_a", "op_b"], names


def test_extend_adds_solve_function():
    ctx = translate("""
        component C { int x; }
        extend component C { solve function void init(int id) { x = id; } }
    """)
    fn = _fn(ctx.type_map["C"], "init")
    assert fn is not None and fn.is_solve


# --- actions ---------------------------------------------------------------

def test_extend_adds_action():
    ctx = translate("""
        component C { int x; }
        extend component C { action my_a { } }
    """)
    assert "C::my_a" in ctx.type_map, sorted(ctx.type_map)
    assert ctx.parent_comp_names.get("C::my_a") == "C", (
        "action from `extend` must be parented to the extended component, "
        "or `comp.<op>()` in its body cannot resolve")


# --- nested type declarations ----------------------------------------------

def test_extend_adds_struct():
    ctx = translate("""
        component C { int x; }
        extend component C { struct s_t { rand int a; } }
    """)
    assert any(k.endswith("s_t") for k in ctx.type_map), sorted(ctx.type_map)


# --- regression: what `extend` already handled -----------------------------

def test_extend_preserves_field_exec_and_constraint():
    ctx = translate("""
        component C { int x; }
        extend component C {
            int y;
            exec init_down { y = 1; }
        }
    """)
    comp = ctx.type_map["C"]
    assert [f.name for f in comp.fields] == ["x", "y"]
    assert _fn(comp, "init_down") is not None


# --- the anti-drift test ---------------------------------------------------

def _shape(comp):
    """The part of a component's IR that both declaration paths must agree on."""
    return {
        "fields": [f.name for f in comp.fields],
        "functions": [(f.name,
                       [a.arg for a in f.args.args] if f.args else None,
                       type(f.returns).__name__,
                       f.is_solve, f.is_target)
                      for f in comp.functions],
    }


_BODY = """
    int y;
    function int add(int a, int b) { return a; }
    target function void op() { y = 1; }
    solve function void init(int id) { y = id; }
    action my_a { }
    exec init_down { y = 0; }
"""


def test_extend_and_inline_dispatch_agree():
    """The invariant the shared-dispatch refactor establishes: a body declared
    inline and the same body declared via `extend` produce the same IR.

    This is the cheap test that would have caught the original defect on day
    one, and it is what keeps the two paths from drifting again -- they now
    share one implementation, and this fails the moment someone re-splits them.
    """
    inline = translate("component C {" + _BODY + "}")
    extended = translate("component C { }\n extend component C {" + _BODY + "}")

    assert _shape(inline.type_map["C"]) == _shape(extended.type_map["C"])
    assert ("C::my_a" in inline.type_map) and ("C::my_a" in extended.type_map)
    assert (inline.parent_comp_names.get("C::my_a")
            == extended.parent_comp_names.get("C::my_a") == "C")


def test_extend_and_inline_dispatch_agree_is_not_vacuous():
    """Guard the guard: if `_BODY` ever stopped declaring anything the dispatch
    handles, the comparison above would pass on two empty components."""
    shape = _shape(translate("component C {" + _BODY + "}").type_map["C"])
    assert len(shape["fields"]) >= 1
    assert len(shape["functions"]) >= 4
