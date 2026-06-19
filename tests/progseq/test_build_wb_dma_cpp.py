"""Phase 7: the C++ behavioral gate -- generate, compile with a host C++
compiler, run, assert WB_DMA PROTOTYPE PASS.
"""
import os
import subprocess

import pytest

from .conftest import available_cpp_compilers, generate_cpp_wb_dma

_CXXFLAGS = ["-std=c++17", "-Wall", "-Wextra", "-Werror"]


def _run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


@pytest.mark.c_toolchain
@pytest.mark.parametrize("cxx", available_cpp_compilers())
def test_build_and_run(tmp_path, cxx):
    out = generate_cpp_wb_dma(tmp_path, dispatch="virtual")
    exe = os.path.join(out, "run")
    build = _run([cxx, *_CXXFLAGS, "-I", out,
                  os.path.join(out, "wb_dma_tb.cpp"), "-o", exe])
    assert build.returncode == 0, build.stderr
    res = _run([exe])
    assert res.returncode == 0, res.stdout + res.stderr
    assert "WB_DMA PROTOTYPE PASS" in res.stdout
