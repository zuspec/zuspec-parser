"""The behavioural gate for the C++ COMPONENT TREE driver.

`test_cpp_op_model.py` says the generated text looks right and compiles. This
is the only test that says the C++ driver talks to the right registers, in the
right order, with the right values.

It runs the SAME five cases against the SAME mock as the C gate
(`test_op_model_behaviour_c.py`, `data/c/op_model_mock.c`), and that is the
point rather than an economy: the two backends project one model into two
languages, so if both are right they issue the same accesses. A case where they
differ is a defect in one of them, and this is what would find it.

**The gate is mutation-checked.** Rewriting the generated per-channel base to
drop the stride -- every channel pointing at bank 0 -- must not be survivable.
A gate that passes is only evidence if you know what makes it fail.
"""
import os
import shutil
import subprocess

import pytest

from .conftest import available_c_compilers, available_cpp_compilers
from .op_model import op_model_sources as _sources

_CXX = available_cpp_compilers()
_CC = available_c_compilers()
_HERE = os.path.dirname(__file__)
_C_TB_DIR = os.path.join(_HERE, "data", "c")
_CPP_TB_DIR = os.path.join(_HERE, "data", "cpp")

_CXXFLAGS = ["-std=c++17", "-Wall", "-Wextra", "-Werror"]
_CFLAGS = ["-std=c99", "-Wall", "-Wextra", "-Werror"]

#: Both toolchains, because the mock is C and the driver is C++.
needs_toolchain = pytest.mark.skipif(
    not (_CXX and _CC), reason="need both a C and a C++ compiler")


def _generate(out_dir, **kw):
    """Generate the C++ tree driver and stage the shared mock beside it."""
    import argparse
    from pssc import driver
    ns = argparse.Namespace(progseq_root="wb_dma_c", cpp_namespace="wb_dma",
                            cpp_dispatch="virtual", cpp_single_header=True,
                            progseq_core_copy=True, output_dir=str(out_dir),
                            **kw)
    res = driver.compile(_sources(), target="op-model-cpp", opts=ns)
    assert res.outputs, "op-model-cpp produced no files"
    for f in ("op_model_mock.h", "op_model_mock.c"):
        shutil.copy2(os.path.join(_C_TB_DIR, f), str(out_dir))
    shutil.copy2(os.path.join(_CPP_TB_DIR, "op_model_tb.cpp"), str(out_dir))
    return str(out_dir)


def _build_and_run(out, cxx, cc):
    """The mock compiles as C and the driver as C++, then they link.

    Compiling the mock as C++ would work and would be wrong: the C gate builds
    that file as C99, and a mock built two different ways is a mock that can
    behave two different ways.
    """
    obj = os.path.join(out, "op_model_mock.o")
    build_mock = subprocess.run(
        [cc, *_CFLAGS, "-I", out, "-c", os.path.join(out, "op_model_mock.c"),
         "-o", obj], capture_output=True, text=True)
    assert build_mock.returncode == 0, build_mock.stderr

    exe = os.path.join(out, "run")
    build = subprocess.run(
        [cxx, *_CXXFLAGS, "-I", out, os.path.join(out, "op_model_tb.cpp"), obj,
         "-o", exe], capture_output=True, text=True)
    assert build.returncode == 0, build.stderr
    return subprocess.run([exe], capture_output=True, text=True)


@pytest.mark.c_toolchain
@needs_toolchain
@pytest.mark.parametrize("cxx", _CXX)
def test_the_tree_driver_programs_the_right_registers(tmp_path, cxx):
    """Five cases, all trace-asserted -- see data/cpp/op_model_tb.cpp.

    On failure the whole access trace is printed and forwarded here, because a
    wrong offset is unreadable without it.
    """
    out = _generate(tmp_path)
    res = _build_and_run(out, cxx, _CC[0])
    assert res.returncode == 0, res.stdout + res.stderr
    assert "WB_DMA CPP OP MODEL PASS" in res.stdout, res.stdout


@pytest.mark.c_toolchain
@needs_toolchain
def test_the_gate_fails_when_the_per_channel_base_is_dropped(tmp_path):
    """The mutation check, run rather than described.

    The mutation is the exact defect a tree lowering has to avoid -- every
    sub-component constructed at the parent's base -- and it must not survive.
    """
    out = _generate(tmp_path)
    src = os.path.join(out, "wb_dma.hpp")
    text = open(src).read()
    mutant = "(0x20u + 0x20u * i)"
    assert mutant in text, \
        "the generated per-channel base changed shape; update this mutation"
    open(src, "w").write(text.replace(mutant, "(0x20u)"))

    res = _build_and_run(out, _CXX[0], _CC[0])
    assert res.returncode != 0, \
        "every channel pointed at bank 0 and the gate still passed"
    assert "channel banks overlap" in res.stdout, res.stdout


@pytest.mark.c_toolchain
@needs_toolchain
def test_the_gate_fails_when_the_masked_write_stops_reading(tmp_path):
    """§21.14.1 makes a masked write a read-modify-write, and the READ is part
    of the definition rather than an implementation detail: on a CSR that
    clears its status bits when read, dropping it changes what the device does.

    Mutated in the runtime rather than in the driver, because that is where the
    C++ backend puts it -- `pssc::reg::write_val_masked` is one method covering
    all four LRM spellings, so this is the single place it could be lost.
    """
    out = _generate(tmp_path)
    src = os.path.join(out, "pssc_reg.hpp")
    text = open(src).read()
    mutant = "write_val(static_cast<raw_t>((read_val() & ~mask) | (val & mask)));"
    assert mutant in text, \
        "the masked-write body changed shape; update this mutation"
    open(src, "w").write(
        text.replace(mutant, "write_val(static_cast<raw_t>(val & mask));"))

    res = _build_and_run(out, _CXX[0], _CC[0])
    assert res.returncode != 0, \
        "the masked write stopped reading and the gate still passed"
    assert "read-modify-write" in res.stdout, res.stdout
