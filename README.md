# pssc — the PSS compiler

`pssc` compiles [Portable Test and Stimulus Standard](https://www.accellera.org/downloads/standards/portable-stimulus)
(PSS) source into executable artifacts. It parses PSS with
[`pssparser`](https://github.com/psstools/pssparser), maps the AST to the
[Zuspec IR](https://github.com/zuspec/zuspec-ir-core), and lowers that IR to a
selected **target** via the Zuspec backends.

> `pssc` is the successor to `zuspec-fe-pss`. Migrating? See
> [docs/migration-from-zuspec-fe-pss.md](docs/migration-from-zuspec-fe-pss.md).

## Install

```sh
pip install pssc        # or: ivpm update   (for a source/dev checkout)
```

## Quickstart

```sh
# list available targets
pssc targets

# generate live Python classes for early evaluation (writes a class manifest)
pssc compile model.pss --target python --emit repr -o out/

# generate SystemVerilog (classes solved by the SV solver)
pssc compile model.pss --target sv -o out/

# front-end only: dump the canonical IR as YAML for inspection
pssc parse model.pss --dump-ir model.ir.yaml
```

Programmatic use:

```python
import pssc

result = pssc.compile("model.pss", target="python")
Top = result.value["pss_top"]          # live zdc class

pssc.compile("model.pss", target="sv", output_dir="out/")
```

## Output styles

`pssc` is designed to drive PSS to the full set of Zuspec implementation styles
(see [docs/targets.md](docs/targets.md) for status):

| # | Style | `--target` | Status |
|---|---|---|---|
| 1 | SystemVerilog classes, solved by the SV solver | `sv-native` (alias `sv`) | available |
| 2 | SV facade calling the C runtime via DPI | `sv-dpi` | available (co-sim needs a simulator) |
| 3 | Host C coroutine runtime (dv-solve) | `c-host`, `c-host-presolved` | available |
| 4 | Embedded C coroutine runtime, runtime solve | `c-embedded` | available |
| 5 | Embedded C, pre-solved constraints | `c-embedded-presolved` | available |
| 6 | Python objects for early evaluation/testing | `python` | available |

The C targets solve rand-field constraints with **dv-solve** — at runtime by
default, or at compile time (baked) with `--presolve` / the `*-presolved` targets.

## DV Flow integration

`pssc` ships a [DV Flow Manager](https://dv-flow.github.io/) task package
(always installed) so PSS compilation is a node in a DFM task graph — one build
task per output style, plus tasks that reference the bundled SV/C/C++ core
source. See [docs/dvflow-tasks.md](docs/dvflow-tasks.md).

## Documentation

- [docs/cli.md](docs/cli.md) — CLI reference
- [docs/dvflow-tasks.md](docs/dvflow-tasks.md) — DV Flow Manager task package
- [docs/architecture.md](docs/architecture.md) — compilation pipeline & IR hand-off
- [docs/targets.md](docs/targets.md) — per-target details
- [design/pssc-application-design.md](design/pssc-application-design.md) — design
- [design/pssc-implementation-plan.md](design/pssc-implementation-plan.md) — plan & status
