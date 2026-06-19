"""Phase 5: the C behavioral gate -- generate, compile with a host C compiler,
run, assert WB_DMA PROTOTYPE PASS. Mirrors the SV Verilator gate.
"""
import os
import subprocess

import pytest

from .conftest import available_c_compilers, generate_c_wb_dma

_CFLAGS = ["-std=c11", "-Wall", "-Wextra", "-Werror"]


def _run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


@pytest.mark.c_toolchain
@pytest.mark.parametrize("cc", available_c_compilers())
@pytest.mark.parametrize("link_style", ["vtable", "direct", "mmio"])
def test_build_and_run(tmp_path, cc, link_style):
    out = generate_c_wb_dma(tmp_path, link_style=link_style)
    define = {"vtable": [], "direct": ["-DPSSC_LINK_DIRECT"],
              "mmio": ["-DPSSC_LINK_MMIO"]}[link_style]
    if link_style == "mmio":
        srcs = [os.path.join(out, "wb_dma_tb_mmio.c")]
    else:
        srcs = [os.path.join(out, "wb_dma.c"), os.path.join(out, "dma_mock.c"),
                os.path.join(out, "wb_dma_tb.c")]
    exe = os.path.join(out, "run")
    build = _run([cc, *_CFLAGS, *define, "-I", out, *srcs, "-o", exe])
    assert build.returncode == 0, build.stderr
    res = _run([exe])
    assert res.returncode == 0, res.stdout + res.stderr
    assert "WB_DMA PROTOTYPE PASS" in res.stdout

@pytest.mark.c_toolchain
@pytest.mark.skipif(not available_c_compilers(), reason="no C compiler")
def test_reg_style_accessors_compiles(tmp_path):
    """The layout-independent --reg-style accessors path compiles -Werror-clean.

    Its operation bodies are the same flow as the bitfields path (which is
    behaviorally gated across all link styles + compilers) -- only register
    field access differs (``<type>_<FIELD>_set/_get`` vs. ``csr.FIELD``)."""
    out = generate_c_wb_dma(tmp_path, link_style="vtable", reg_style="accessors")
    cc = available_c_compilers()[0]
    obj = os.path.join(out, "wb_dma.o")
    build = _run([cc, *_CFLAGS, "-I", out, "-c", os.path.join(out, "wb_dma.c"),
                  "-o", obj])
    assert build.returncode == 0, build.stderr
