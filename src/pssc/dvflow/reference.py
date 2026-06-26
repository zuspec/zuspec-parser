"""Reference tasks: emit filesets over the core source ``pssc`` bundles.

These tasks have no PSS input; they resolve the bundled ``share/`` directory via
the existing ``pssc.cli`` path helpers and emit a single typed fileset so a
downstream ``SimImage`` / compile step can consume the core source by ``needs:``.

  * :func:`RegPkg`  — SV register package (+ optional runtime) -> systemVerilogSource
  * :func:`CoreC`   — C seam headers (+ optional zsp_bridge)   -> cSource
  * :func:`CoreCpp` — C++ core header                          -> cppSource
"""
from __future__ import annotations

import logging
import os
from typing import List

_log = logging.getLogger("pssc.dvflow.reference")

#: Map the ``flavor`` param to the primary ``pssc_mem_*`` seam header.
_C_FLAVOR_HEADER = {
    "direct": "pssc_mem_direct.h",
    "mmio": "pssc_mem_mmio.h",
    "vtable": "pssc_mem_vtable.h",
}


def _memento(input, files: List[str]) -> dict:
    """Memento keyed on the pssc version + selected files (invalidate on upgrade)."""
    from pssc.__version__ import version
    return {"version": version, "files": sorted(files)}


def _unchanged(input, memento: dict) -> bool:
    prev = input.memento if isinstance(input.memento, dict) else None
    return prev is not None and prev == memento


async def RegPkg(ctxt, input):
    """Emit the bundled SV ``pssc_reg_pkg.sv`` (and, by default, ``zsp_rt_pkg.sv``)."""
    from dv_flow.mgr import FileSet, TaskDataResult
    from pssc.cli import sv_core_dir

    d = sv_core_dir()
    files = ["pssc_reg_pkg.sv"]
    if getattr(input.params, "runtime", True):
        files.append("zsp_rt_pkg.sv")

    missing = [f for f in files if not (d / f).is_file()]
    if missing:
        ctxt.error("pssc.RegPkg: bundled file(s) missing: %s" % ", ".join(missing))
        return TaskDataResult(status=1)

    memento = _memento(input, files)
    fs = FileSet(src=input.name, filetype="systemVerilogSource",
                 basedir=str(d), files=files, incdirs=[str(d)])
    return TaskDataResult(changed=not _unchanged(input, memento),
                          output=[fs], memento=memento)


async def CoreC(ctxt, input):
    """Emit the bundled C seam headers (+ optional ``zsp_bridge.{c,h}``)."""
    from dv_flow.mgr import FileSet, TaskDataResult
    from pssc.cli import c_core_dir

    d = c_core_dir()
    flavor = getattr(input.params, "flavor", "mmio") or "mmio"
    primary = _C_FLAVOR_HEADER.get(flavor)
    if primary is None:
        ctxt.error("pssc.CoreC: unknown flavor '%s' (expected one of %s)"
                   % (flavor, ", ".join(sorted(_C_FLAVOR_HEADER))))
        return TaskDataResult(status=1)

    files = ["pssc_mem.h", primary]
    if getattr(input.params, "bridge", False):
        files.extend(["zsp_bridge.h", "zsp_bridge.c"])

    missing = [f for f in files if not (d / f).is_file()]
    if missing:
        ctxt.error("pssc.CoreC: bundled file(s) missing: %s" % ", ".join(missing))
        return TaskDataResult(status=1)

    memento = _memento(input, files)
    fs = FileSet(src=input.name, filetype="cSource",
                 basedir=str(d), files=files, incdirs=[str(d)])
    return TaskDataResult(changed=not _unchanged(input, memento),
                          output=[fs], memento=memento)


async def CoreCpp(ctxt, input):
    """Emit the bundled C++ core header ``pssc_reg.hpp``."""
    from dv_flow.mgr import FileSet, TaskDataResult
    from pssc.cli import cpp_core_dir

    d = cpp_core_dir()
    files = ["pssc_reg.hpp"]

    missing = [f for f in files if not (d / f).is_file()]
    if missing:
        ctxt.error("pssc.CoreCpp: bundled file(s) missing: %s" % ", ".join(missing))
        return TaskDataResult(status=1)

    memento = _memento(input, files)
    fs = FileSet(src=input.name, filetype="cppSource",
                 basedir=str(d), files=files, incdirs=[str(d)])
    return TaskDataResult(changed=not _unchanged(input, memento),
                          output=[fs], memento=memento)
