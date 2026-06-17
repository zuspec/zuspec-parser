"""C (software) targets via ``zuspec-be-sw`` — Context-first, no ``zuspec-dataclasses``.

``c-host`` (output style 3): host-targeted C coroutine runtime. The translated PSS
IR ``Context`` is lowered (actions -> components, activities inlined) and handed to
``zuspec.be.sw.CGenerator.generate(ctx)``, which emits the C coroutine runtime.

A generated ``main.c`` harness instantiates the root action and drives its activity
to completion via the timebase. With ``--runtime-solve`` (PSS style 4), rand fields
are solved by **dv-solve at runtime** (each run seedable) instead of baked at
compile time (style 5).
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import List, Optional

from .base import Target
from .sw_lower import to_sw_context, find_root_action
from ..ir import to_core_context


def _sanitize(name: str) -> str:
    """Mirror zuspec-be-sw's ``sanitize_c_name`` (``pss_top::Root`` -> ``pss_top__Root``)."""
    return re.sub(r"[^a-zA-Z0-9_]", "_", name)


def _resolve_root(core, requested: Optional[str]) -> Optional[str]:
    """Resolve the root action to a qualified ``type_m`` key."""
    if requested:
        if requested in core.type_m:
            return requested
        matches = [k for k in core.type_m if k.split("::")[-1] == requested]
        return matches[0] if len(matches) == 1 else None
    return find_root_action(core)


def _plan_globals(plan):
    """Yield ``(global_name, var_id, entry_index)`` for every solved slot."""
    for i, entry in enumerate(plan):
        for slot in entry["slots"]:
            yield ("g_" + entry["prefix"] + slot.cname, slot.var_id, i)


def _root_harness(root_qual: str, runtime_solve: bool, with_main: bool = True) -> str:
    """Emit ``pssc_run(int seed)`` — instantiate ``root_qual`` and drive its
    activity — plus, when ``with_main``, a CLI ``main`` that calls it. The
    ``pssc_run`` entry is also the DPI boundary the sv-dpi facade calls."""
    t = _sanitize(root_qual)
    hdr = t.lower()
    pre = "#include <stdlib.h>\n#include <time.h>\n"
    if runtime_solve:
        pre += "extern void pssc_solve_all(unsigned long long seed);\n"
    solve_call = "    pssc_solve_all((unsigned long long)seed);\n" if runtime_solve else ""
    main = ""
    if with_main:
        main = """
int main(int argc, char **argv) {
    int seed = argc > 1 ? atoi(argv[1]) : (int)time(0);
    pssc_run(seed);
    return 0;
}
"""
    return f"""{pre}#include "zsp_alloc.h"
#include "zsp_init_ctxt.h"
#include "zsp_timebase.h"
#include "{hdr}.h"

void pssc_run(int seed) {{
    (void)seed;
{solve_call}    zsp_alloc_t alloc;
    zsp_alloc_malloc_init(&alloc);

    zsp_timebase_t tb;
    zsp_timebase_init(&tb, &alloc, ZSP_TIME_PS);

    zsp_init_ctxt_t ctxt;
    ctxt.alloc = &alloc;
    ctxt.timebase = &tb;

    {t} root;
    {t}_init(&ctxt, &root, "root", NULL);
    {t}_body(&root, &tb);
    zsp_timebase_run(&tb);
}}
{main}"""


def _sv_dpi_facade(seed: int = 1) -> str:
    """SV facade: import the c-host ``pssc_run`` entry via DPI and call it from a
    top module. (Style 2: SV testbench drives the C coroutine runtime.)"""
    return f"""// pssc-generated SV/DPI facade over the c-host C runtime.
package pssc_dpi_pkg;
  import "DPI-C" function void pssc_run(input int seed);
endpackage

module pssc_top;
  import pssc_dpi_pkg::*;
  initial begin
    pssc_run({seed});
    $finish;
  end
endmodule
"""


def _solve_c(plan) -> str:
    """The ``pssc_solve.c`` translation unit: includes only dv-solve headers (kept
    separate from the runtime headers, which carry a conflicting ``zsp_alloc.h``).
    Defines the solved-field globals and ``pssc_solve_all`` which solves each
    traversal's embedded problem with a per-run seed."""
    lines = [
        "#include <stdint.h>",
        "#include <string.h>",
        '#include "zsp_block_alloc.h"',
        '#include "zsp_problem.h"',
        '#include "zsp_ctx.h"',
        '#include "zsp_search.h"',
        "",
    ]
    for g, _vid, _i in _plan_globals(plan):
        lines.append(f"int32_t {g};")
    lines.append("")
    for i, entry in enumerate(plan):
        data = ",".join(str(x) for x in entry["bytes"])
        lines.append(f"static const unsigned char prob_{i}[] = {{{data}}};")
    lines += ["", "void pssc_solve_all(unsigned long long seed) {",
              "    static unsigned char cbuf[1<<20];"]
    for i, entry in enumerate(plan):
        lines.append("    {")
        lines.append("        zsp_block_alloc_t *ba = zsp_block_alloc_create(0, 1<<20);")
        lines.append("        SolveCtx *c = solver_create(cbuf, sizeof(cbuf), ba);")
        lines.append(f"        solver_compile(c, (SolveProblem*)prob_{i});")
        lines.append("        SolveOpts o; memset(&o, 0, sizeof(o));")
        lines.append(f"        o.seed = seed + {i}ull; o.fair_pick = 1;")
        lines.append("        solver_solve(c, &o);")
        for slot in entry["slots"]:
            g = "g_" + entry["prefix"] + slot.cname
            lines.append(f"        {g} = (int32_t)solver_get_value(c, {slot.var_id});")
        lines.append("        solver_destroy(c); zsp_block_alloc_destroy(ba);")
        lines.append("    }")
    lines += ["}", ""]
    return "\n".join(lines)


def _inject_externs(c_path: Path, plan) -> None:
    """Add ``extern`` decls for the solved-field globals to a generated .c file so
    the coroutine (which reads them) compiles."""
    externs = "\n".join(f"extern int32_t {g};" for g, _v, _i in _plan_globals(plan))
    if not externs:
        return
    text = c_path.read_text()
    lines = text.splitlines()
    last_inc = max((i for i, l in enumerate(lines) if l.startswith("#include")), default=-1)
    lines.insert(last_inc + 1, "#include <stdint.h>\n" + externs)
    c_path.write_text("\n".join(lines) + "\n")


class _CTarget(Target):
    """Shared C-coroutine codegen. Subclasses set the default solve mode; the
    host/embedded distinction is the runtime tier (future)."""

    #: When True, rand fields are solved by dv-solve at runtime (style 4); when
    #: False they are pre-solved at compile time and baked in (style 5).
    default_runtime_solve = False

    #: Emit a CLI ``main`` in the harness (False for the DPI entry, which SV calls).
    harness_with_main = True

    #: Also emit the SV/DPI facade (``pssc_top.sv``) over the C runtime.
    emit_sv_dpi = False

    def run(self, ctx, opts: argparse.Namespace) -> List[Path]:
        from zuspec.be.sw import CGenerator

        core = getattr(ctx, "ir_context", None)
        if core is None:
            core = to_core_context(ctx)

        # Per-target default, overridable either way on the CLI.
        runtime_solve = self.default_runtime_solve
        if getattr(opts, "runtime_solve", False):
            runtime_solve = True
        if getattr(opts, "presolve", False):
            runtime_solve = False
        solve_plan = [] if runtime_solve else None
        sw_ctx = to_sw_context(core, solve_plan=solve_plan)

        out = Path(str(getattr(opts, "output_dir", ".") or "."))
        out.mkdir(parents=True, exist_ok=True)
        files = list(CGenerator(output_dir=str(out)).generate(sw_ctx))

        root = _resolve_root(core, getattr(opts, "root_action", None))

        if runtime_solve and solve_plan:
            # separate solver TU + extern decls in the root coroutine .c
            solve_c = out / "pssc_solve.c"
            solve_c.write_text(_solve_c(solve_plan))
            files.append(solve_c)
            if root is not None:
                _inject_externs(out / (_sanitize(root).lower() + ".c"), solve_plan)

        if root is not None:
            main_c = out / "main.c"
            main_c.write_text(_root_harness(
                root, runtime_solve and bool(solve_plan), with_main=self.harness_with_main))
            if main_c not in files:
                files.append(main_c)
            if self.emit_sv_dpi:
                sv = out / "pssc_top.sv"
                sv.write_text(_sv_dpi_facade())
                files.append(sv)
        return files


class CHostTarget(_CTarget):
    name = "c-host"
    description = "Host C coroutine runtime, dv-solve runtime solving (style 3)"
    default_runtime_solve = True

    def add_args(self, parser: argparse.ArgumentParser) -> None:
        # The C targets share these options; only c-host registers them so the
        # single compile parser sees each option once.
        parser.add_argument(
            "--root-action", dest="root_action", metavar="NAME", default=None,
            help="C targets: action whose activity the generated main runs "
            "(simple or qualified name; default: auto-detect the single top action)",
        )
        parser.add_argument(
            "--runtime-solve", dest="runtime_solve", action="store_true", default=False,
            help="C targets: force dv-solve runtime solving",
        )
        parser.add_argument(
            "--presolve", dest="presolve", action="store_true", default=False,
            help="C targets: force compile-time pre-solving (bake constant values)",
        )


class CHostPresolvedTarget(_CTarget):
    name = "c-host-presolved"
    description = "Host C coroutine runtime, pre-solved constraints (style 3)"
    default_runtime_solve = False


class SvDpiTarget(_CTarget):
    name = "sv-dpi"
    description = "SV facade driving the c-host C runtime via DPI (style 2)"
    default_runtime_solve = True
    harness_with_main = False   # SV calls pssc_run via DPI instead of main()
    emit_sv_dpi = True


class CEmbeddedTarget(_CTarget):
    name = "c-embedded"
    description = "Embedded C coroutine runtime, dv-solve runtime solving (style 4)"
    default_runtime_solve = True


class CEmbeddedPresolvedTarget(_CTarget):
    name = "c-embedded-presolved"
    description = "Embedded C coroutine runtime, pre-solved constraints (style 5)"
    default_runtime_solve = False
