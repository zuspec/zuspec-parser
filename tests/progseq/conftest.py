"""Shared fixtures for sv-progseq tests.

Provides simulator discovery and a fixture that runs the sv-progseq target on
the WB DMA model and stages a self-contained compile dir (core + generated +
testbench).
"""
import argparse
import os
import shutil

import pytest

_HERE = os.path.dirname(__file__)
_EXAMPLE = os.path.join(_HERE, "..", "..", "examples", "export", "programming_seqs")
_SRCS = [os.path.join(_EXAMPLE, "dma_regs.pss"),
         os.path.join(_EXAMPLE, "dma_engine.pss")]
_TB = os.path.join(_HERE, "data", "wb_dma_tb.sv")


def available_sims():
    """Simulator short-tags whose executable is on PATH (libhdlsim naming)."""
    sims = []
    for exe, tag in {"verilator": "vlt", "vsim": "mti", "vcs": "vcs",
                     "xsim": "xsm", "xmvlog": "xcm", "iverilog": "ivl"}.items():
        if shutil.which(exe):
            sims.append(tag)
    return sims


# --- C / C++ host-compiler discovery (the progseq C/C++ behavioral gate) ----

def available_c_compilers():
    """C compilers on PATH (the c-progseq compile-and-run gate)."""
    return [cc for cc in ("gcc", "clang", "cc") if shutil.which(cc)]


def available_cpp_compilers():
    """C++ compilers on PATH (the cpp-progseq compile-and-run gate)."""
    return [cxx for cxx in ("g++", "clang++", "c++") if shutil.which(cxx)]


#: Shipped core seam header directories (also returned by `pssc c-core-path`).
C_CORE_DIR = os.path.normpath(os.path.join(
    _HERE, "..", "..", "src", "pssc", "share", "c"))
CPP_CORE_DIR = os.path.normpath(os.path.join(
    _HERE, "..", "..", "src", "pssc", "share", "cpp"))


def generate_wb_dma(out_dir, package="wb_dma_pkg", root="dma_engine_c"):
    """Run the sv-progseq target into ``out_dir`` and stage the testbench.

    Returns the directory (containing pssc_reg_pkg.sv, <package>.sv, wb_dma_tb.sv).
    """
    from pssc import driver
    ns = argparse.Namespace(progseq_root=root, progseq_package=package,
                            output_dir=str(out_dir))
    res = driver.compile(_SRCS, target="sv-progseq", opts=ns)
    assert res.outputs, "sv-progseq produced no files"
    shutil.copy2(_TB, os.path.join(str(out_dir), "wb_dma_tb.sv"))
    return str(out_dir)


@pytest.fixture(scope="module")
def wb_dma_build(tmp_path_factory):
    out = tmp_path_factory.mktemp("wb_dma_gen")
    return generate_wb_dma(out)


#: TB-only sources (mock bus + self-check) for the generated C driver.
_C_TB_DIR = os.path.join(_HERE, "data", "c")


def generate_c_wb_dma(out_dir, link_style="vtable", reg_style="bitfields",
                      root="dma_engine_c"):
    """Run the c-progseq target into ``out_dir`` (prefix wb_dma) and stage the
    matching testbench + mock. Returns the directory."""
    import argparse
    from pssc import driver
    ns = argparse.Namespace(progseq_root=root, c_prefix="wb_dma",
                            c_link_style=link_style, c_reg_style=reg_style,
                            c_header_only=False, progseq_core_copy=True,
                            output_dir=str(out_dir))
    res = driver.compile(_SRCS, target="c-progseq", opts=ns)
    assert res.outputs, "c-progseq produced no files"
    out = str(out_dir)
    if link_style == "mmio":
        shutil.copy2(os.path.join(_C_TB_DIR, "wb_dma_tb_mmio.c"), out)
    else:
        for f in ("dma_mock.h", "dma_mock.c", "wb_dma_tb.c"):
            shutil.copy2(os.path.join(_C_TB_DIR, f), out)
    return out


#: TB-only source (mock bus + self-check) for the generated C++ driver.
_CPP_TB_DIR = os.path.join(_HERE, "data", "cpp")


def generate_cpp_wb_dma(out_dir, dispatch="virtual", root="dma_engine_c"):
    """Run the cpp-progseq target into ``out_dir`` (namespace wb_dma) and stage
    the testbench. Returns the directory."""
    import argparse
    from pssc import driver
    ns = argparse.Namespace(progseq_root=root, cpp_namespace="wb_dma",
                            cpp_dispatch=dispatch, cpp_single_header=True,
                            progseq_core_copy=True, output_dir=str(out_dir))
    res = driver.compile(_SRCS, target="cpp-progseq", opts=ns)
    assert res.outputs, "cpp-progseq produced no files"
    shutil.copy2(os.path.join(_CPP_TB_DIR, "wb_dma_tb.cpp"), str(out_dir))
    return str(out_dir)
