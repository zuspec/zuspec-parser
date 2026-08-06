"""The checked-in operation model must not drift from its recorded manifest.

``examples/op_model/pss/`` is a copy of fw-wb-dma's ``src/pss/``. A copy that
drifts does not fail — it passes, against the wrong model — which is exactly the
silent-success failure mode the operation-model work exists to eliminate. So the
copy carries a per-file digest and this test enforces it.

This checks the copy against *itself* (was it edited in place?), which needs
nothing but this repository. Checking it against upstream needs both
repositories and is the ``--src`` mode of the same script.
"""
import os
import subprocess
import sys

_SCRIPT = os.path.normpath(os.path.join(
    os.path.dirname(__file__), "..", "..", "scripts", "sync_op_model.py"))
_MODEL = os.path.normpath(os.path.join(
    os.path.dirname(__file__), "..", "..", "examples", "op_model", "pss"))


def test_op_model_copy_in_sync():
    r = subprocess.run([sys.executable, _SCRIPT, "--check"],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr


def test_op_model_files_f_lists_every_source():
    """``files.f`` is the dependency order the model must be presented in, and
    a file missing from it is silently absent from the model (pssparser D3).
    So the list and the tree must agree, in both directions."""
    with open(os.path.join(_MODEL, "files.f")) as fp:
        listed = {ln.strip() for ln in fp if ln.strip() and not ln.startswith("#")}
    # entries are written relative to the fw-wb-dma root: src/pss/<path>
    listed = {os.path.relpath(p, "src/pss") for p in listed}

    present = set()
    for dirpath, _, filenames in os.walk(_MODEL):
        for fn in filenames:
            if fn.endswith(".pss"):
                present.add(os.path.relpath(os.path.join(dirpath, fn), _MODEL))

    assert listed == present, (
        f"files.f and the tree disagree; "
        f"not on disk: {sorted(listed - present)}; not listed: {sorted(present - listed)}")
