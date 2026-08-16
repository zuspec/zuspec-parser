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

from .op_model import op_model_rel_paths

_SCRIPT = os.path.normpath(os.path.join(
    os.path.dirname(__file__), "..", "..", "scripts", "sync_op_model.py"))
_MODEL = os.path.normpath(os.path.join(
    os.path.dirname(__file__), "..", "..", "examples", "op_model", "pss"))


def test_op_model_copy_in_sync():
    r = subprocess.run([sys.executable, _SCRIPT, "--check"],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr


#: Upstream ``src/pss``, when both repositories are checked out. Set
#: ``FW_WB_DMA_SRC`` to point at it explicitly; otherwise the sibling layout
#: this repository is vendored into is tried.
def _upstream_src():
    env = os.environ.get("FW_WB_DMA_SRC")
    if env:
        return env if os.path.isdir(env) else None
    # <fw-wb-dma>/packages/pssc/tests/progseq -> <fw-wb-dma>
    guess = os.path.normpath(os.path.join(
        os.path.dirname(__file__), "..", "..", "..", "..", "src", "pss"))
    return guess if os.path.isdir(guess) else None


def test_op_model_copy_matches_upstream():
    """The check that `--check` alone cannot make.

    `--check` compares the copy to its own recorded manifest, so it passes for
    as long as nobody edits the copy -- no matter how far upstream has moved.
    That is exactly what happened: the copy sat four commits behind, reporting
    "in sync" the whole time, and still carried a two-file config-package shape
    the model had replaced. A regression suite passing against a stale model
    reports the wrong thing, which is worse than not running.

    Skips when upstream is not available, because pssc must remain testable
    from its own checkout alone.
    """
    src = _upstream_src()
    if src is None:
        import pytest
        pytest.skip("upstream fw-wb-dma src/pss not available "
                    "(set FW_WB_DMA_SRC to enable)")
    r = subprocess.run([sys.executable, _SCRIPT, "--check", "--src", src],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr


def test_files_f_puts_the_register_package_first():
    """The generated register package is not part of `src/pss` and must lead.

    Every component imports `wb_dma_regs_pkg`, and a front end that meets the
    import before the declaration leaves it unresolved while still reporting
    0 errors (pssparser D3). Since this entry is the one `files.f` line with no
    upstream path, it is also the one the ordering derivation cannot produce --
    so it is asserted rather than assumed.
    """
    entries = op_model_rel_paths()
    assert entries[0] == "wb_dma_regs_pkg.pss", entries[:3]


def test_op_model_files_f_lists_every_source():
    """``files.f`` is the dependency order the model must be presented in, and
    a file missing from it is silently absent from the model (pssparser D3).
    So the list and the tree must agree, in both directions."""
    listed = set(op_model_rel_paths())

    present = set()
    for dirpath, _, filenames in os.walk(_MODEL):
        for fn in filenames:
            if fn.endswith(".pss"):
                present.add(os.path.relpath(os.path.join(dirpath, fn), _MODEL))

    assert listed == present, (
        f"files.f and the tree disagree; "
        f"not on disk: {sorted(listed - present)}; not listed: {sorted(present - listed)}")
