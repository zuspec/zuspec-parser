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
import shutil
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


# ---------------------------------------------------------------------------
# sv-dpi-bridge: multi-action C scenario driven from SV via the zsp_bridge DPI
# runtime (Backend B, Phase C1). See design/pssc-c-bridge-runtime-design.md and
# design/pssc-c1-impl-plan.md. No imports yet (C2+).
# ---------------------------------------------------------------------------

def _c_share_dir() -> Path:
    """pssc's C seam directory (ships zsp_bridge.{h,c})."""
    return Path(__file__).resolve().parents[1] / "share" / "c"


def _besw_share() -> tuple:
    """(include_dir, rt_dir) of the zuspec-be-sw runtime."""
    from zuspec.be import sw as _sw
    base = Path(_sw.__file__).parent / "share"
    return base / "include", base / "rt"


def _dvsolve_share() -> tuple:
    """(include_dir, lib_dir) for dv-solve (runtime constraint solving)."""
    import dv_solve as _dv  # the installed package, if present
    root = Path(_dv.__file__).resolve().parents[2]
    return root / "src" / "c", root / "build"


def _resolve_actions(core, opts) -> List[dict]:
    """Resolve the export-action set to ``[{id, short, ctype, header}]``.

    Uses ``--export-action`` names when given, else the auto-detected single
    root. ``ctype`` is the sanitized C type (``pss_top__Entry``); ``header`` is
    its lowercased ``.h``; ``short`` is the unqualified action name.
    """
    names = getattr(opts, "export_actions", None)
    quals: List[str] = []
    if names:
        for n in names:
            q = _resolve_root(core, n)
            if q is None:
                raise ValueError(f"sv-dpi-bridge: cannot resolve export action '{n}'")
            quals.append(q)
    else:
        q = find_root_action(core)
        if q is None:
            raise ValueError(
                "sv-dpi-bridge: no export actions; pass --export-action NAME")
        quals.append(q)

    actions = []
    for i, q in enumerate(quals):
        ctype = _sanitize(q)
        actions.append({
            "id": i,
            "short": q.split("::")[-1],
            "ctype": ctype,
            "header": ctype.lower() + ".h",
            "dt": core.type_m.get(q),   # IR dtype, for presolving rand fields
        })
    return actions


def _field_assigns(a: dict, var: str, runtime: bool) -> List[str]:
    """C assignments that set a spawned action's own ``rand`` fields between
    ``_init`` and ``_body``: a runtime-solved global (``root.x = g_Entry__x;``)
    when ``runtime``, else a baked constant (``root.x = 4;``).

    Covers top-level scalar rand fields (the common atomic-action case); deeper
    paths / arrays are left to the activity-inlining solve path. Non-rand fields
    keep the ``_init`` default of 0.
    """
    dt = a.get("dt")
    if dt is None:
        return []
    from .sw_lower import _field_locals, solve_global_name
    out: List[str] = []
    if runtime:
        solve = a.get("solve") or {}
        prefix = solve.get("prefix", "")
        slot_cnames = {s.cname for s in solve.get("slots", [])}
        for fld in getattr(dt, "fields", []):
            for cname, path, _edt in _field_locals(fld):
                if len(path) == 1 and cname in slot_cnames:
                    out.append(f"        {var}.{path[0]} = {solve_global_name(prefix, cname)};")
        return out
    try:
        from .sw_solve import solve_action, seed_for
        solved = solve_action(dt, seed=seed_for(getattr(dt, "name", "") or ""))
    except Exception:
        return []
    for fld in getattr(dt, "fields", []):
        for cname, path, _edt in _field_locals(fld):
            if len(path) == 1 and cname in solved:
                out.append(f"        {var}.{path[0]} = {int(solved[cname])};")
    return out


def _bridge_dispatch_c(actions: List[dict], runtime: bool) -> str:
    """The generated ``pssc_bridge_dispatch.c``: ACTION_* ids + spawn switch.

    Each case instantiates the action's root coroutine in **static** storage (it
    must outlive ``spawn`` until ``run`` drains it -- one active instance per
    action, the documented serial contract), injects its solved rand fields, and
    posts its ``_body`` onto the bridge timebase. When ``runtime``, the per-spawn
    ``seed`` drives ``pssc_solve_all`` (dv-solve) into the ``g_*`` globals.
    """
    from .sw_lower import solve_global_name
    L = ['#include "zsp_bridge.h"', "#include <stdint.h>"]
    for a in actions:
        L.append(f'#include "{a["header"]}"')
    if runtime:
        L.append("extern void pssc_solve_all(unsigned long long seed);")
        for a in actions:
            solve = a.get("solve") or {}
            for s in solve.get("slots", []):
                L.append(f'extern int32_t {solve_global_name(solve["prefix"], s.cname)};')
    L.append("")
    for a in actions:
        L.append(f'#define ACTION_{a["short"]} {a["id"]}')
    L.append("")
    L.append("void pssc_bridge_dispatch(zsp_bridge_t *b, int action_id, long long seed) {")
    if runtime:
        L.append("    pssc_solve_all((unsigned long long)seed);")
    else:
        L.append("    (void)seed;")
    L.append("    switch (action_id) {")
    for a in actions:
        ct = a["ctype"]
        L.append(f'    case ACTION_{a["short"]}: {{')
        L.append(f"        static {ct} root;")
        L.append(f'        {ct}_init(&b->ctxt, &root, "root", NULL);')
        L.extend(_field_assigns(a, "root", runtime))
        L.append(f"        {ct}_body(&root, &b->tb);")
        L.append("        break;")
        L.append("    }")
    L.append("    default: break;")
    L.append("    }")
    L.append("}")
    return "\n".join(L) + "\n"


def _bridge_pkg_sv(actions: List[dict]) -> str:
    """``pssc_bridge_pkg.sv``: DPI decls, ACTION_* localparams, and a
    ``pssc_run_action`` trampoline task (spawn -> run -> drain to done)."""
    L = ["// pssc-generated bridge package (sv-dpi-bridge).",
         "package pssc_bridge_pkg;",
         '  import "DPI-C" function chandle zsp_bridge_create();',
         '  import "DPI-C" function void    zsp_bridge_destroy(chandle b);',
         '  import "DPI-C" function void    zsp_bridge_spawn(chandle b, int action_id, longint seed);',
         '  import "DPI-C" function void    zsp_bridge_run(chandle b);',
         '  import "DPI-C" function int     zsp_bridge_done(chandle b);',
         ""]
    for a in actions:
        L.append(f'  localparam int ACTION_{a["short"]} = {a["id"]};')
    L += [
        "",
        "  // Spawn one action and drive the C scheduler to completion.",
        "  task automatic pssc_run_action(chandle b, int action_id, longint seed);",
        "    zsp_bridge_spawn(b, action_id, seed);",
        "    zsp_bridge_run(b);",
        "    while (zsp_bridge_done(b) == 0) zsp_bridge_run(b);",
        "  endtask",
        "",
        "  // As above, but draw the C-side seed from the calling process's random",
        "  // state ($urandom is the thread PRNG, reproducible under the testbench",
        "  // seed). The C side uses it for runtime constraint solving.",
        "  task automatic pssc_run_action_rand(chandle b, int action_id);",
        "    pssc_run_action(b, action_id, {$urandom(), $urandom()});",
        "  endtask",
        "endpackage",
    ]
    return "\n".join(L) + "\n"


class SvDpiBridgeTarget(Target):
    name = "sv-dpi-bridge"
    description = ("Multi-action C scenario as a DPI shared lib (libpssc_scenario.so) "
                  "driven from SV via the zsp_bridge runtime (Phase C1)")

    # `--export-action` is the shared compile-level option (see cli.build_parser).

    def run(self, ctx, opts: argparse.Namespace) -> List[Path]:
        import subprocess
        from zuspec.be.sw import CGenerator

        core = getattr(ctx, "ir_context", None) or to_core_context(ctx)
        actions = _resolve_actions(core, opts)
        runtime = bool(getattr(opts, "runtime_solve", False))

        out = Path(str(getattr(opts, "output_dir", ".") or "."))
        out.mkdir(parents=True, exist_ok=True)

        # Generate the C scenario (the body coroutines; rand fields are injected
        # by the dispatcher -- baked (presolve) or solved per-spawn (runtime)).
        sw_ctx = to_sw_context(core, solve_plan=None)
        gen = list(CGenerator(output_dir=str(out)).generate(sw_ctx))

        # Runtime-solve: a per-action dv-solve problem -> pssc_solve.c (separate
        # TU: dv-solve headers must not co-occur with the runtime's zsp_alloc.h).
        if runtime:
            from .sw_solve import problem_bytes
            plan = []
            for a in actions:
                pb, slots = problem_bytes(a["dt"]) if a.get("dt") is not None else (None, [])
                if pb is not None and slots:
                    a["solve"] = {"prefix": a["short"] + "__", "slots": slots}
                    plan.append({"prefix": a["solve"]["prefix"], "bytes": pb, "slots": slots})
            if plan:
                (out / "pssc_solve.c").write_text(_solve_c(plan))

        # Bridge runtime (copied) + generated dispatcher + SV shim.
        share_c = _c_share_dir()
        for fn in ("zsp_bridge.h", "zsp_bridge.c"):
            (out / fn).write_text((share_c / fn).read_text())
        (out / "pssc_bridge_dispatch.c").write_text(_bridge_dispatch_c(actions, runtime))
        (out / "pssc_bridge_pkg.sv").write_text(_bridge_pkg_sv(actions))

        written = list(gen) + [
            out / "zsp_bridge.h", out / "zsp_bridge.c",
            out / "pssc_bridge_dispatch.c", out / "pssc_bridge_pkg.sv",
        ]
        if runtime and (out / "pssc_solve.c").exists():
            written.append(out / "pssc_solve.c")

        # Build libpssc_scenario.so when a compiler is available.
        if shutil.which("gcc"):
            inc, rt = _besw_share()
            objs: List[str] = []
            link_extra: List[str] = []
            # Separate TU for the dv-solve solver (own include path).
            if runtime and (out / "pssc_solve.c").exists():
                dv_inc, dv_lib = _dvsolve_share()
                solve_o = out / "pssc_solve.o"
                rs = subprocess.run(
                    ["gcc", "-w", "-c", "-fPIC", f"-I{dv_inc}",
                     str(out / "pssc_solve.c"), "-o", str(solve_o)],
                    capture_output=True, text=True)
                if rs.returncode != 0:
                    raise RuntimeError(f"pssc_solve.c build failed:\n{rs.stderr}")
                objs.append(str(solve_o))
                link_extra = [f"-L{dv_lib}", "-ldv_solve", f"-Wl,-rpath,{dv_lib}"]

            srcs = [str(f) for f in gen if f.suffix == ".c" and f.name != "main.c"]
            srcs += [str(out / "zsp_bridge.c"), str(out / "pssc_bridge_dispatch.c")]
            srcs += [str(p) for p in rt.glob("*.c")]
            lib = out / "libpssc_scenario.so"
            cmd = ["gcc", "-w", "-fPIC", "-shared",
                   f"-I{inc}", f"-I{share_c}", f"-I{out}", *srcs, *objs,
                   "-o", str(lib), *link_extra]
            r = subprocess.run(cmd, capture_output=True, text=True)
            if r.returncode != 0:
                raise RuntimeError(f"libpssc_scenario.so build failed:\n{r.stderr}")
            written.append(lib)

        return written


class CEmbeddedTarget(_CTarget):
    name = "c-embedded"
    description = "Embedded C coroutine runtime, dv-solve runtime solving (style 4)"
    default_runtime_solve = True


class CEmbeddedPresolvedTarget(_CTarget):
    name = "c-embedded-presolved"
    description = "Embedded C coroutine runtime, pre-solved constraints (style 5)"
    default_runtime_solve = False
