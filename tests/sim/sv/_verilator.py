"""Verilator build+run helper for the pure-SV (``sv-pure``) test path.

Verilator 5.04x supports SV classes, ``rand``/``constraint``/``randomize()``,
and (with ``--timing``) ``fork/join``, events, mailboxes and semaphores -- the
full surface the pure-SV lowering targets. This module gives tests a simple,
dependency-light way to compile (and optionally run) generated SV and assert on
the result, independent of the ``dv_flow``-based ``vsim``/``vcs`` harness in
``conftest.py``.

Typical use::

    from ._verilator import HAVE_VERILATOR, verilator_build_run
    rc, log = verilator_build_run(sv_dir, top_module="top")
    assert rc == 0, log
    assert "PASS" in log
"""
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import List, Optional, Tuple

VERILATOR = shutil.which("verilator")
HAVE_VERILATOR = VERILATOR is not None

# Warnings that are noise for generated constrained-random class code; we care
# about hard errors (syntax / elaboration / solve), not lint style.
_DEFAULT_WNO = (
    "WIDTH", "WIDTHEXPAND", "WIDTHTRUNC", "UNUSED", "UNUSEDSIGNAL",
    "UNUSEDPARAM", "CASEINCOMPLETE", "BLKANDNBLK", "MULTIDRIVEN",
    "UNOPTFLAT", "DECLFILENAME", "VARHIDDEN", "SYMRSVDWORD",
    # Verilator 5.049 added IMPLICITSTATIC, which fires on every
    # `my_class c = new();` declared in a static scope -- the ordinary shape of
    # a generated harness, and of hand-written golden SV. Verilator promotes
    # warnings to a non-zero exit, so without this every build here fails on a
    # lint note about initializer lifetime rather than on anything real.
    "IMPLICITSTATIC",
)


def verilator_build_run(
    sv_dir,
    top_module: str = "top",
    *,
    files: Optional[List[str]] = None,
    run: bool = True,
    extra_args: Optional[List[str]] = None,
    timeout: int = 300,
) -> Tuple[int, str]:
    """Compile (and optionally run) SV sources with Verilator.

    Args:
        sv_dir: Directory containing the ``.sv`` sources (and the build dir).
        top_module: Top-level module to elaborate.
        files: Explicit file list (relative to ``sv_dir``); defaults to all
            ``*.sv`` in ``sv_dir``, sorted.
        run: If True, run the built binary and append its output to the log.
        extra_args: Additional Verilator arguments.
        timeout: Per-subprocess timeout in seconds.

    Returns:
        ``(returncode, log)``. ``returncode == 0`` means build (and run, if
        requested) succeeded. On build failure the build log is returned with
        the non-zero compiler return code.
    """
    if not HAVE_VERILATOR:
        raise RuntimeError("verilator not found on PATH")

    sv_dir = Path(sv_dir)
    if files is not None:
        srcs = list(files)
    else:
        # Prefer the generated dependency-ordered filelist (zsp_rt_pkg before
        # zsp_gen_pkg before the top); fall back to a sorted glob.
        filelist = sv_dir / "zsp_filelist.f"
        if filelist.exists():
            srcs = [ln.strip() for ln in filelist.read_text().splitlines()
                    if ln.strip() and ln.strip().endswith(".sv")]
        else:
            srcs = sorted(p.name for p in sv_dir.glob("*.sv"))
    if not srcs:
        return (1, f"no .sv sources found in {sv_dir}")

    wno = [f"-Wno-{w}" for w in _DEFAULT_WNO]
    cmd = [
        VERILATOR, "--binary", "--timing", "--quiet",
        *wno,
        "--top-module", top_module,
        "-o", "sim",
        *(extra_args or []),
        *srcs,
    ]

    build = subprocess.run(
        cmd, cwd=str(sv_dir), capture_output=True, text=True, timeout=timeout)
    log = f"$ {' '.join(cmd)}\n{build.stdout}\n{build.stderr}"
    if build.returncode != 0:
        return (build.returncode, log)

    if not run:
        return (0, log)

    binary = sv_dir / "obj_dir" / "sim"
    if not binary.exists():
        return (1, log + f"\n[verilator] expected binary missing: {binary}")

    sim = subprocess.run(
        [str(binary)], cwd=str(sv_dir), capture_output=True, text=True,
        timeout=timeout)
    log += f"\n--- run ---\n{sim.stdout}\n{sim.stderr}"
    return (sim.returncode, log)
