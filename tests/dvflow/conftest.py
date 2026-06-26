"""Shared fixtures/helpers for the pssc DFM task tests.

Provides a `requires_dfm` skip marker and a small helper that builds and runs a
`std.FileSet(pssSource) -> pssc.<Task>` graph entirely in-process, returning the
status, output filesets, and any error markers.
"""
import asyncio
import importlib.util
from pathlib import Path

import pytest


def dfm_available() -> bool:
    return importlib.util.find_spec("dv_flow.mgr") is not None


requires_dfm = pytest.mark.skipif(
    not dfm_available(), reason="dv-flow-mgr not installed")


def _make_loader(errors):
    from dv_flow.mgr import PackageLoader
    from dv_flow.mgr.task_data import SeverityE

    def listener(marker):
        if marker.severity == SeverityE.Error:
            errors.append(str(marker.msg))

    return PackageLoader(marker_listeners=[listener]).load_rgy(["std", "pssc"])


def run_task(tmp_path, task_type, *, pss_text=None, pss_files=None,
             needs_extra=None, **params):
    """Build and run a single pssc build/reference task graph.

    Args:
        tmp_path: working dir (rundir parent).
        task_type: e.g. "pssc.SvNative" or "pssc.RegPkg".
        pss_text: inline PSS source -> written to a file + a pssSource FileSet.
        pss_files: explicit list of PSS file paths (alternative to pss_text).
        needs_extra: list of already-built task nodes to also add to `needs`.
        **params: forwarded to the task node (the task's `with:` params).

    Returns:
        (status, output_filesets, errors)
    """
    from dv_flow.mgr import TaskSetRunner
    from dv_flow.mgr.task_graph_builder import TaskGraphBuilder
    from dv_flow.mgr.task_data import SeverityE

    rundir = str(Path(tmp_path) / "rundir")
    errors = []
    builder = TaskGraphBuilder(_make_loader(errors), rundir)
    runner = TaskSetRunner(rundir)
    runner.builder = builder

    # Collect runtime task markers (ctxt.error -> result.markers) as the runner
    # only dispatches (task, reason) events, not markers, to listeners.
    seen = set()

    def collect_markers(task, reason):
        result = getattr(task, "result", None)
        for m in getattr(result, "markers", None) or []:
            key = (id(m), getattr(m, "msg", None))
            if key in seen:
                continue
            seen.add(key)
            if getattr(m, "severity", None) == SeverityE.Error:
                errors.append(str(m.msg))

    runner.add_listener(collect_markers)

    needs = list(needs_extra or [])

    if pss_text is not None:
        src = Path(tmp_path) / "model.pss"
        src.write_text(pss_text)
        pss_files = [str(src)]
    if pss_files:
        base = str(Path(pss_files[0]).parent)
        fileset = builder.mkTaskNode(
            "std.FileSet", name="pss_src", type="pssSource",
            base=base, include=[Path(p).name for p in pss_files], needs=[])
        needs.append(fileset)

    node = builder.mkTaskNode(task_type, name="task", needs=needs, **params)
    out = asyncio.run(runner.run(node))

    output = list(out.output) if out is not None and hasattr(out, "output") else []
    return runner.status, output, errors


def filesets_by_type(output):
    """Index output filesets by their `filetype`."""
    res = {}
    for fs in output:
        ft = getattr(fs, "filetype", None)
        if ft is not None:
            res.setdefault(ft, []).append(fs)
    return res
