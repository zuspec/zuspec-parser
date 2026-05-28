# PSS Test Patterns

Original PSS 2.0 models written for the zuspec test suite.
Released under the same Apache 2.0 / MIT license as the repository.

These models are **not** derived from any third-party source.  They were
written from scratch to exercise the PSS language features defined in the
Accellera PSS specification (Accellera copyright), using completely original
domain scenarios, type names, and structural choices.

## Scope

The patterns collectively exercise:

| PSS feature | Pattern(s) |
|---|---|
| rand fields, range constraints, named constraints, exec body | `hello_world.pss` |
| Buffer flow objects, produce/consume, activity bind | `producer_consumer.pss` |
| Compound traversal: named action handles, inline constraints, bind | `compound_traversal.pss` |
| Resource pool, `lock`, parallel fork/join, repeat | `parallel_resources.pss` |
| Resource pool, `share`, concurrent sharing of a read-only resource | `resource_share.pss` |
| Stream flow objects, `schedule` block, labeled traversals, abstract action, inheritance | `pipeline_stream.pss` |
| State flow objects, state-threading through sequential actions | `state_flow.pss` |
| Abstract action, named constraint override in derived types | `abstract_action.pss` |
| Weighted `select`, conditional guards, `if/else` | `select_weighted.pss` |
| `replicate` with and without index, replicate inside schedule | `replicate_indexed.pss` |
| Nested `parallel`, default join-all semantics | `join_variants.pss` |
| Component hierarchy, sub-component nesting, struct fields | `nested_components.pss` |

## pssparser compatibility notes

The following PSS 3.x features are defined in the Accellera spec but are not
yet parseable by the version of `pssparser` bundled with zuspec.  The
affected patterns work around these limitations with a comment explaining the
restriction:

- `parallel join_first / join_none / join_select { ... }` — pssparser does
  not yet accept join-specifier keywords on the `parallel` keyword.
- Constraint blocks referencing flow-object sub-fields
  (`constraint c { out.field.member == x; }`) — pssparser does not resolve
  composite scope paths on flow-object fields inside named constraint blocks.

These are pssparser gaps, not zuspec SV-lowering gaps.  The IR nodes
(`JoinSpec`, flow-object field refs) are supported by the lowering code and
are exercised in the unit tests under `tests/unit/sv/`.
