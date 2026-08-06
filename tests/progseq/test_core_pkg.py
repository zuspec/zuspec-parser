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


def test_reg_c_exposes_the_masked_write():
    """`write_val_masked` is the one primitive the four §21.14.1 spellings
    reduce to, so it is part of the frozen runtime ABI alongside read/write."""
    text = (sv_core_dir() / SV_CORE_PKG).read_text()
    assert "task write_val_masked(data_t mask, data_t val);" in text


def test_the_masked_write_actually_reads():
    """§21.14.1 defines the masked forms as read-modify-write.

    On this device the read is observable -- a channel CSR read clears its
    status and interrupt-source bits -- so an implementation that "optimised"
    the read away would silently change device behaviour. Pinned here because
    the mistake would look like a cleanup.
    """
    text = (sv_core_dir() / SV_CORE_PKG).read_text()
    body = text.split("task write_val_masked")[1].split("endtask")[0]
    assert "read_val(cur);" in body
    assert "(cur & ~mask) | (val & mask)" in body


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
