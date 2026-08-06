"""Build tasks compile a trivial PSS model and emit correctly-typed filesets."""
import os
import types

import pytest

from .conftest import requires_dfm, run_task, filesets_by_type
from pssc.dvflow import build


# A component with an action AND an operation. The operation is not incidental:
# progseq refuses to emit an export API with zero operations (that shape is how
# every front-end defect in its history presented), so a model without one is
# not a valid input to those tasks.
_MODEL = """
component pss_top {
    int count;
    function void bump() { count = count + 1; }
    action Entry { exec body { print("hi\\n"); } }
}
"""


# --- override-keyword contract (no DFM runtime needed) -----------------------

def _params(**kw):
    return types.SimpleNamespace(**kw)


def test_sv_native_override_keywords():
    ov = build._sv_native_overrides(_params(
        projection="oo_api", package_name="zsp_gen_pkg",
        single_file=True, runtime=True))
    assert ov == {"sv_projection": "oo_api", "sv_package_name": "zsp_gen_pkg",
                  "sv_multi_file": True, "rt_pkg": True}


def test_progseq_override_keywords():
    ov = build._sv_progseq_overrides(_params(
        root="pss_top", package_name="", core_copy=True))
    assert ov["progseq_root"] == "pss_top"
    assert "progseq_package" not in ov   # empty package omitted
    assert ov["progseq_core_copy"] is True

    cov = build._c_progseq_overrides(_params(
        root="pss_top", prefix="", link_style="vtable",
        reg_style="bitfields", header_only=False, core_copy=True))
    assert cov["progseq_root"] == "pss_top"
    assert cov["c_link_style"] == "vtable"
    assert cov["c_reg_style"] == "bitfields"


def test_c_runtime_override_optionality():
    # Nothing set -> empty (each target keeps its own defaults)
    assert build._c_runtime_overrides(_params(
        root_action="", runtime_solve=False, presolve=False)) == {}
    assert build._c_runtime_overrides(_params(
        root_action="Entry", runtime_solve=True, presolve=False)) == {
            "root_action": "Entry", "runtime_solve": True}


def test_tasks_table_covers_all_entry_points():
    # Every TASKS entry has a matching module-level coroutine.
    import inspect
    for name in build.TASKS:
        fn = getattr(build, name, None)
        assert fn is not None and inspect.iscoroutinefunction(fn)


# --- end-to-end build runs (DFM, no simulator) -------------------------------

@requires_dfm
def test_sv_native_emits_systemverilog(tmp_path):
    status, output, errors = run_task(
        tmp_path, "pssc.SvNative", pss_text=_MODEL, export_action=["Entry"])
    assert status == 0, errors
    by_ft = filesets_by_type(output)
    assert "systemVerilogSource" in by_ft
    fs = by_ft["systemVerilogSource"][0]
    assert any(f.endswith(".sv") for f in fs.files)
    for f in fs.files:
        assert os.path.isfile(os.path.join(fs.basedir, f))


@requires_dfm
@pytest.mark.parametrize("task,filetype", [
    ("pssc.CHost", "cSource"),
    ("pssc.CHostPresolved", "cSource"),
    ("pssc.CEmbedded", "cSource"),
    ("pssc.CEmbeddedPresolved", "cSource"),
    ("pssc.SvDpi", "cSource"),
])
def test_c_family_emits_csource(tmp_path, task, filetype):
    status, output, errors = run_task(
        tmp_path, task, pss_text=_MODEL, export_action=["Entry"])
    assert status == 0, errors
    by_ft = filesets_by_type(output)
    assert filetype in by_ft
    fs = by_ft[filetype][0]
    assert fs.files


@requires_dfm
def test_pysource_emit_repr_manifest(tmp_path):
    status, output, errors = run_task(
        tmp_path, "pssc.PySource", pss_text=_MODEL, emit="repr")
    assert status == 0, errors
    by_ft = filesets_by_type(output)
    assert "pythonSource" in by_ft
    fs = by_ft["pythonSource"][0]
    assert fs.files
    for f in fs.files:
        assert os.path.isfile(os.path.join(fs.basedir, f))


@requires_dfm
def test_svprogseq_with_root(tmp_path):
    status, output, errors = run_task(
        tmp_path, "pssc.SvProgSeq", pss_text=_MODEL, root="pss_top")
    assert status == 0, errors
    assert "systemVerilogSource" in filesets_by_type(output)


@requires_dfm
def test_cppprogseq_with_root(tmp_path):
    status, output, errors = run_task(
        tmp_path, "pssc.CppProgSeq", pss_text=_MODEL, root="pss_top")
    assert status == 0, errors
    assert "cppSource" in filesets_by_type(output)


@requires_dfm
@pytest.mark.skipif(__import__("shutil").which("gcc") is None,
                    reason="gcc required to build the bridge .so")
def test_svdpibridge_emits_sv_and_dpi(tmp_path):
    status, output, errors = run_task(
        tmp_path, "pssc.SvDpiBridge", pss_text=_MODEL, export_action=["Entry"])
    assert status == 0, errors
    by_ft = filesets_by_type(output)
    # The trampoline SV package plus the compiled DPI shared library.
    assert "systemVerilogSource" in by_ft
    assert "systemVerilogDPI" in by_ft
    so = by_ft["systemVerilogDPI"][0]
    assert any(f.endswith(".so") for f in so.files)
    for f in so.files:
        assert os.path.isfile(os.path.join(so.basedir, f))


@requires_dfm
def test_progseq_requires_root(tmp_path):
    # Empty root -> pssc raises ValueError -> task surfaces an error marker.
    status, output, errors = run_task(
        tmp_path, "pssc.CProgSeq", pss_text=_MODEL)
    assert status != 0
    assert any("root" in e.lower() for e in errors)


@requires_dfm
def test_cprogseq_with_root(tmp_path):
    status, output, errors = run_task(
        tmp_path, "pssc.CProgSeq", pss_text=_MODEL, root="pss_top")
    assert status == 0, errors
    by_ft = filesets_by_type(output)
    assert "cSource" in by_ft


@requires_dfm
def test_no_pss_input_errors(tmp_path):
    status, output, errors = run_task(tmp_path, "pssc.SvNative")
    assert status != 0
    assert any("pssSource" in e for e in errors)


@requires_dfm
def test_memento_skips_recompile(tmp_path):
    # First run compiles; a second identical run should report no change.
    from dv_flow.mgr import TaskSetRunner
    from dv_flow.mgr.task_graph_builder import TaskGraphBuilder
    from .conftest import _make_loader
    import asyncio
    from pathlib import Path

    rundir = str(Path(tmp_path) / "rundir")
    src = Path(tmp_path) / "model.pss"
    src.write_text(_MODEL)

    def build_and_run():
        errors = []
        builder = TaskGraphBuilder(_make_loader(errors), rundir)
        runner = TaskSetRunner(rundir)
        runner.builder = builder
        fileset = builder.mkTaskNode(
            "std.FileSet", name="pss_src", type="pssSource",
            base=str(tmp_path), include=["model.pss"], needs=[])
        node = builder.mkTaskNode(
            "pssc.SvNative", name="task", needs=[fileset],
            export_action=["Entry"])
        out = asyncio.run(runner.run(node))
        return out

    out1 = build_and_run()
    out2 = build_and_run()
    # Second run: the build task should be up-to-date (changed=False).
    assert out2 is not None
    assert out2.changed is False
