"""Phase 2: the shipped C/C++ core seam headers + their locator subcommands.

Pure-Python presence/locator checks plus a -fsyntax-only compile of each header
where a host compiler is available (the c_toolchain gate).
"""
import os
import shutil
import subprocess

import pytest

from pssc.cli import (c_core_dir, cpp_core_dir, main as cli_main,
                      C_CORE_HEADER, CPP_CORE_HEADER)

_C_HEADERS = ["pssc_mem.h", "pssc_mem_vtable.h", "pssc_mem_direct.h", "pssc_mem_mmio.h"]


def test_c_core_dir_exists():
    d = c_core_dir()
    assert d.is_dir()
    for h in _C_HEADERS:
        assert (d / h).is_file(), h
    txt = (d / "pssc_mem_vtable.h").read_text()
    assert "pssc_mem_if" in txt and "pssc_w32" in txt


def test_cpp_core_dir_exists():
    d = cpp_core_dir()
    assert d.is_dir()
    assert (d / CPP_CORE_HEADER).is_file()
    txt = (d / CPP_CORE_HEADER).read_text()
    for sym in ("namespace pssc", "struct mem_if", "class reg", "struct mmio_mem"):
        assert sym in txt, sym


def test_c_core_path_cli(capsys):
    assert cli_main(["c-core-path"]) == 0
    assert os.path.isdir(capsys.readouterr().out.strip())
    assert cli_main(["c-core-path", "--file"]) == 0
    out = capsys.readouterr().out.strip()
    assert out.endswith(C_CORE_HEADER) and os.path.isfile(out)
    assert cli_main(["c-core-path", "--file", "pssc_mem_vtable.h"]) == 0
    assert os.path.isfile(capsys.readouterr().out.strip())


def test_cpp_core_path_cli(capsys):
    assert cli_main(["cpp-core-path"]) == 0
    assert os.path.isdir(capsys.readouterr().out.strip())
    assert cli_main(["cpp-core-path", "--file"]) == 0
    out = capsys.readouterr().out.strip()
    assert out.endswith(CPP_CORE_HEADER) and os.path.isfile(out)


@pytest.mark.c_toolchain
@pytest.mark.skipif(not shutil.which("gcc"), reason="gcc not on PATH")
@pytest.mark.parametrize("header", _C_HEADERS)
def test_c_headers_syntax(header):
    d = str(c_core_dir())
    r = subprocess.run(["gcc", "-std=c11", "-fsyntax-only", "-Wall", "-Wextra",
                        "-I", d, os.path.join(d, header)],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr


@pytest.mark.c_toolchain
@pytest.mark.skipif(not shutil.which("g++"), reason="g++ not on PATH")
def test_cpp_header_syntax():
    d = str(cpp_core_dir())
    r = subprocess.run(["g++", "-std=c++17", "-fsyntax-only", "-Wall", "-Wextra",
                        "-I", d, os.path.join(d, CPP_CORE_HEADER)],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
