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
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
from typing import Dict, List, Tuple

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
    return _report(*_compare(_manifest(src), _manifest(_DEST)), src_desc=src)


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

    It also picks the BUILD PROFILE: the ``src`` task excludes
    ``wb_dma_cfg_nonblocking.pss``, and it must. The two ``wb_dma_cfg_pkg``
    files declare the same package with opposite values of
    ``WB_DMA_HAS_BLOCKING``, so a tree holding both does not elaborate at all.
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


def refresh(src: str, source_commit: str) -> int:
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

    # files.f: the same order, written the way the tests read it (relative to
    # the upstream repo root, so a path in it is a path a reader can follow).
    with open(os.path.join(_DEST, "files.f"), "w") as fp:
        fp.write("# Derived from src/pss/flow.yaml (task `src`) by "
                 "scripts/sync_op_model.py -- do not edit.\n")
        for rel in order:
            fp.write(f"src/pss/{rel}\n")

    with open(_PROVENANCE, "w") as fp:
        json.dump({
            "source": "fw-wb-dma:src/pss",
            "source_commit": source_commit,
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
    args = ap.parse_args(argv)

    if args.src:
        src = os.path.abspath(args.src)
        if not os.path.isdir(src):
            print(f"no such directory: {src}", file=sys.stderr)
            return 1
        return check_against(src) if args.check else refresh(src, _git_commit(src))

    if not args.check:
        ap.error("refreshing requires --src; use --check to verify in place")
    return check_self()


if __name__ == "__main__":
    sys.exit(main())
