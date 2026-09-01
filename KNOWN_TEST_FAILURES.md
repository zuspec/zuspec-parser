# Known test failures — zuspec-be-sv and zuspec-be-sw

Recorded 2026-09-01, during the pssc PyPI release work.

**None of this is packaging fallout.** It all predates the release work. It was
invisible because neither repo had CI until now, and the first run each got
could not even install `pytest` (see *How this surfaced*, below). The failures
are excluded in each repo's `pytest.ini`, with the same explanation inline, so
that the ~670 tests that *do* pass can gate CI. Every entry below is a bug to
fix, not a test to delete.

Baselines, measured on Python 3.13 with the full `default-dev` dep-set:

| repo | before excluding | after excluding |
|---|---|---|
| zuspec-be-sv | 180 passed, 14 failed, 4 skipped, 1 collection error | 180 passed, 4 skipped, 3 deselected |
| zuspec-be-sw | 544 passed, 47 failed, 36 skipped, 82 errors | 491 passed, 35 skipped |

---

## zuspec-be-sw

Two root causes account for essentially all of it.

### 1. `AbstractionFieldIR` has no `.datatype` — 53 failures

`src/zuspec/be/sw/passes/elaborate.py:123`:

```python
for field in dtype.fields:
    field_dtype = self._resolve_type(field.datatype, ctxt)
```

The loop assumes every entry in `dtype.fields` is an ordinary field. It is not.
An abstraction field (`IndexedRegFile`, `Counter`, …) elaborates to
`zuspec.ir.core.AbstractionFieldIR`, which is a *deliberately opaque* node —
`spec_type_name`, `field_name`, `field_index`, `py_cls`, `inst_kwargs`,
`ir_node`, and no `datatype`. So any component containing an abstraction field
raises `AttributeError` during elaboration.

**This is a gap in be-sw's abstraction-field support, not IR drift.** ir-core is
doing exactly what it documents; be-sw needs to dispatch on the node kind rather
than assume a single shape. Fixing this one loop should clear most of the 53.

Affected: `test_minicore_integration.py` (16), `test_backdoor_protocols.py` (8),
`test_topology_b.py` (7), and part of `test_rvcore_integration.py` and
`test_c_runtime_regfile.py`.

### 2. The `org.zuspec.example.*` fixture corpus is missing — 72 errors

```python
from org.zuspec.example.mls.riscv.rv_units import ALUUnit
```

No `org` package exists anywhere in the workspace, and none is declared by
`ivpm.yaml` or `pyproject.toml`. These tests were written against a corpus that
never shipped with the repo. Either vendor it, or declare where it comes from.

Affected: `test_rvcore_integration.py` (73 total), `test_rvcore_units_integration.py`
(10), `test_c_runtime_regfile.py` (11).

### 3. `zuspec.fe.pss` is absent — 19 skips, not failures

`_pss_harness.py` and `_sv_bridge_harness.py` use `importorskip`, so these
degrade to skips on their own and need no exclusion. Worth knowing that this
coverage is silently not running: `zuspec-fe-pss` is not in this workspace.

### Excluded files

`test_rvcore_integration.py`, `test_rvcore_units_integration.py`,
`test_c_runtime_regfile.py`, `test_minicore_integration.py`,
`test_backdoor_protocols.py`, `test_topology_b.py`, `test_pss_examples_e2e.py`,
`test_pss_sv_example_e2e.py`, `passes/rtl/test_debug_layer.py`

File-level rather than per-test: every one is broken in whole or in large part,
and per-test deselection would run to ~129 entries and rot faster than it helps.

---

## zuspec-be-sv

### 1. `zuspec.cli` does not exist — 1 collection error

`test_be_cli_plugin.py` imports it, via `src/zuspec/be/sv/cli_plugin.py`, which
does `from zuspec.cli.plugin import Plugin` **at module scope**. Nothing
declares that dependency and no such package is in this workspace.

`cli_plugin` is not reachable from `zuspec/be/sv/__init__.py`, so installed
wheels import fine — but it is a landmine of exactly the kind that produced the
truncated-wheel bugs earlier in this release: shipped source importing something
undeclared. Either declare `zuspec-cli` or guard the import.

### 2. Transactor API drift — 8 failures

`test_xtor_smoke.py` (8/8) fails with a `TypeError` from the `SVGenerator`
constructor plus assertion failures. The transactor API moved and its tests did
not follow.

### 3. Tests requiring a real simulator — 2 failures

`test_sim.py` (2/2) and the `[vlt]`/`[xsm]` parametrisations want verilator or
xsim on `PATH`. They cannot pass on a stock GitHub runner regardless of
correctness. These should be marked and skipped on absence, the way
`test_param_simulation.py` already does for iverilog.

### 4. Assorted assertion failures — 4

`test_smoke.py::test_smoke` (1/1), and 3 of 11 in `test_translation.py`
(`test_basic_counter`, `test_arithmetic_operations`, `test_multiple_outputs`).
The other 8 in `test_translation.py` still run and still gate.

### Not excluded — fixed properly instead

`test_fsm_to_sv.py`, `test_mmr_to_sv.py` and `test_protocol_to_sv.py` were also
failing collection, on `No module named 'zuspec.synth'`. Those tests were not
broken — the dependency was simply undeclared. `zuspec-synth` was added to
`ivpm.yaml`'s `default-dev` and all three pass, so they keep gating CI.

---

## How this surfaced

These repos had no CI at all before this release work. The workflow added during
it ran `ivpm update -a --py-pip` — and `-a` is `--anonymous-git`, *not* a
dep-set selector — so ivpm fell back to "the first dep-set in the file". For
be-py that was `default` (runtime deps only); for be-sv that dep-set was
outright *empty*. Nothing installed, so the runs died on
`pytest: No such file or directory` long before any test could fail.

Fixing that (`default-dep-set: default-dev`) is what made the suites run for the
first time, and what exposed everything above.
