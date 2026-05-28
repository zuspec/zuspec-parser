# Known Limitations — PSS-to-SV Lowering

This file documents gaps between valid PSS and what the current
`zuspec-fe-pss` SV backend handles correctly.

---

## All Previously-Known Limitations Fixed (as of 2026-05-08)

The following limitations (L1–L6 from the initial analysis) have been resolved.
All 12 simulation patterns now pass under VCS.

### L1 — Bit-slice constraints `addr[1:0] == 0`

**Root cause:** Two bugs:
1. `AstBuilderInt::mkExprBitSlice()` in `packages/pssparser/src/AstBuilderInt.cpp`
   used `constant_expression(0)` for both upper and lower bounds; fixed to
   `constant_expression(0)` / `constant_expression(1)`.
2. `AstToIrTranslator._apply_ref_bit_slice()` called `.getVal()` instead of
   `.getValue()` on `ExprUnsignedNumber` nodes.

**Fix locations:** `pssparser/src/AstBuilderInt.cpp` + `ast_to_ir.py`.

---

### L2 — Named action handles in activity blocks

**Root cause:** `_translate_action()` in `ast_to_ir.py` did not handle
`ActionHandleField` children, so named handle declarations inside activity
blocks (e.g. `link_init a_init;`) were silently dropped from the IR.

**Fix:** Added `ActionHandleField` handling in `_translate_action` to emit
them as `DataTypeRef` fields on the IR action class.

---

### L3 — State flow-object constraints (CNST-CIF)

**Root cause:** Several VCS-specific constraints on the SV class randomization
model:

1. Output flow-object fields (e.g. `next`) must be declared as `rand` handles
   in the SV class so VCS includes their sub-fields in the randomization scope.
   Without `rand`, constraints like `next.established == 1` are treated as
   constant-variable conflicts → CNST-CIF.

2. For compound actions with action-handle fields (`a_conn`, `a_xfr`, etc.),
   `do_test.randomize()` would traverse null input fields (e.g. `prev`) before
   they are injected in `body()`. Fix: call `handle.constraint_mode(0)` in
   `do_test.pre_solve()` to disable constraints during parent randomize, then
   `handle.constraint_mode(1)` before the explicit `handle.randomize()`.

3. State flow object `with { prev == flow_var }` constraints in the `with`
   clause cause CNST-CIF because `prev` is non-rand; removed these — field
   injection (`a.prev = flow_var`) before `pre_solve()` is sufficient.

4. Do NOT call `rand_mode(0)` on flow objects — VCS applies it class-wide,
   disabling randomization of ALL instances of that class.

5. Compound actions with no direct rand fields should skip `randomize()` in
   the test top to avoid null-handle traversal. The test generator now checks
   whether the root action has rand fields and conditionally skips randomize.

**Fix locations:** `lower_actions.py` (output field `rand` declaration, 
`pre_solve()` `constraint_mode` calls), `lower_activities.py` (remove
`with`-constraint for state inputs, remove `rand_mode(0)` for state objects,
add `constraint_mode(1)` re-enable before named handle's own randomize),
`test_sim_patterns.py` (skip randomize for compound root actions).

---

### L4 — Resource pool name from declaration

**Root cause:** `AstToIrTranslator` generates pool name from element type
(`dma_channel_r_pool`) rather than the declared identifier (`ch_pool`). The
PSS parser absorbs pool declarations during `TaskLink` so the original name
is unavailable in the linked AST.

**Current workaround:** Pool lookup in `lower_activities.py` matches on
element type name. Pool capacity defaults to 16 when not inferrable.

**Status:** Workaround in place; full fix requires pssparser to expose pool
declarations (name + capacity) in the linked AST before TaskLink absorbs them.

---

### L5 — `join_first`/`join_none`/`join_select` parallel keywords

**Root cause:** pssparser grammar gap.

**Status:** Not fixed; fix requires changes in pssparser package.

---

### L6 — Class-level action handle construction in `pre_solve()`

**Root cause:** `lower_actions.py` only constructed output flow-object fields
in `pre_solve()`, not action-handle fields (`rd`, `vf`, `wr` in
`copy_and_verify`).

**Fix:** `lower_actions.py` `pre_solve()` generation now also constructs
fields whose datatype resolves to a `DataTypeClass` (action handle fields),
and calls `constraint_mode(0)` on them to prevent parent randomize traversal.

---

## Summary

| ID  | Feature                                   | Status  |
|-----|-------------------------------------------|---------|
| L1  | Bit-slice constraints `addr[1:0] == 0`    | FIXED   |
| L2  | Named action handles in activity blocks   | FIXED   |
| L3  | State flow-object member constraints      | FIXED   |
| L4  | Pool name from declaration (workaround)   | workaround in place |
| L5  | `join_first/none/select` keywords         | needs pssparser fix |
| L6  | Class-level action handle construction    | FIXED   |

All 12 simulation patterns pass under VCS W-2024.09.
