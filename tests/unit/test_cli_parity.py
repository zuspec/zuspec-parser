"""Phase-2 Gate: CLI/driver output matches the legacy API.

  * SV     -> byte-identical files vs generate_sv_files
  * Python -> identical class set vs load_pss_files
"""
import filecmp
from pathlib import Path

import pssc
from pssc.cli import main

SRC = "component pss_top { action A { rand bit[8] x; constraint x > 3; } }"


def _src(tmp_path):
    p = tmp_path / "m.pss"
    p.write_text(SRC)
    return str(p)


def test_sv_byte_parity_with_legacy(tmp_path):
    src = _src(tmp_path)
    legacy = tmp_path / "legacy"
    new = tmp_path / "new"
    pssc.generate_sv_files([src], str(legacy))
    code = main(["compile", src, "-t", "sv", "-o", str(new), "-q"])
    assert code == 0

    legacy_files = sorted(p.name for p in legacy.iterdir())
    new_files = sorted(p.name for p in new.iterdir())
    assert legacy_files == new_files
    for name in legacy_files:
        assert filecmp.cmp(legacy / name, new / name, shallow=False), \
            f"SV file {name} differs from legacy output"


def test_python_classset_parity_with_legacy(tmp_path):
    src = _src(tmp_path)
    legacy_reg = pssc.load_pss_files([src])
    res = pssc.compile(src, target="python")
    assert sorted(res.value.keys()) == sorted(legacy_reg.keys())


def test_python_cli_manifest_matches_registry(tmp_path):
    src = _src(tmp_path)
    out = tmp_path / "py"
    main(["compile", src, "-t", "python", "--emit", "repr", "-o", str(out), "-q"])
    manifest = (out / "pss_classes.txt").read_text().split()
    legacy_reg = pssc.load_pss_files([src])
    assert sorted(manifest) == sorted(legacy_reg.keys())
