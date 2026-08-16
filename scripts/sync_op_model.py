#!/usr/bin/env python3
"""Refresh (or verify) the checked-in copy of the WB DMA operation model.

``examples/op_model/pss/`` is a **copy** of the model that lives in the
fw-wb-dma repository at ``src/pss/``. pssc's tests are developed against it, so
it has to be here — pssc must be testable from its own checkout alone — but a
copy that can drift silently is worse than no copy: a regression suite that
passes against a stale model is a regression suite that reports the wrong thing.

Two modes, and they answer different questions:

``--check`` (no ``--src``)
    Has anyone edited the copy in place? Compares every file against the
    manifest recorded in ``PROVENANCE.json``. This is the CI mode: it needs
    nothing but this repository.

``--check --src <path>``  /  ``--src <path>`` (refresh)
    Has the upstream model moved on? Compares against — or copies from — a real
    ``src/pss`` tree. Run this where both repositories are checked out.

Exit status is 0 when the answer is "in sync", 1 otherwise, and the differing
paths are named. Deliberately not silent about *which* files differ: "the
example is stale" is not actionable.

NOTE WHICH QUESTION EACH MODE ANSWERS, because the difference has already cost
one silent drift. ``--check`` compares the copy **to itself**; it passes for as
long as nobody edits the copy, no matter how far upstream has moved. Only
``--src`` looks upstream, and nothing runs it automatically. If you are adding
CI, the mode you want is ``--check --src``.

THE REGISTER PACKAGE IS NOT UNDER ``src/pss``. ``wb_dma_regs_pkg`` is generated
from SystemRDL and reaches the compiler from another task, so a copy of
``src/pss`` alone does not elaborate. Pass ``--regs <generated .pss>`` to
snapshot it alongside; it is written with a provenance banner and listed first
in ``files.f``.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
from typing import Dict, List, Optional, Tuple

_HERE = os.path.dirname(os.path.abspath(__file__))
_DEST = os.path.normpath(os.path.join(_HERE, "..", "examples", "op_model", "pss"))
_PROVENANCE = os.path.normpath(
    os.path.join(_HERE, "..", "examples", "op_model", "PROVENANCE.json"))

#: Only these are part of the model. Anything else in a source tree (build
#: output, editor droppings) is not copied and not compared.
_SUFFIXES = (".pss", ".f", ".md")


def _files(root: str) -> List[str]:
    """Model files under ``root``, as sorted repo-relative paths."""
    out: List[str] = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames if not d.startswith("."))
        for fn in sorted(filenames):
            if fn.endswith(_SUFFIXES):
                out.append(os.path.relpath(os.path.join(dirpath, fn), root))
    return sorted(out)


def _digest(path: str) -> str:
    with open(path, "rb") as fp:
        return hashlib.sha256(fp.read()).hexdigest()


def _manifest(root: str) -> Dict[str, str]:
    return {rel: _digest(os.path.join(root, rel)) for rel in _files(root)}


def _compare(want: Dict[str, str], have: Dict[str, str]) -> Tuple[List[str], List[str], List[str]]:
    """(missing, extra, differing) — ``want`` is the reference."""
    missing = sorted(set(want) - set(have))
    extra = sorted(set(have) - set(want))
    differing = sorted(k for k in set(want) & set(have) if want[k] != have[k])
    return missing, extra, differing


def _report(missing: List[str], extra: List[str], differing: List[str], src_desc: str) -> int:
    if not (missing or extra or differing):
        print(f"examples/op_model/pss is in sync with {src_desc}")
        return 0
    print(f"examples/op_model/pss has DRIFTED from {src_desc}:", file=sys.stderr)
    for rel in missing:
        print(f"  missing:   {rel}", file=sys.stderr)
    for rel in extra:
        print(f"  unexpected:{rel}", file=sys.stderr)
    for rel in differing:
        print(f"  differs:   {rel}", file=sys.stderr)
    print("\nRun scripts/sync_op_model.py --src <fw-wb-dma>/src/pss to refresh.",
          file=sys.stderr)
    return 1


def check_self() -> int:
    """Verify the copy against its own recorded manifest (no --src needed)."""
    if not os.path.isfile(_PROVENANCE):
        print(f"no provenance file: {_PROVENANCE}", file=sys.stderr)
        return 1
    with open(_PROVENANCE) as fp:
        prov = json.load(fp)
    return _report(*_compare(prov["manifest"], _manifest(_DEST)),
                   src_desc=f"its recorded manifest ({prov.get('source_commit', 'unknown')})")


def check_against(src: str) -> int:
    """Has the upstream model moved on? Compare the copy against a real tree.

    Two files this script itself writes are excluded from the comparison:
    ``files.f`` (derived from the flow at sync time; upstream deleted its copy
    precisely because a static list rots) and the register-package snapshot
    (generated from SystemRDL, so nothing under ``src/pss`` declares it).
    Neither has an upstream counterpart to differ from, and reporting them as
    ``unexpected`` on every run would train a reader to ignore this output --
    which is the failure mode this whole script exists to prevent.

    Their freshness is a separate question: ``files.f`` is rewritten on every
    refresh, and the snapshot when ``--regs`` is passed.
    """
    have = {k: v for k, v in _manifest(_DEST).items() if k not in _GENERATED}
    return _report(*_compare(_manifest(src), have), src_desc=src)


def _derive_order(src: str) -> List[str]:
    """The model's files, in dependency order, derived from its own flow.

    ``src/pss/flow.yaml``'s ``src`` task IS the statement of which files make up
    the model and what order they must be presented in -- the order is
    load-bearing, because a file presented before something it references leaves
    the reference unresolved while the front end still reports ``0 errors``
    (pssparser D3).

    Derived, not copied. Upstream used to keep a generated ``src/pss/files.f``
    for this and deleted it precisely because a static list goes stale while a
    derivation cannot; the sync then had nothing to copy and left the example
    without one. Asking the flow at sync time is the version of that list which
    cannot rot.

    It no longer has to pick a build profile. The model used to carry two
    mutually-exclusive ``wb_dma_cfg_*.pss`` files and the ``src`` task excluded
    one; the profile is now a property of the TARGET (``target_cfg_pkg``,
    injected by pssc) and one fileset serves both.
    """
    import subprocess
    r = subprocess.run(
        ["pss-order", "--from-flow", src, "--task", "src"],
        capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(
            "could not derive the model's file order from "
            f"{src}/flow.yaml via `pss-order`:\n{r.stderr.strip()}\n"
            "The order is not guessable -- alphabetical order leaves dozens of "
            "references unresolved and still exits 0 -- so this refuses rather "
            "than writing a files.f that would be wrong.")
    return [ln.strip() for ln in r.stdout.splitlines() if ln.strip()]


#: Where the snapshot of the generated register package lands. It is NOT under
#: `src/pss` upstream and never will be -- see :func:`_snapshot_regs`.
_REGS_REL = "wb_dma_regs_pkg.pss"

#: Files this script writes into the copy that have no upstream counterpart.
#: `check_against` must not report these as unexpected.
_GENERATED = frozenset({_REGS_REL, "files.f"})

_REGS_BANNER = """\
// SNAPSHOT -- do not edit, and do not treat as part of the model.
//
// `wb_dma_regs_pkg` is GENERATED IN FULL from `src/rdl` by PeakRDL
// (`reg-model-pss` in the upstream flow). No file under `src/pss` declares it;
// the components there import it and the flow orders it ahead of them with
// `needs`. So it is not in the derived file order, and copying `src/pss` alone
// produces a tree that does not elaborate.
//
// It is snapshotted here rather than generated, deliberately: pssc's test suite
// must run from pssc's own checkout, and acquiring a PeakRDL dependency to
// rebuild a file that changes when the RDL changes -- rarely, and visibly --
// would cost more than it buys.
//
// Refresh it with the rest of the model:
//   scripts/sync_op_model.py --src <fw-wb-dma>/src/pss --regs <generated>.pss
//
// Source: {source}
// Upstream commit: {commit}
"""


def _snapshot_regs(regs: str, source_commit: str) -> None:
    """Copy the generated register package in, with a provenance banner."""
    with open(regs) as fp:
        body = fp.read()
    banner = _REGS_BANNER.format(
        source=f"fw-wb-dma:{os.path.basename(regs)} (generated from src/rdl)",
        commit=source_commit)
    with open(os.path.join(_DEST, _REGS_REL), "w") as fp:
        fp.write(banner + "//\n" + body)


def refresh(src: str, source_commit: str, regs: Optional[str] = None) -> int:
    order = _derive_order(src)

    if os.path.isdir(_DEST):
        shutil.rmtree(_DEST)
    # The ordered set, plus the non-source files (README) that document it.
    copied = list(order) + [f for f in _files(src)
                            if not f.endswith(".pss") and f not in order]
    for rel in copied:
        dst = os.path.join(_DEST, rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(os.path.join(src, rel), dst)

    if regs:
        _snapshot_regs(regs, source_commit)

    # files.f: the same order, written the way the tests read it (relative to
    # the upstream repo root, so a path in it is a path a reader can follow).
    #
    # The register package goes FIRST and is spelled relative to THIS tree,
    # because it has no upstream path under src/pss -- it is generated. Getting
    # this wrong is the silent kind: every component imports the package, and a
    # front end that meets the import before the declaration leaves it
    # unresolved while still reporting 0 errors (pssparser D3).
    with open(os.path.join(_DEST, "files.f"), "w") as fp:
        fp.write("# Derived from src/pss/flow.yaml (task `src`) by "
                 "scripts/sync_op_model.py -- do not edit.\n")
        if regs:
            fp.write("# Generated register package, snapshotted here; it is "
                     "not part of src/pss and must compile first.\n")
            fp.write(f"{_REGS_REL}\n")
        for rel in order:
            fp.write(f"src/pss/{rel}\n")

    with open(_PROVENANCE, "w") as fp:
        json.dump({
            "source": "fw-wb-dma:src/pss",
            "source_commit": source_commit,
            "regs_snapshot": _REGS_REL if regs else None,
            "manifest": _manifest(_DEST),
        }, fp, indent=2, sort_keys=True)
        fp.write("\n")
    print(f"refreshed examples/op_model/pss from {src} ({len(_files(_DEST))} files)")
    return 0


def _git_commit(src: str) -> str:
    """The commit of the repository holding ``src``, or 'unknown'."""
    import subprocess
    try:
        r = subprocess.run(["git", "-C", src, "rev-parse", "--short", "HEAD"],
                           capture_output=True, text=True, check=True)
        return r.stdout.strip()
    except Exception:
        return "unknown"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--src", help="path to the upstream fw-wb-dma src/pss tree")
    ap.add_argument("--check", action="store_true",
                    help="report drift instead of refreshing")
    ap.add_argument("--regs", metavar="PSS",
                    help="path to the GENERATED wb_dma_regs_pkg.pss to "
                         "snapshot alongside the model (from the upstream "
                         "build, e.g. rundir/*.reg-model-pss/). Nothing under "
                         "src/pss declares that package, so a copy without it "
                         "does not elaborate.")
    args = ap.parse_args(argv)

    if args.src:
        src = os.path.abspath(args.src)
        if not os.path.isdir(src):
            print(f"no such directory: {src}", file=sys.stderr)
            return 1
        if args.check:
            return check_against(src)
        if args.regs and not os.path.isfile(args.regs):
            print(f"no such file: {args.regs}", file=sys.stderr)
            return 1
        return refresh(src, _git_commit(src), args.regs)

    if args.regs:
        ap.error("--regs is only meaningful when refreshing (--src)")
    if not args.check:
        ap.error("refreshing requires --src; use --check to verify in place")
    return check_self()


if __name__ == "__main__":
    sys.exit(main())
