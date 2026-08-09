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
| `--target-cfg NAME=VALUE` | override what the target publishes as `target_cfg_pkg` (repeatable; see below) |

### `target_cfg_pkg` — the target describes itself to the model

Every target may inject PSS source that is processed **before** the user's
sources. The built-in use is `target_cfg_pkg`, which answers questions about the
execution target that a portable model has to branch on:

```pss
package target_cfg_pkg {
    static const int  TARGET_CFG_VERSION  = 1;
    static const bool HAVE_BLOCKING       = true;   // can the runtime suspend a thread?
    static const bool HAVE_RUNTIME_SOLVER = true;   // solver in the image, or pre-solved?
}
```

`pssc targets` prints what each target publishes. `op-model-sv` claims both
(generated operations are `task`s, and SV carries a solver); `op-model-c` and
`op-model-cpp` claim neither (plain functions, no coroutine runtime). A target
that has not established its capabilities publishes nothing, and the model takes
its own defaults.

A model reads it by testing the version marker first, then the flag — **nested,
not `&&`**:

```pss
package target_cfg_pkg { }          // stub, so the name resolves

package my_cfg_pkg {
    compile if (compile has(target_cfg_pkg::TARGET_CFG_VERSION)) {
        static const bool HAS_BLOCKING = target_cfg_pkg::HAVE_BLOCKING;
    } else {
        static const bool HAS_BLOCKING = true;      // default: the richer model
    }
}
```

`compile has(V) && target_cfg_pkg::HAVE_BLOCKING` — the shape in the LRM's
Example275 — is a hard error: pssparser evaluates both operands of a
compile-time binary expression eagerly. Short-circuiting is normative (§8.4.4)
but governs evaluation, not name resolution. Nesting sidesteps it.

A provider that declares `TARGET_CFG_VERSION = N` declares **every** constant in
version N; that obligation is what lets a model reference the flags directly
instead of guarding each one, and it is enforced rather than defaulted.

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
| `op-model-sv` | `--root COMP` | root component type to generate the API for (required) |
| `op-model-sv` | `--package NAME` | generated package name (default `<root>_pkg`) |
| *(all op-model)* | `--root COMP` | root component (shared by `op-model-sv` / `-c` / `-cpp`) |
| *(all op-model)* | `--no-core-copy` | do not copy the core seam header(s)/package |
| `op-model-c` | `--prefix NAME` | symbol/file prefix (default root sans `_c`) |
| `op-model-c` | `--link-style {vtable,direct,mmio}` | memory-access seam (default `vtable`) |
| `op-model-c` | `--reg-style {bitfields,accessors}` | register value layout (default `bitfields`) |
| `op-model-c` | `--header-only` | emit a single `.h` (forced for `mmio`) |
| `op-model-cpp` | `--namespace NAME` | namespace + class prefix (default root sans `_c`) |
| `op-model-cpp` | `--dispatch {virtual,template}` | dispatch model (default `virtual`) |

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
(`pssc_reg_pkg`), used by the `op-model-sv` target. Useful for adding the core to
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
`op-model-c` / `op-model-cpp` targets.

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
pssc compile dma_regs.pss dma_engine.pss -t op-model-sv --root dma_engine_c -o gen/
pssc sv-core-path --file        # locate pssc_reg_pkg.sv for the compile order
```
