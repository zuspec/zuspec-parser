"""Phase 4 (P4.T2): the conformance suite, and proof it can fail.

Every check here corresponds to a real defect found late in one of pssc's own
backends, and none of them fails a build. A suite that only ever passes proves
nothing about the suite, so each check has a stub target built to break exactly
it -- if a check stops catching its own stub, the check has rotted.
"""
from __future__ import annotations

import pytest

from pssc.targets.op_model import OpModelTarget
from pssc.testing import conformance


@pytest.fixture
def registered():
    from pssc import targets
    added = []

    def add(target):
        targets.register(target)
        added.append(target.name)
        return target.name

    yield add
    for name in added:
        targets._REGISTRY.pop(name, None)


def _check(report, name):
    for c in report.checks:
        if c.name == name:
            return c
    raise AssertionError(f"no check named {name!r} in {report}")


# -- the built-ins -----------------------------------------------------------

@pytest.mark.parametrize("target", ["op-model-sv", "op-model-c", "op-model-cpp"])
def test_the_builtins_pass_their_own_conformance_suite(target):
    report = conformance.run(target)
    assert report.ok, str(report)
    assert len(report.checks) == 5


def test_assert_conforms_returns_the_report():
    report = conformance.assert_conforms("op-model-c")
    assert report.target == "op-model-c" and report.ok


def test_the_report_reads_as_a_report():
    text = str(conformance.run("op-model-c"))
    assert "5/5 passed" in text and "[PASS] addresses-match-fold" in text


# -- what the address check actually asserts ---------------------------------

def test_relative_and_absolute_addressing_are_both_accepted():
    """The C backend folds a nested group's base into one flat accessor
    (`base + 0x3c`); C++ constructs the group at its own base and writes
    `base + 0x1c`. Both are correct. An expectation that admitted only one
    spelling reported the C backend as emitting a wrong address -- which is the
    worst outcome available to a check whose purpose is to be believed."""
    for target in ("op-model-c", "op-model-cpp"):
        assert _check(conformance.run(target), "addresses-match-fold").passed


def test_a_value_is_found_in_any_language_spelling():
    from pssc.testing.conformance import _value_appears
    for text in ("base + 0x1c)", "base + 64'h1c)", "base + 28;",
                 "0x1cu", "0x001C", "'h1C"):
        assert _value_appears(text, 0x1c), text
    for text in ("0x1cd", "0x11c", "128", "281"):
        assert not _value_appears(text, 0x1c), text


def test_an_operation_is_found_behind_a_symbol_prefix():
    from pssc.testing.conformance import _name_appears
    assert _name_appears("void dma_engine_configure_channel(", "configure_channel")
    assert _name_appears("task configure_channel(", "configure_channel")
    assert not _name_appears("configure_channel_ex(", "configure_channel")
    assert not _name_appears("xconfigure_channel(", "configure_channel")


# -- the stubs ---------------------------------------------------------------

class _Base(OpModelTarget):
    """A minimal conforming-ish backend the stubs below each break one way."""
    language = "text"
    legality_target = "op-model-c"

    def _lines(self, model):
        out = []
        for comp in model.components:
            for fn in model.operations(comp):
                out.append(f"void {fn.name}(void);")
        for group in model.reg_groups:
            for field in (getattr(group, "fields", None) or []):
                name = getattr(field, "name", "")
                if not name or name.startswith("_"):
                    continue
                try:
                    out.append(f"#define {name}_OFF "
                               f"{hex(model.offset_of(group, name))}")
                except Exception:
                    pass
        return out

    def emit(self, model, opts):
        p = model.out_dir / "out.h"
        p.write_text("\n".join(self._lines(model)) + "\n")
        return [p]


def test_the_stub_baseline_conforms(registered):
    """The control. Without it, a stub failing proves only that the stub is
    broken somewhere, not that it is broken where intended."""
    class _Good(_Base):
        name = "x-conf-good"

    registered(_Good())
    report = conformance.run("x-conf-good")
    assert report.ok, str(report)


def test_a_target_that_drops_an_operation_fails(registered):
    class _Dropper(_Base):
        name = "x-conf-drop"

        def _lines(self, model):
            return [ln for ln in super()._lines(model)
                    if "mem_to_mem_copy_desc" not in ln]

    registered(_Dropper())
    report = conformance.run("x-conf-drop")
    assert not report.ok
    failed = _check(report, "operations-present")
    assert not failed.passed
    assert "mem_to_mem_copy_desc" in failed.detail
    # ...and only that check failed
    assert [c.name for c in report.failures] == ["operations-present"]


def test_a_target_that_emits_a_wrong_address_fails(registered):
    """The bug class a golden snapshot can NEVER catch: a wrong address frozen
    into a snapshot stays green forever."""
    class _Wrong(_Base):
        name = "x-conf-addr"

        def _lines(self, model):
            return [ln.replace("0x1c", "0x2c") for ln in super()._lines(model)]

    registered(_Wrong())
    report = conformance.run("x-conf-addr")
    failed = _check(report, "addresses-match-fold")
    assert not failed.passed
    assert "SWPTR" in failed.detail


def test_a_target_that_emits_an_empty_api_fails(registered):
    class _Empty(_Base):
        name = "x-conf-empty"

        def _lines(self, model):
            return ["/* nothing */"]

    registered(_Empty())
    report = conformance.run("x-conf-empty")
    assert not report.ok
    assert not _check(report, "operations-present").passed
    assert not _check(report, "addresses-match-fold").passed


def test_a_nondeterministic_target_fails(registered):
    seq = {"n": 0}

    class _Flaky(_Base):
        name = "x-conf-flaky"

        def _lines(self, model):
            seq["n"] += 1
            return super()._lines(model) + [f"/* run {seq['n']} */"]

    registered(_Flaky())
    report = conformance.run("x-conf-flaky")
    assert not _check(report, "regeneration-is-byte-stable").passed


def test_a_target_that_writes_nothing_fails(registered):
    class _Silent(_Base):
        name = "x-conf-silent"

        def emit(self, model, opts):
            return []

    registered(_Silent())
    report = conformance.run("x-conf-silent")
    failed = _check(report, "path-list-is-a-compilation-order")
    assert not failed.passed
    assert "nothing downstream" in failed.detail


def test_a_target_returning_sv_in_the_wrong_order_fails(registered):
    """The core package must precede the generated package that imports it.
    The returned list IS what a build system compiles, in order."""
    class _Backwards(_Base):
        name = "x-conf-order"

        def emit(self, model, opts):
            gen = model.out_dir / "gen_pkg.sv"
            core = model.out_dir / "pssc_reg_pkg.sv"
            gen.write_text("\n".join(self._lines(model)) + "\n")
            core.write_text("// core\n")
            return [gen, core]

    registered(_Backwards())
    report = conformance.run("x-conf-order")
    failed = _check(report, "path-list-is-a-compilation-order")
    assert not failed.passed
    assert "precedes the core package" in failed.detail


def test_a_report_survives_a_target_that_refuses_the_model(registered):
    """A target whose legality set cannot render the shipped model reports a
    failed CHECK, not a crashed suite -- the other four still run."""
    class _Strict(_Base):
        name = "x-conf-strict"
        legality_target = "x-conf-strict-nothing"

    registered(_Strict())
    report = conformance.run("x-conf-strict")
    assert len(report.checks) == 5
