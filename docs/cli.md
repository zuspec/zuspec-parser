# pssc CLI reference

```
pssc [--version] <command> ...
```

Exit codes: `0` success · `1` user error (unknown target, parse/translate
failure) · `2` internal error.

## `pssc compile`

Compile PSS sources to a target.

```
pssc compile SOURCES... [-t TARGET] [-o DIR] [--dump-ir FILE] [-q] [target-opts]
```

| Option | Description |
|---|---|
| `SOURCES...` | one or more `.pss` files (parsed together) |
| `-t, --target` | target name (default `python`; see `pssc targets`) |
| `-o, --output-dir` | output directory, created if absent (default `.`) |
| `--dump-ir FILE` | also write the canonical IR `Context` as YAML to `FILE` |
| `-q, --quiet` | do not print written file paths |

Per-target options (contributed by each target's `add_args`):

| Target | Option | Description |
|---|---|---|
| `python` | `--emit {none,repr,pickle}` | on-disk artifact: none (in-memory only), `repr` (class-name manifest `pss_classes.txt`), `pickle` (`pss_classes.pkl`). Default `none`. |
| `sv` | `--projection {oo_api,harness}` | package shape: `oo_api` (export API + factory, default) or `harness` (standalone `zsp_test_top`). See [exported-actions-sv.md](exported-actions-sv.md) |
| `sv` | `--export-action NAME` | expose `NAME` on `export_api_if` (repeatable; default: auto-detected root) |
| `sv` | `--package-name NAME` | generated package name (default `zsp_gen_pkg`) |
| `sv` | `--no-rt-pkg` | do not emit the bundled `zsp_rt_pkg.sv` runtime package |
| `sv` | `--single-file` | emit one `zsp_pkg.sv` instead of one file per type |
| `sv-dpi-bridge` | `--export-action NAME` | action to expose as a DPI bridge entry point (repeatable; shared with `sv`) |
| `sv-dpi-bridge` | `--runtime-solve` | solve rand fields per-spawn from the seed (dv-solve linked into the `.so`); default bakes a constant |
| `sv-dpi-bridge` | *(imports)* | package-scope imports become a `pssc_import_if` the testbench implements + registers (`pssc_set_imports`): **solve** imports are synchronous `export "DPI-C"` functions; **target** imports are blocking SV **tasks** (may consume time) serviced via the request-mailbox + fork trampoline. Build the simulator with `-Wl,--export-dynamic` |
| `sv-progseq` | `--root COMP` | root component type to generate the API for (required) |
| `sv-progseq` | `--package NAME` | generated package name (default `<root>_pkg`) |
| *(all progseq)* | `--root COMP` | root component (shared by sv/c/cpp-progseq) |
| *(all progseq)* | `--no-core-copy` | do not copy the core seam header(s)/package |
| `c-progseq` | `--prefix NAME` | symbol/file prefix (default root sans `_c`) |
| `c-progseq` | `--link-style {vtable,direct,mmio}` | memory-access seam (default `vtable`) |
| `c-progseq` | `--reg-style {bitfields,accessors}` | register value layout (default `bitfields`) |
| `c-progseq` | `--header-only` | emit a single `.h` (forced for `mmio`) |
| `cpp-progseq` | `--namespace NAME` | namespace + class prefix (default root sans `_c`) |
| `cpp-progseq` | `--dispatch {virtual,template}` | dispatch model (default `virtual`) |

## `pssc parse`

Run the front end only (parse → translate); optionally dump the IR.

```
pssc parse SOURCES... [--dump-ir FILE] [-q]
```

Without `--dump-ir`, prints a one-line summary (`parsed OK: N types`). With
`--dump-ir FILE`, writes the canonical `zuspec.ir.core.Context` as YAML.

## `pssc targets`

List registered targets and their descriptions.

## `pssc sv-core-path`

Print the install path of the bundled SystemVerilog core package
(`pssc_reg_pkg`), used by the `sv-progseq` target. Useful for adding the core to
a build's compile order.

```
pssc sv-core-path [--file]
```

| Option | Description |
|---|---|
| (none) | print the directory (`.../pssc/share/sv`) |
| `--file` | print the path to `pssc_reg_pkg.sv` |

## `pssc c-core-path` / `pssc cpp-core-path`

Print the install path of the bundled C / C++ core seam headers, used by the
`c-progseq` / `cpp-progseq` targets.

```
pssc c-core-path   [--file [NAME]]      # default NAME: pssc_mem.h
pssc cpp-core-path [--file [NAME]]      # default NAME: pssc_reg.hpp
```

| Option | Description |
|---|---|
| (none) | print the directory (`.../pssc/share/c` or `.../pssc/share/cpp`) |
| `--file [NAME]` | print the path to a header (e.g. `--file pssc_mem_vtable.h`) |

## `pssc --version`

Print the pssc version and exit.

## Examples

```sh
pssc compile cpu.pss bus.pss -t sv -o gen/
pssc compile model.pss -t python --emit repr -o build/
pssc parse model.pss --dump-ir model.ir.yaml

# Generate a SystemVerilog programming API from a component tree
pssc compile dma_regs.pss dma_engine.pss -t sv-progseq --root dma_engine_c -o gen/
pssc sv-core-path --file        # locate pssc_reg_pkg.sv for the compile order
```
