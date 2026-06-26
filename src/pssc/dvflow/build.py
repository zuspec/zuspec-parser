"""Build tasks: one per ``pssc`` output style.

Each task is a thin wrapper that names a ``pssc`` target and supplies an
``overrides_from_params`` mapping (task ``with:`` params -> the keyword names
``pssc.compile`` forwards onto the target's option namespace). All shared
logic — gathering PSS sources, running the compile, classifying outputs,
incremental skipping — lives in :func:`pssc.dvflow.common.run_build`.

The override keyword names are the ``dest=`` names declared by each target's
``add_args`` (verified against ``pssc/targets/*.py``); ``test_build_tasks``
pins them so a future rename surfaces as a test failure rather than a no-op.
"""
from __future__ import annotations

from typing import Any, Dict

from .common import run_build


def _get(params, name, default=None):
    return getattr(params, name, default)


# --- override maps (task params -> pssc.compile target keyword) --------------

def _python_overrides(p) -> Dict[str, Any]:
    return {"emit": _get(p, "emit", "none")}


def _sv_native_overrides(p) -> Dict[str, Any]:
    return {
        "sv_projection": _get(p, "projection", "oo_api"),
        "sv_package_name": _get(p, "package_name", "zsp_gen_pkg"),
        "sv_multi_file": _get(p, "single_file", True),
        "rt_pkg": _get(p, "runtime", True),
    }


def _c_runtime_overrides(p) -> Dict[str, Any]:
    """Shared options for the c-host/c-embedded/sv-dpi family.

    ``root_action``/``runtime_solve``/``presolve`` are all optional; pass only
    what was set so each target keeps its own default (e.g. presolved variants).
    """
    ov: Dict[str, Any] = {}
    root_action = _get(p, "root_action", "")
    if root_action:
        ov["root_action"] = root_action
    if _get(p, "runtime_solve", False):
        ov["runtime_solve"] = True
    if _get(p, "presolve", False):
        ov["presolve"] = True
    return ov


def _bridge_overrides(p) -> Dict[str, Any]:
    ov: Dict[str, Any] = {}
    if _get(p, "runtime_solve", False):
        ov["runtime_solve"] = True
    return ov


def _sv_progseq_overrides(p) -> Dict[str, Any]:
    ov: Dict[str, Any] = {"progseq_root": _get(p, "root", "")}
    if _get(p, "package_name", ""):
        ov["progseq_package"] = _get(p, "package_name")
    ov["progseq_core_copy"] = _get(p, "core_copy", True)
    return ov


def _c_progseq_overrides(p) -> Dict[str, Any]:
    ov: Dict[str, Any] = {"progseq_root": _get(p, "root", "")}
    if _get(p, "prefix", ""):
        ov["c_prefix"] = _get(p, "prefix")
    ov["c_link_style"] = _get(p, "link_style", "vtable")
    ov["c_reg_style"] = _get(p, "reg_style", "bitfields")
    if _get(p, "header_only", False):
        ov["c_header_only"] = True
    ov["progseq_core_copy"] = _get(p, "core_copy", True)
    return ov


def _cpp_progseq_overrides(p) -> Dict[str, Any]:
    ov: Dict[str, Any] = {"progseq_root": _get(p, "root", "")}
    if _get(p, "namespace", ""):
        ov["cpp_namespace"] = _get(p, "namespace")
    ov["cpp_dispatch"] = _get(p, "dispatch", "virtual")
    ov["progseq_core_copy"] = _get(p, "core_copy", True)
    return ov


#: Public mapping of task name -> (pssc target, override factory). Exposed so
#: tests can assert the override keyword contract without DFM at runtime.
TASKS = {
    "PySource": ("python", _python_overrides),
    "SvNative": ("sv-native", _sv_native_overrides),
    "SvDpi": ("sv-dpi", _c_runtime_overrides),
    "SvDpiBridge": ("sv-dpi-bridge", _bridge_overrides),
    "CHost": ("c-host", _c_runtime_overrides),
    "CHostPresolved": ("c-host-presolved", _c_runtime_overrides),
    "CEmbedded": ("c-embedded", _c_runtime_overrides),
    "CEmbeddedPresolved": ("c-embedded-presolved", _c_runtime_overrides),
    "SvProgSeq": ("sv-progseq", _sv_progseq_overrides),
    "CProgSeq": ("c-progseq", _c_progseq_overrides),
    "CppProgSeq": ("cpp-progseq", _cpp_progseq_overrides),
}


# --- task entry points -------------------------------------------------------

async def PySource(ctxt, input):
    return await run_build(ctxt, input, target="python",
                           overrides_from_params=_python_overrides)


async def SvNative(ctxt, input):
    return await run_build(ctxt, input, target="sv-native",
                           overrides_from_params=_sv_native_overrides)


async def SvDpi(ctxt, input):
    return await run_build(ctxt, input, target="sv-dpi",
                           overrides_from_params=_c_runtime_overrides)


async def SvDpiBridge(ctxt, input):
    return await run_build(ctxt, input, target="sv-dpi-bridge",
                           overrides_from_params=_bridge_overrides)


async def CHost(ctxt, input):
    return await run_build(ctxt, input, target="c-host",
                           overrides_from_params=_c_runtime_overrides)


async def CHostPresolved(ctxt, input):
    return await run_build(ctxt, input, target="c-host-presolved",
                           overrides_from_params=_c_runtime_overrides)


async def CEmbedded(ctxt, input):
    return await run_build(ctxt, input, target="c-embedded",
                           overrides_from_params=_c_runtime_overrides)


async def CEmbeddedPresolved(ctxt, input):
    return await run_build(ctxt, input, target="c-embedded-presolved",
                           overrides_from_params=_c_runtime_overrides)


async def SvProgSeq(ctxt, input):
    return await run_build(ctxt, input, target="sv-progseq",
                           overrides_from_params=_sv_progseq_overrides)


async def CProgSeq(ctxt, input):
    return await run_build(ctxt, input, target="c-progseq",
                           overrides_from_params=_c_progseq_overrides)


async def CppProgSeq(ctxt, input):
    return await run_build(ctxt, input, target="cpp-progseq",
                           overrides_from_params=_cpp_progseq_overrides)
