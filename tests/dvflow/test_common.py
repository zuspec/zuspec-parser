"""Unit tests for pssc.dvflow.common helpers (no DFM runtime required)."""
import os
import types
from pathlib import Path

import pytest

from pssc.dvflow import common


def _fs(filetype, basedir, files):
    """Duck-typed stand-in for a dv_flow FileSet/DataItem."""
    return types.SimpleNamespace(filetype=filetype, basedir=str(basedir),
                                 files=list(files))


def _input(inputs=(), **params):
    return types.SimpleNamespace(
        inputs=list(inputs),
        params=types.SimpleNamespace(**params))


def test_gather_pss_sources_orders_and_joins(tmp_path):
    inp = _input(inputs=[
        _fs("pssSource", tmp_path, ["a.pss", "b.pss"]),
        _fs("systemVerilogSource", tmp_path, ["ignore.sv"]),
        _fs("pssSource", tmp_path / "sub", ["c.pss"]),
    ])
    got = common.gather_pss_sources(inp)
    assert got == [
        str(tmp_path / "a.pss"),
        str(tmp_path / "b.pss"),
        str(tmp_path / "sub" / "c.pss"),
    ]


def test_gather_pss_sources_absolute_passthrough(tmp_path):
    abs_p = str(tmp_path / "x.pss")
    inp = _input(inputs=[_fs("pssSource", "/nonexistent/base", [abs_p])])
    assert common.gather_pss_sources(inp) == [abs_p]


def _dfm():
    import importlib.util
    return importlib.util.find_spec("dv_flow.mgr") is not None


@pytest.mark.skipif(not _dfm(), reason="dv-flow-mgr not installed")
def test_classify_outputs_groups_by_filetype_and_incdirs(tmp_path):
    # Create representative output files.
    names = ["zsp_gen_pkg.sv", "lib.so", "exec.c", "exec.h",
             "model.cpp", "model.hpp", "zsp_filelist.f"]
    for n in names:
        (tmp_path / n).write_text("x")
    paths = [tmp_path / n for n in names]

    filesets = common.classify_outputs(paths, "task", str(tmp_path))
    by_ft = {fs.filetype: fs for fs in filesets}

    assert set(by_ft) == {"systemVerilogSource", "systemVerilogDPI",
                          "cSource", "cppSource"}
    # .f filelist dropped
    assert "zsp_filelist.f" not in by_ft["systemVerilogSource"].files
    assert by_ft["systemVerilogSource"].files == ["zsp_gen_pkg.sv"]
    # .sv contributes an incdir; .so does not
    assert by_ft["systemVerilogSource"].incdirs == [str(tmp_path)]
    assert by_ft["systemVerilogDPI"].incdirs == []
    # cSource groups .c (no incdir) + .h (incdir)
    assert set(by_ft["cSource"].files) == {"exec.c", "exec.h"}
    assert by_ft["cSource"].incdirs == [str(tmp_path)]
    # cppSource groups .cpp + .hpp
    assert set(by_ft["cppSource"].files) == {"model.cpp", "model.hpp"}
    assert by_ft["cppSource"].incdirs == [str(tmp_path)]


@pytest.mark.skipif(not _dfm(), reason="dv-flow-mgr not installed")
def test_classify_outputs_skips_outside_basedir(tmp_path):
    inside = tmp_path / "in"
    inside.mkdir()
    f_in = inside / "a.sv"
    f_in.write_text("x")
    outside = tmp_path / "out.sv"
    outside.write_text("x")

    filesets = common.classify_outputs([f_in, outside], "task", str(inside))
    assert len(filesets) == 1
    assert filesets[0].files == ["a.sv"]


def test_compute_memento_is_stable_and_sensitive(tmp_path):
    a = tmp_path / "a.pss"
    a.write_text("component c {}")
    opts = {"export_actions": ["E"], "x": 1}

    m1 = common.compute_memento([str(a)], "sv-native", opts)
    m2 = common.compute_memento([str(a)], "sv-native", opts)
    assert m1 == m2

    # changed source content
    a.write_text("component c { action A {} }")
    assert common.compute_memento([str(a)], "sv-native", opts) != m1

    # changed target
    assert common.compute_memento([str(a)], "c-host", opts) != m1
    # changed option
    assert common.compute_memento([str(a)], "sv-native",
                                  {"export_actions": ["E"], "x": 2}) != m1


def test_ext_filetype_excludes_filelist():
    assert ".f" not in common.EXT_FILETYPE
    assert common.EXT_FILETYPE[".sv"] == ("systemVerilogSource", True)
    assert common.EXT_FILETYPE[".so"] == ("systemVerilogDPI", False)
    assert common.EXT_FILETYPE[".h"][1] is True   # header -> incdir
    assert common.EXT_FILETYPE[".c"][1] is False
