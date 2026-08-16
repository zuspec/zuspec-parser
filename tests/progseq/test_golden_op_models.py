"""The frozen operation-model snapshots (P0.T2).

One test per configuration in `golden_util.CONFIGS`. A failure here means the
generated artifact changed; the failure message says which file and how, and
what to do if the change was intended.

These prove sameness, not correctness. See golden_util's module docstring.
"""
import pytest

from . import golden_util as gu


pytestmark = pytest.mark.golden


@pytest.mark.parametrize("config", [c.name for c in gu.CONFIGS])
def test_golden(config, tmp_path):
    gu.assert_golden(config, tmp_path)


def test_every_config_is_snapshotted():
    """A config added to CONFIGS without a snapshot would otherwise only fail
    the first time someone ran it -- which is the run that regenerates."""
    missing = [c.name for c in gu.CONFIGS
               if not (gu.GOLDEN_ROOT / c.name / "MANIFEST").exists()]
    assert not missing, f"configs with no frozen snapshot: {missing}"


def test_no_orphaned_snapshots():
    """A snapshot for a config nobody generates any more is dead weight that
    still reads as coverage."""
    if not gu.GOLDEN_ROOT.exists():
        pytest.skip("no snapshots yet")
    known = {c.name for c in gu.CONFIGS}
    orphans = sorted(d.name for d in gu.GOLDEN_ROOT.iterdir()
                     if d.is_dir() and d.name not in known)
    assert not orphans, f"snapshot directories with no config: {orphans}"
