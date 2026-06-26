"""Shared helpers for the ``pssc`` DFM build tasks.

The heavy lifting that every per-output-style build task shares lives here:

  * :func:`gather_pss_sources` — pull ``pssSource`` files out of task inputs.
  * :func:`classify_outputs` — group ``pssc.compile`` outputs into typed filesets.
  * :func:`compute_memento` — content hash for incremental-rebuild skipping.
  * :func:`run_build` — the full build-task body (gather → compile → classify).

:mod:`dv_flow.mgr` symbols are imported lazily inside the functions so that
importing this module never hard-requires DFM.
"""
from __future__ import annotations

import asyncio
import contextlib
import hashlib
import logging
import os
from pathlib import Path
from typing import Any, Callable, Dict, List, Tuple

_log = logging.getLogger("pssc.dvflow")

#: The fileset ``filetype`` PSS sources are tagged with (authored via
#: ``std.FileSet { type: pssSource }``).
PSS_SOURCE_FILETYPE = "pssSource"

#: Dataset ``type`` carrying shared build options (see ``flow.yaml``).
PSSC_ARGS_TYPE = "pssc.PsscArgs"

#: extension -> (fileset filetype, contributes-its-dir-as-an-incdir)
#: ``.f`` filelists are intentionally absent: DFM tracks file membership itself,
#: so the generated filelist is dropped (design §7.5).
EXT_FILETYPE: Dict[str, Tuple[str, bool]] = {
    ".sv": ("systemVerilogSource", True),
    ".svh": ("systemVerilogSource", True),
    ".so": ("systemVerilogDPI", False),
    ".c": ("cSource", False),
    ".h": ("cSource", True),
    ".cpp": ("cppSource", False),
    ".cc": ("cppSource", False),
    ".hpp": ("cppSource", True),
    ".hh": ("cppSource", True),
    ".py": ("pythonSource", False),
    ".txt": ("pythonSource", False),
    ".pkl": ("pythonSource", False),
}


def gather_pss_sources(input) -> List[str]:
    """Return absolute paths of every ``pssSource`` file in ``input.inputs``.

    Order is preserved (fileset order, then file order within each fileset).
    """
    sources: List[str] = []
    for fs in input.inputs:
        if getattr(fs, "filetype", None) != PSS_SOURCE_FILETYPE:
            continue
        basedir = getattr(fs, "basedir", "") or ""
        for f in getattr(fs, "files", []) or []:
            sources.append(f if os.path.isabs(f) else os.path.join(basedir, f))
    return sources


def gather_export_actions(input) -> List[str]:
    """Collect export-action names from task params and ``pssc.PsscArgs`` inputs."""
    actions: List[str] = list(getattr(input.params, "export_action", None) or [])
    for ds in input.inputs:
        if getattr(ds, "type", None) == PSSC_ARGS_TYPE:
            actions.extend(getattr(ds, "export_action", None) or [])
    return actions


def gather_extra_args(input) -> List[str]:
    """Collect raw pass-through ``args`` from task params and ``pssc.PsscArgs``."""
    args: List[str] = list(getattr(input.params, "args", None) or [])
    for ds in input.inputs:
        if getattr(ds, "type", None) == PSSC_ARGS_TYPE:
            args.extend(getattr(ds, "args", None) or [])
    return args


def classify_outputs(paths, src_name: str, basedir: str) -> List[Any]:
    """Group ``pssc.compile`` output ``paths`` into typed DFM filesets.

    One :class:`~dv_flow.mgr.FileSet` per distinct filetype, each with
    ``basedir`` and relative ``files``; directories of incdir-eligible files
    (headers, SV) are added to that fileset's ``incdirs``. Files outside
    ``basedir`` or with an unknown extension are logged and skipped.
    """
    from dv_flow.mgr import FileSet

    base = os.path.abspath(basedir)
    # filetype -> (files[], incdirs set)
    groups: Dict[str, Tuple[List[str], set]] = {}
    for p in paths:
        ap = os.path.abspath(str(p))
        ext = os.path.splitext(ap)[1].lower()
        mapping = EXT_FILETYPE.get(ext)
        if mapping is None:
            _log.debug("classify_outputs: skipping unmapped output %s", ap)
            continue
        filetype, is_incdir = mapping
        try:
            rel = os.path.relpath(ap, base)
        except ValueError:
            rel = None
        if rel is None or rel.startswith(".."):
            _log.warning("classify_outputs: output %s outside basedir %s; skipping",
                         ap, base)
            continue
        files, incdirs = groups.setdefault(filetype, ([], set()))
        files.append(rel)
        if is_incdir:
            incdirs.add(os.path.dirname(ap) or base)

    filesets = []
    for filetype, (files, incdirs) in groups.items():
        # Preserve pssc's emission order: it returns files in dependency order
        # (e.g. zsp_rt_pkg.sv before zsp_gen_pkg.sv), which SV compilation needs.
        filesets.append(FileSet(
            src=src_name,
            filetype=filetype,
            basedir=base,
            files=files,
            incdirs=sorted(incdirs),
        ))
    return filesets


def _read_text(path: str) -> str:
    try:
        with open(path, "r", errors="replace") as fp:
            return fp.read()
    except OSError as e:
        _log.warning("memento: cannot read %s: %s", path, e)
        return ""


def compute_memento(sources: List[str], target: str,
                    options: Dict[str, Any]) -> str:
    """Stable md5 over source *contents*, the target, and the resolved options.

    Used to skip recompilation when nothing relevant changed (mirrors the
    ``std.CreateFile`` md5-memento pattern).
    """
    h = hashlib.md5()
    h.update(("target=" + target).encode())
    for key in sorted(options):
        h.update(f"|opt:{key}={options[key]!r}".encode())
    for src in sorted(sources):
        h.update(("|src:" + os.path.basename(src) + ":").encode())
        h.update(_read_text(src).encode())
    return h.hexdigest()


async def run_build(ctxt, input, *, target: str,
                    overrides_from_params: Callable[[Any], Dict[str, Any]]):
    """Body shared by every ``pssc`` build task.

    Gathers PSS sources and options, optionally skips via the memento, runs
    ``pssc.compile`` (off-thread), converts PSS errors into DFM markers, and
    returns typed output filesets.
    """
    from dv_flow.mgr import TaskDataResult
    import pssc
    from pssc.driver import CompileError

    sources = gather_pss_sources(input)
    if not sources:
        ctxt.error("pssc.%s: no 'pssSource' inputs found (needs a "
                   "std.FileSet with type: pssSource)" % target)
        return TaskDataResult(status=1, changed=True)

    export_actions = gather_export_actions(input)
    overrides = dict(overrides_from_params(input.params))
    extra_args = gather_extra_args(input)

    # Option set that participates in the memento / change detection.
    option_sig: Dict[str, Any] = dict(overrides)
    option_sig["export_actions"] = sorted(export_actions)
    option_sig["args"] = list(extra_args)

    memento = compute_memento(sources, target, option_sig)
    prev = input.memento if isinstance(input.memento, dict) else None
    if (not input.changed and prev is not None
            and prev.get("hash") == memento and prev.get("output") is not None):
        from dv_flow.mgr import FileSet
        cached = [FileSet(**fs) for fs in prev["output"]]
        _log.debug("pssc.%s: up to date; reusing %d cached fileset(s)",
                   target, len(cached))
        return TaskDataResult(changed=False, output=cached,
                              memento=prev)

    out_dir = input.rundir
    os.makedirs(out_dir, exist_ok=True)
    log_path = os.path.join(out_dir, "pssc_compile.log")

    def _do_compile():
        # Some targets print a report to stdout; capture it to a logfile.
        with open(log_path, "w") as logf, contextlib.redirect_stdout(logf):
            return pssc.compile(
                sources, target=target, output_dir=out_dir,
                export_actions=export_actions or None, **overrides)

    try:
        res = await asyncio.to_thread(_do_compile)
    except CompileError as e:
        errs = e.errors or [str(e)]
        for msg in errs:
            ctxt.error("pssc.%s: %s" % (target, msg))
        return TaskDataResult(status=1, changed=True)
    except Exception as e:  # noqa: BLE001 — surface any target failure as a marker
        _log.exception("pssc.%s failed", target)
        ctxt.error("pssc.%s: %s: %s" % (target, type(e).__name__, e))
        return TaskDataResult(status=1, changed=True)

    output = classify_outputs(res.outputs, input.name, out_dir)
    new_memento = {"hash": memento,
                   "output": [fs.model_dump() for fs in output]}
    return TaskDataResult(status=0, changed=True, output=output,
                          memento=new_memento)
