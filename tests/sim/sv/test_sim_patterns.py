"""VCS simulation smoke-tests for all PSS test patterns.

For each pattern in tests/patterns/, this test:
  1. Calls generate_sv_files() to produce the SV package
  2. Writes a minimal top module that instantiates the component and
     traverses the root action (do_test when present, else first action)
  3. Compiles with VCS
  4. Runs the simulation and asserts "TEST PASSED" in the output

Requires VCS in PATH (provided via direnv exec . in this project).
Tests are marked @pytest.mark.sim so they can be skipped without a simulator.
"""
from __future__ import annotations

import os
import pathlib
import subprocess
import tempfile
import textwrap
from typing import List, Optional, Tuple

import pytest

from pssc import Parser, AstToIrTranslator, generate_sv_files
from zuspec.dataclasses import ir as pss_ir

# ---------------------------------------------------------------------------
pytestmark = pytest.mark.sim

# ---------------------------------------------------------------------------
# Known limitations that cause specific patterns to fail at sim time.
# See tests/patterns/KNOWN_LIMITATIONS.md for details.
# Map pattern stem -> (limitation_id, short reason)
# ---------------------------------------------------------------------------
_KNOWN_FAILURES: dict = {}

_REPO_ROOT   = pathlib.Path(__file__).parents[5]
_PATTERNS_DIR = _REPO_ROOT / "packages" / "zuspec-fe-pss" / "tests" / "patterns"

# ---------------------------------------------------------------------------
# Discover patterns
# ---------------------------------------------------------------------------
_PATTERN_FILES: List[pathlib.Path] = sorted(_PATTERNS_DIR.glob("*.pss"))
assert _PATTERN_FILES, f"No .pss files in {_PATTERNS_DIR}"


def _find_root_action(pss_file: pathlib.Path):
    """Parse the PSS file and return (comp_type, root_action_type, ir_ctx).

    Looks for 'do_test' first, then falls back to the first action on pss_top.
    """
    p = Parser()
    p.parse([str(pss_file)])
    ast = p.link()
    ir_ctx = AstToIrTranslator().translate(ast, annotations=p.annotations)
    comp_type = "pss_top"
    # Collect actions on pss_top
    top_actions = []
    for qname, dtype in ir_ctx.type_map.items():
        if not isinstance(dtype, pss_ir.DataTypeClass):
            continue
        parent = ir_ctx.parent_comp_names.get(qname, "")
        if "pss_top" not in parent:
            continue
        local = qname.split("::")[-1]
        top_actions.append(local)
    if "do_test" in top_actions:
        return comp_type, "do_test", ir_ctx
    if top_actions:
        return comp_type, top_actions[0], ir_ctx
    raise ValueError(f"No actions found on pss_top in {pss_file.name}")


def _write_top(outdir: pathlib.Path, comp_type: str, root_action: str, has_rand_fields: bool = True) -> pathlib.Path:
    """Write a minimal SV top module."""
    sv_name_comp   = comp_type.replace("::", "__")
    sv_name_action = f"{sv_name_comp}__{root_action}"
    top_sv = textwrap.dedent(f"""\
        `timescale 1ns/1ps
        module zsp_test_top;
          import zsp_rt_pkg::*;
          import zsp_gen_pkg::*;

          initial begin
            {sv_name_comp}  comp;
            {sv_name_action} root;
            comp = new("top", null);
            root = new();
            root.comp = comp;
            root.pre_solve();
            {("if (!root.randomize()) $fatal(1, \"randomize failed\");" if has_rand_fields else "// compound action: no direct rand fields — skip randomize")}
            root.post_solve();
            root.body();
            $display("TEST PASSED");
            $finish;
          end
        endmodule
    """)
    top_path = outdir / "zsp_test_top.sv"
    top_path.write_text(top_sv)
    return top_path


def _vcs_compile(sv_files: List[pathlib.Path], simv: pathlib.Path) -> Tuple[bool, str]:
    """Compile sv_files with VCS. Returns (success, log)."""
    cmd = [
        "vcs", "-full64", "-sverilog", "-timescale=1ns/1ps",
        *[str(f) for f in sv_files],
        "-o", str(simv),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    log = result.stdout + result.stderr
    return result.returncode == 0, log


def _vcs_run(simv: pathlib.Path) -> Tuple[bool, str]:
    """Run a VCS simv. Returns (passed, log)."""
    result = subprocess.run(
        [str(simv), "-no_save"],
        capture_output=True, text=True, timeout=60,
    )
    log = result.stdout + result.stderr
    passed = "TEST PASSED" in log
    return passed, log


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    "pss_file",
    _PATTERN_FILES,
    ids=[f.stem for f in _PATTERN_FILES],
)
def test_pattern_simulates(pss_file: pathlib.Path, tmp_path: pathlib.Path):
    """Generate SV, compile with VCS, simulate, assert TEST PASSED."""
    stem = pss_file.stem
    if stem in _KNOWN_FAILURES:
        lim_id, reason = _KNOWN_FAILURES[stem]
        pytest.xfail(f"Known limitation {lim_id}: {reason} "
                     f"(see tests/patterns/KNOWN_LIMITATIONS.md)")

    # Generate SV
    gen_files = generate_sv_files([str(pss_file)], output_dir=str(tmp_path))
    sv_files   = [f for f in gen_files if f.suffix == ".sv"]

    # Discover root action
    try:
        comp_type, root_action, ir_ctx = _find_root_action(pss_file)
    except Exception as exc:
        pytest.skip(f"Could not determine root action: {exc}")

    # Write top
    # Check if root action has direct rand fields
    from zuspec.ir.core.fields import FieldKind as _FK
    root_dtype = ir_ctx.type_map.get(f"{comp_type}::{root_action}")
    _has_rand = root_dtype is not None and any(
        f.rand_kind == "rand" for f in getattr(root_dtype, "fields", [])
    )
    top_path = _write_top(tmp_path, comp_type, root_action, has_rand_fields=_has_rand)
    sv_files.append(top_path)

    # Compile
    simv = tmp_path / "simv"
    ok, log = _vcs_compile(sv_files, simv)
    assert ok, f"VCS compile failed for {pss_file.name}:\n{log[-2000:]}"

    # Simulate
    passed, log = _vcs_run(simv)
    assert passed, f"Simulation did not produce TEST PASSED for {pss_file.name}:\n{log[-1000:]}"
