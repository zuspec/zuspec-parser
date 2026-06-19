"""Phase 1 tests: the bundled SV core package and the `sv-core-path` subcommand.

Pure-Python (no simulator). Validates that pssc ships `pssc_reg_pkg.sv` and that
the locator subcommand resolves to it cleanly (no stray stdout).
"""
import subprocess
import sys

from pssc.cli import sv_core_dir, SV_CORE_PKG


def test_sv_core_dir_resolves():
    d = sv_core_dir()
    assert d.is_dir(), f"core SV dir missing: {d}"
    assert (d / SV_CORE_PKG).is_file(), f"core package missing: {d / SV_CORE_PKG}"


def test_core_pkg_contents():
    text = (sv_core_dir() / SV_CORE_PKG).read_text()
    # The frozen runtime ABI (design §5).
    assert "package pssc_reg_pkg;" in text
    assert "interface class pss_mem_if;" in text
    assert "typedef bit [63:0] addr_handle_t;" in text
    assert "class reg_c #(" in text
    # task-based bus (not function-based), 8/16/32/64 primitives.
    for prim in ("write8", "read8", "write16", "read16",
                 "write32", "read32", "write64", "read64"):
        assert f"task {prim} " in text or f"task {prim}(" in text, prim


def _run_cli(*args):
    out = subprocess.run(
        [sys.executable, "-m", "pssc.cli", *args],
        capture_output=True, text=True, check=True,
    )
    return out.stdout


def test_sv_core_path_cli_dir():
    out = _run_cli("sv-core-path").strip()
    # Exactly one clean line that points at the shipped directory.
    assert out.endswith("share/sv"), repr(out)
    assert "\n" not in out, f"unexpected extra stdout: {out!r}"


def test_sv_core_path_cli_file():
    out = _run_cli("sv-core-path", "--file").strip()
    assert out.endswith(SV_CORE_PKG), repr(out)
    assert "\n" not in out, f"unexpected extra stdout: {out!r}"
