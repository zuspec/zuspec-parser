"""The call-legality registry: the tier contract, and the manifest's honesty.

Two tests here carry the design rather than a behaviour:

  * `test_every_target_renders_the_common_set` is the Tier 1 contract. Without
    it "COMMON" is an aspiration each backend independently fails to meet --
    which was the state that produced four disagreeing copies of the builtin
    list (docs §3.0).

  * `test_manifest_matches_the_front_end_stdlib` is the check that keeps the
    Python manifest from drifting from the language. Tier 0 SHOULD be derived
    from the front end's declarations rather than restated here; it is not,
    because the declarations do not survive into the IR -- `type_map` carries
    `addr_reg_pkg::reg_group_c` with an EMPTY `functions` list, and package-scope
    functions like `print`/`read32` are not represented at all. Until ast2ir
    retains them (docs §10, item 8), a cross-check against the stdlib SOURCE is
    what makes the restatement safe: drift fails here instead of shipping.
"""
import os
import re

import pytest

from pssc.targets.call_legality import (COMMON, Ctx, Disposition, EXTENSIONS,
                                        Outcome, PROGSEQ_TARGETS, TIER0,
                                        classify, entries_for, renderable)

_STDLIB = os.path.normpath(os.path.join(
    os.path.dirname(__file__), "..", "..", "..", "pssparser", "src", "stdlib"))


# --- the tier contract ------------------------------------------------------

def test_every_target_renders_the_common_set():
    """A target may EXTEND the common set. It may never shrink it."""
    for target in PROGSEQ_TARGETS:
        missing = set(COMMON) - renderable(target)
        assert not missing, (
            f"{target} does not render common calls: {sorted(missing)}")


def test_extensions_do_not_contradict_common():
    """A Tier 2 entry must not re-declare a Tier 1 name as unsupported --
    that would be shrinking the common set through the back door."""
    for target, ext in EXTENSIONS.items():
        for name, entry in ext.items():
            if name in COMMON:
                assert not entry.unsupported, (
                    f"{target} marks common call '{name}' unsupported")


def test_sv_extends_beyond_common():
    """The SV target is the reference backend; if it added nothing, the tiering
    would be describing a distinction that does not exist."""
    assert renderable("op-model-sv") > set(COMMON)


def test_c_cannot_do_channels_and_says_why():
    """The C backend's real capability gap, and the reason the tiers exist at
    all rather than one flat list."""
    r = classify("try_put", context=Ctx.TARGET, target="c-progseq")
    assert r.outcome is Outcome.UNSUPPORTED_HERE
    assert "channel_c" in r.message
    assert classify("try_put", context=Ctx.TARGET, target="op-model-sv").ok


# --- the four outcomes ------------------------------------------------------

def test_supported():
    r = classify("message", context=Ctx.SOLVE, target="op-model-sv")
    assert r.ok and r.entry.disposition is Disposition.UTILITY


def test_unsupported_here_names_the_prerequisite():
    """Math is registered, not omitted: the diagnostic must say it is a real
    core-library function blocked on float64, not 'unknown call'."""
    r = classify("sqrt", context=Ctx.TARGET, target="op-model-sv")
    assert r.outcome is Outcome.UNSUPPORTED_HERE
    assert "float64" in r.message and "21.5.2" in r.message


def test_wrong_context_for_a_bus_access_in_a_constructor():
    """addr_reg_pkg declares read32 as a plain `function`, so the FRONT END
    permits this. The lowering cannot: there is no bus while the model is being
    constructed. The message has to explain itself, not just cite a rule."""
    r = classify("read32", context=Ctx.SOLVE, target="op-model-sv")
    assert r.outcome is Outcome.WRONG_CONTEXT
    assert "target context" in r.message


def test_unknown_points_at_the_import_route():
    r = classify("my_helper", context=Ctx.TARGET, target="op-model-sv")
    assert r.outcome is Outcome.UNKNOWN
    assert "import" in r.message


def test_model_names_are_not_in_any_tier():
    """An operation of the component being lowered, an import function and a
    sub-component constructor are all model names, resolved from the model."""
    assert classify("transfer_single", context=Ctx.TARGET, target="op-model-sv",
                    model_ops=frozenset({"transfer_single"})).ok
    assert classify("dma_bfm", context=Ctx.TARGET, target="op-model-sv",
                    imports=frozenset({"dma_bfm"})).ok
    assert classify("initialize", context=Ctx.SOLVE, target="op-model-sv",
                    subcomps=frozenset({"initialize"})).ok


# --- keeping the manifest honest -------------------------------------------

def _declared_in_stdlib():
    """Free-function names declared by the front end's stdlib SOURCE."""
    names = set()
    pat = re.compile(
        r"^\s*(?:(?:solve|target|pure|import)\s+)*function\s+[\w:\[\]<>, ]+?"
        r"(\w+)\s*\(", re.M)
    for fn in ("std_pkg.pss", "addr_reg_pkg.pss", "sync_pkg.pss"):
        path = os.path.join(_STDLIB, fn)
        if not os.path.exists(path):
            continue
        src = re.sub(r"//[^\n]*", "", open(path).read())
        names |= set(pat.findall(src))
    return names


@pytest.mark.skipif(not os.path.isdir(_STDLIB), reason="stdlib source not present")
def test_manifest_matches_the_front_end_stdlib():
    """Every stdlib-declared function must be in SOME tier.

    A name the front end resolves but no tier knows falls straight through to
    the verbatim fallthrough -- which is how `urandom()` would have reached
    generated SystemVerilog as a call to a function that does not exist.
    """
    known = set(COMMON) | set(TIER0)
    for ext in EXTENSIONS.values():
        known |= set(ext)
    # Declared on components (reg_c, channel_c) rather than at package scope,
    # and already covered by the REG/CHANNEL dispositions.
    known |= {"get_handle", "add_addr_space"}
    missing = _declared_in_stdlib() - known
    assert not missing, (
        f"declared by the stdlib but in no tier, so they would fall through to "
        f"verbatim emission: {sorted(missing)}")


def test_error_and_fatal_are_still_missing_from_the_stdlib():
    """PSS 3.1 §21.3 puts error() and fatal() in std_pkg; the front end's
    stdlib does not declare them, so a model calling error() does not resolve.

    Registered in COMMON regardless -- the registry states the LANGUAGE, and
    this test is the reminder that the front end has not caught up. Flip it to
    an equality assertion when std_pkg.pss gains them (docs §9, Phase 1a).
    """
    declared = _declared_in_stdlib()
    if not declared:
        pytest.skip("stdlib source not readable")
    assert {"error", "fatal"} - declared == {"error", "fatal"}, (
        "std_pkg.pss now declares error/fatal -- Phase 1a is done; "
        "update this test to assert they ARE declared")


def test_tier0_entries_all_carry_a_reason():
    """An entry with no reason is indistinguishable from a supported one, and
    would produce a diagnostic that says nothing."""
    for name, entry in TIER0.items():
        assert entry.unsupported, f"Tier 0 entry '{name}' has no reason"


def test_entries_for_merges_in_precedence_order():
    """COMMON must not be shadowed by Tier 0, and a target extension must be
    able to make a Tier 0 name renderable."""
    sv = entries_for("op-model-sv")
    assert not sv["make_handle_from_handle"].unsupported
    assert not sv["print"].unsupported
    assert entries_for("c-progseq")["format"].unsupported


# --- the gate, end to end ---------------------------------------------------

# `read_bytes` is DECLARED by addr_reg_pkg, so the front end resolves it -- which
# is what makes this a test of the backend gate rather than of name resolution.
# (`sqrt` would not do: the stdlib does not declare the math functions, so the
# front end rejects it first. That is the Tier 0 distinction in action.)
_BAD_MODEL = """
import addr_reg_pkg::*;

component gate_c {
    target function void go(addr_handle_t h) {
        write_bytes(h, null);
    }
}
"""


def test_unlowerable_call_fails_the_build_and_writes_nothing(tmp_path):
    """The whole point: a call with no lowering must stop the compile, and must
    not leave a partial artifact behind for a later build to treat as
    up-to-date.
    """
    import argparse
    from pssc import driver

    src = tmp_path / "gate.pss"
    src.write_text(_BAD_MODEL)
    out = tmp_path / "out"
    out.mkdir()
    ns = argparse.Namespace(progseq_root="gate_c", progseq_package="gate_pkg",
                            output_dir=str(out))
    with pytest.raises(driver.CompileError) as ei:
        driver.compile([str(src)], target="op-model-sv", opts=ns)

    joined = "\n".join(ei.value.errors)
    assert "write_bytes" in joined and "list" in joined
    assert "gate_c::go" in joined, "the diagnostic must locate the call"
    assert not list(out.glob("gate_pkg.sv")), "a rejected compile wrote output"


def test_a_lowerable_model_still_generates(tmp_path):
    """The gate must not be so eager that it rejects the models that work --
    the risk any newly-added gate carries."""
    import argparse
    from pssc import driver
    model = os.path.join(os.path.dirname(__file__), "data", "offset_fold.pss")

    out = tmp_path / "ok"
    out.mkdir()
    ns = argparse.Namespace(progseq_root="fold_top_c", progseq_package="fold_top_pkg",
                            output_dir=str(out))
    res = driver.compile([model], target="op-model-sv", opts=ns)
    assert res.outputs
