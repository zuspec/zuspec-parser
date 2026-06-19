"""Phase 1: compile + run the hand-written C/C++ gold references.

These are the oracles the c-progseq / cpp-progseq generators must converge on
(design §7.5). Guarding them here means a change that breaks the reference --
or the toolchain assumptions -- is caught before the generator is blamed.

Marked `compile`; skipped cleanly where no host compiler is available.
"""
import os
import shutil
import subprocess

import pytest

from .conftest import (available_c_compilers, available_cpp_compilers,
                       C_CORE_DIR, CPP_CORE_DIR)

_HERE = os.path.dirname(__file__)
_C_PROTO = os.path.normpath(os.path.join(
    _HERE, "..", "..", "examples", "export", "programming_seqs", "c_proto"))
_CPP_PROTO = os.path.normpath(os.path.join(
    _HERE, "..", "..", "examples", "export", "programming_seqs", "cpp_proto"))

_CFLAGS = ["-std=c11", "-Wall", "-Wextra", "-Werror"]
_CXXFLAGS = ["-std=c++17", "-Wall", "-Wextra", "-Werror"]


def _run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


@pytest.mark.c_toolchain
@pytest.mark.parametrize("cc", available_c_compilers())
@pytest.mark.parametrize("link_style", ["vtable", "direct", "mmio"])
def test_c_proto_runs(tmp_path, cc, link_style):
    exe = str(tmp_path / "wb_dma_c")
    define = {"vtable": [], "direct": ["-DPSSC_LINK_DIRECT"],
              "mmio": ["-DPSSC_LINK_MMIO"]}[link_style]
    srcs = [os.path.join(_C_PROTO, "wb_dma.c")]
    if link_style == "mmio":
        srcs.append(os.path.join(_C_PROTO, "wb_dma_tb_mmio.c"))
    else:
        srcs += [os.path.join(_C_PROTO, "dma_mock.c"),
                 os.path.join(_C_PROTO, "wb_dma_tb.c")]
    build = _run([cc, *_CFLAGS, *define, "-I", C_CORE_DIR, "-I", _C_PROTO,
                  *srcs, "-o", exe])
    assert build.returncode == 0, build.stderr
    run = _run([exe])
    assert run.returncode == 0, run.stdout + run.stderr
    assert "WB_DMA PROTOTYPE PASS" in run.stdout


@pytest.mark.c_toolchain
@pytest.mark.parametrize("cxx", available_cpp_compilers())
def test_cpp_proto_runs(tmp_path, cxx):
    exe = str(tmp_path / "wb_dma_cpp")
    build = _run([cxx, *_CXXFLAGS, "-I", CPP_CORE_DIR, "-I", _CPP_PROTO,
                  os.path.join(_CPP_PROTO, "wb_dma_tb.cpp"), "-o", exe])
    assert build.returncode == 0, build.stderr
    run = _run([exe])
    assert run.returncode == 0, run.stdout + run.stderr
    assert "WB_DMA PROTOTYPE PASS" in run.stdout
