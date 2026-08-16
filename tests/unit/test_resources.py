"""Phase 4 (P4.T5): locating a package's runtime source.

Generated code is not self-contained -- it includes `pssc_reg_pkg.sv`,
`pssc_mem.h`, `pssc_reg.hpp`. Three backends each resolved that directory and
copied from it, and each had its own chance to forget `--no-core-copy` or to
fail unhelpfully on a header missing from a wheel. `pssc.resources` is the one
lookup, and it takes a PACKAGE so a plugin can ship its own.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import pytest

from pssc import resources


# -- the lookup --------------------------------------------------------------

@pytest.mark.parametrize("lang,expect", [
    ("sv", "pssc_reg_pkg.sv"),
    ("c", "pssc_mem.h"),
    ("cpp", "pssc_reg.hpp"),
])
def test_core_dir_resolves_for_pssc(lang, expect):
    d = resources.core_dir("pssc", lang)
    assert d.is_dir()
    assert (d / expect).is_file()


def test_core_file_returns_the_file():
    p = resources.core_file("pssc_mem.h", "pssc", "c")
    assert p.is_file() and p.name == "pssc_mem.h"


def test_core_files_preserves_order():
    names = ["pssc_mem.h", "pssc_chan.h", "pssc_env.h"]
    got = resources.core_files(names, "pssc", "c")
    assert [p.name for p in got] == names


def test_an_absent_language_names_the_package_and_the_path():
    with pytest.raises(resources.ResourceError) as exc:
        resources.core_dir("pssc", "cobol")
    msg = str(exc.value)
    assert "pssc" in msg and "cobol" in msg
    assert "package data" in msg      # says what to do about it


def test_an_absent_package_is_reported_as_such():
    with pytest.raises(resources.ResourceError) as exc:
        resources.core_dir("no_such_distribution_xyz", "c")
    assert "not importable" in str(exc.value)


def test_a_missing_file_blames_packaging_not_the_copy():
    """A runtime header missing from a wheel is a packaging bug, and its
    diagnostic should say so rather than surfacing as a shutil error naming a
    file nobody wrote."""
    with pytest.raises(resources.ResourceError) as exc:
        resources.core_file("pssc_nonexistent.h", "pssc", "c")
    msg = str(exc.value)
    assert "pssc_nonexistent.h" in msg and "package-data" in msg


def test_a_plugin_package_resolves_its_own_share(tmp_path, monkeypatch):
    """The reason the lookup takes a package name at all."""
    pkg = tmp_path / "acme_pssc"
    (pkg / "share" / "c").mkdir(parents=True)
    (pkg / "__init__.py").write_text("")
    (pkg / "share" / "c" / "acme_rt.h").write_text("/* acme */")
    monkeypatch.syspath_prepend(str(tmp_path))
    import importlib
    importlib.invalidate_caches()

    assert resources.core_dir("acme_pssc", "c").is_dir()
    assert resources.core_file("acme_rt.h", "acme_pssc", "c").is_file()


# -- the CLI wrappers --------------------------------------------------------

def test_the_cli_accessors_are_thin_wrappers():
    """`pssc <lang>-core-path` is published surface; it must keep working and
    must not become a second lookup."""
    from pssc import cli
    assert cli.sv_core_dir() == resources.core_dir("pssc", "sv")
    assert cli.c_core_dir() == resources.core_dir("pssc", "c")
    assert cli.cpp_core_dir() == resources.core_dir("pssc", "cpp")


# -- Target.install_core -----------------------------------------------------

class _Model:
    """The two attributes `install_core` touches."""
    def __init__(self, out_dir):
        self.out_dir = Path(out_dir)


def _target(names, lang="c"):
    from pssc.targets.op_model import OpModelTarget

    class _T(OpModelTarget):
        name = "x-core-test"
        core_lang = lang

        def core_file_names(self, model, opts):
            return list(names)

        def emit(self, model, opts):
            return []

    return _T()


def test_core_files_copies_and_reports_in_order(tmp_path):
    names = ["pssc_mem.h", "pssc_chan.h"]
    written = _target(names).install_core(_Model(tmp_path),
                                          argparse.Namespace())
    assert [p.name for p in written] == names
    for p in written:
        assert p.is_file() and p.read_text()


def test_no_core_copy_is_honoured_once_for_the_family(tmp_path):
    """It was three independent `if copy_core:` blocks; a fourth backend would
    have written a fourth, and a backend that forgot would have written the
    files anyway with nothing failing."""
    opts = argparse.Namespace(progseq_core_copy=False)
    written = _target(["pssc_mem.h"]).install_core(_Model(tmp_path), opts)
    assert written == []
    assert list(tmp_path.iterdir()) == []


def test_a_target_needing_no_runtime_source_copies_nothing(tmp_path):
    written = _target([]).install_core(_Model(tmp_path), argparse.Namespace())
    assert written == []


def test_the_default_target_ships_nothing(tmp_path):
    """`core_file_names` returning [] is the default, so a target that has no
    runtime source says nothing and gets nothing."""
    from pssc.targets.op_model import OpModelTarget

    class _T(OpModelTarget):
        name = "x-bare"
        def emit(self, model, opts):
            return []

    assert _T().install_core(_Model(tmp_path), argparse.Namespace()) == []


def test_the_builtin_targets_declare_their_runtime_source():
    from pssc import targets
    for name, lang in (("op-model-sv", "sv"), ("op-model-c", "c"),
                       ("op-model-cpp", "cpp")):
        assert targets.get(name).core_lang == lang
