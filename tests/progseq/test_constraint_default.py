"""pssparser drops `constraint default` bodies before they reach the AST.

A front-end observation, recorded here because it is invisible from the outside:
`constraint default X == V;` parses without error into a `ConstraintBlock`
carrying **zero** statements, so `ast2ir` has nothing to translate. Measured (see
`test_the_parser_drops_the_default_constraint_body`):

    two plain constraints    -> 3 blocks, 2 statements
    one plain + one default  -> 3 blocks, 1 statement
    only a default           -> 2 blocks, 0 statements

The relational constraint survives; the default does not.

SCOPE -- this does NOT affect either shipping op-model API. Constraints and
actions are deliberately excluded from an operation model: there is no solver in
a generated C image, and the op-model-sv target emits no constraints either. The
generated SV package contains **zero** occurrences of `constraint`, including
`constraint tot_sz > 0`, which reaches the IR perfectly well. So the eleven
defaults on `wb_dma_ch_cfg_s` are absent from both APIs by design, not by this
defect, and a C-side `_DEFAULT` macro knob (plan C6.5) is out of scope rather
than blocked.

Where it WOULD matter is a solver-capable target, which is the only kind that
consumes constraints at all. The `xfail(strict=True)` markers below describe the
behaviour that should hold at the AST/IR level for such a target, and will start
failing loudly -- as XPASS -- the day pssparser carries the body.
"""
import os

import pytest

from pssc import driver
from pssc.frontend import Parser

from .codetext import code_only
from .op_model import op_model_sources


_PROBE = """
package p {
    struct s_t {
        rand bit[32] a;
        rand bit[32] b;
%s
    }
}
"""


def _blocks_and_stmts(body):
    """(ConstraintBlock count, total constraint-statement count) in the AST."""
    p = Parser()
    p.parses([("t.pss", _PROBE % body)])
    root = p.link()
    n = [0, 0]

    def walk(x):
        try:
            kids = x.children() or []
        except Exception:
            return
        for c in kids:
            if c is None:
                continue
            if type(c).__name__ == "ConstraintBlock":
                n[0] += 1
                n[1] += len(c.getConstraints() or [])
            walk(c)

    walk(root)
    return tuple(n)


def test_a_plain_constraint_reaches_the_ast():
    """The control. Without it, "the default is dropped" could just as well mean
    constraints on structs are dropped wholesale."""
    assert _blocks_and_stmts("        constraint b > 0;")[1] == 1


def test_the_parser_drops_the_default_constraint_body():
    """The measurement, as behaviour rather than prose. This test passes TODAY
    and documents the defect; the two below are the ones that should pass.

    Kept separate so that when pssparser is fixed exactly one thing breaks here
    and its name says what changed.
    """
    # NOTE: this is a front-end fact only. No op-model backend reads constraints,
    # so nothing downstream of here changes when it is fixed -- see module docstring.
    plain = _blocks_and_stmts("        constraint b > 0;\n"
                              "        constraint a == 7;")
    mixed = _blocks_and_stmts("        constraint b > 0;\n"
                              "        constraint default a == 7;")
    assert plain[1] == 2, plain
    assert mixed[1] == 1, (
        f"a default constraint now carries a body ({mixed}); pssparser was "
        f"fixed -- remove the xfail markers below and implement C6.5")


@pytest.mark.xfail(strict=True,
                   reason="pssparser drops `constraint default` bodies before "
                          "they reach the AST")
def test_a_default_constraint_should_reach_the_ast():
    assert _blocks_and_stmts("        constraint default a == 7;")[1] == 1


@pytest.mark.xfail(strict=True,
                   reason="pssparser drops `constraint default` bodies, so the "
                          "value never reaches the IR for a solver target")
def test_the_models_defaults_should_be_visible_in_the_ir():
    """The same loss, stated against the REAL model rather than a probe.

    `wb_dma_ch_cfg_s` documents `src_mask == 0xfffffffc`; nothing in the IR says
    so. No op-model backend would read it if it did -- but a solver-capable
    target has no other source for the value, so this is where the defect would
    first become visible. Asserting it here means the fix is detected against the
    real model, not just a two-field probe.
    """
    ctx = driver.translate(op_model_sources()).ir_context
    cfg = ctx.type_m["wb_dma_ch_cfg_s"]

    # Whichever way it eventually arrives -- a field initial_value, or a
    # constraint the backend can recognise as an equality default -- the value
    # has to be findable. Accept either shape so this test survives the fix.
    by_field = {f.name: getattr(f, "initial_value", None) for f in cfg.fields}
    if by_field.get("src_mask") is not None:
        assert getattr(by_field["src_mask"], "value", None) == 0xfffffffc
        return

    text = " ".join(str(f.body) for f in cfg.functions)
    assert "4294967292" in text or "fffffffc" in text.lower(), (
        "the model states `constraint default src_mask == 0xfffffffc` and "
        "nothing in the IR carries it")


# --- the exclusion itself, as behaviour rather than prose -------------------

def test_no_constraint_reaches_the_c_output():
    """Constraints and actions are excluded from an operation model silently and
    by construction (design §10) -- there is no solver in a generated C image.

    Stated as a test because it was previously only prose, and prose is what let
    me mistake an *intended* absence for a front-end defect: I found that
    pssparser drops `constraint default` bodies, saw the model's defaults missing
    from the generated APIs, and joined the two. They are unrelated. The plain
    `constraint tot_sz > 0` reaches the IR intact (see the control test above)
    and is equally absent from the output, which is the fact that distinguishes
    "excluded by design" from "lost in the front end".

    So this asserts the *surviving* constraint is dropped too. A backend that
    started projecting equality defaults would still pass a test that only looked
    for the defaults; it would fail this one.
    """
    import argparse
    import tempfile
    from pssc import driver

    with tempfile.TemporaryDirectory() as out:
        ns = argparse.Namespace(progseq_root="wb_dma_c", c_prefix="wb_dma",
                                output_dir=out, c_header_only=True)
        driver.compile(list(op_model_sources()), target="op-model-c", opts=ns)
        text = (
            open(os.path.join(out, "wb_dma.h")).read()
            if os.path.exists(os.path.join(out, "wb_dma.h")) else "")

    # Comments excluded. The output carries the register model's own
    # documentation, and `0xfffffffc` is also this register's RDL *reset*
    # value, which appears in a field's comment. That is a different fact
    # about the same number; the claim here is about what is emitted as code.
    code = code_only(text)

    # Positive control: the FIELD is emitted, so the absence below is the
    # constraint being excluded and not the struct being missing.
    assert "tot_sz" in code and "src_mask" in code
    # `tot_sz > 0` survives to the IR and is still not emitted...
    assert "tot_sz > 0" not in code
    # ...and neither is any value that only a `constraint default` states.
    assert "0xfffffffc" not in code.lower()


def test_no_constraint_reaches_the_sv_output():
    """The same boundary on the other op-model target, which is what makes it a
    boundary rather than a C limitation. The generated SV package contains zero
    occurrences of `constraint` -- checked against the model's own plain
    constraint, not just its defaults, for the reason given above.
    """
    import argparse
    import tempfile
    from pssc import driver

    with tempfile.TemporaryDirectory() as out:
        ns = argparse.Namespace(progseq_root="wb_dma_c", output_dir=out)
        driver.compile(list(op_model_sources()), target="op-model-sv", opts=ns)
        text = "".join(
            open(os.path.join(out, f)).read()
            for f in sorted(os.listdir(out)) if f.endswith(".sv"))

    code = code_only(text)
    assert "tot_sz" in code, "positive control: the field itself must be emitted"
    # Comments excluded for the same reason as above: the model's prose is now
    # carried into the output, and prose about a constraint is not a constraint.
    assert "constraint" not in code
