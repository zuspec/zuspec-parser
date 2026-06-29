"""Gate-1 guardrail: the `pssc` package imports, exposes its frozen public API,
and ships its data files (migration from zuspec-fe-pss)."""
from importlib.resources import files

import pytest

import pssc

FROZEN_API = [
    "Parser", "ParseException", "PssTranslationError",
    "load_pss", "load_pss_files", "generate_sv", "generate_sv_files",
    "AstToIrTranslator", "AstToIrContext", "IrToRuntimeBuilder", "ClassRegistry",
    "get_deps", "get_libs", "get_libdirs", "get_incdirs",
    # Phase 2 additions
    "compile", "to_core_context", "CompileResult", "CompileError",
]


@pytest.mark.parametrize("name", FROZEN_API)
def test_frozen_api_importable(name):
    assert hasattr(pssc, name), f"pssc.{name} missing"


def test_version_exposed():
    assert isinstance(pssc.__version__, str) and pssc.__version__


def test_data_files_resolvable():
    root = files("pssc")
    assert root.joinpath("share/sv/zsp_rt_pkg.sv").is_file()
    assert root.joinpath("std_libs/sml_pkg.pss").is_file()


def test_ast2ir_uses_ir_core_directly():
    """ast2ir must target zuspec.ir.core directly, not via zuspec.dataclasses."""
    import zuspec.ir.core as core
    import pssc.ast2ir as a
    assert a.ir is core
    src = files("pssc").joinpath("ast2ir.py").read_text()
    assert "from zuspec.dataclasses import ir" not in src


def test_no_dataclasses_ir_shim_in_pssc():
    """No production pssc module may import the IR via the zuspec.dataclasses shim.

    The canonical IR lives in zuspec.ir.core; importing it through
    ``from zuspec.dataclasses import ir`` is a legacy alias that re-couples pssc
    to zuspec-dataclasses.  Every pssc source file must target zuspec.ir.core
    directly (see docs/be-py-runtime-relocation-design.md, Phase 0).
    """
    import pathlib
    import pssc
    pkg_root = pathlib.Path(pssc.__file__).parent
    offenders = [
        str(p.relative_to(pkg_root))
        for p in pkg_root.rglob("*.py")
        if "from zuspec.dataclasses import ir" in p.read_text()
    ]
    assert not offenders, (
        "pssc modules still import the IR via the dataclasses shim: " + ", ".join(offenders)
    )


def test_import_pssc_does_not_pull_in_dataclasses():
    """``import pssc`` must not transitively import ``zuspec.dataclasses``.

    The Python runtime now lives in ``zuspec.be.py``; ``zuspec.dataclasses`` is a
    frontend that pssc depends on only for tests.  Importing pssc must stay free
    of it (see docs/be-py-runtime-relocation-design.md, Phase 4).  Run in a
    subprocess so an already-imported dataclasses (from another test) can't mask a
    regression.
    """
    import subprocess, sys, textwrap
    code = textwrap.dedent(
        """
        import sys
        import pssc  # noqa: F401
        leaked = sorted(
            m for m in sys.modules
            if m == 'zuspec.dataclasses' or m.startswith('zuspec.dataclasses.')
        )
        if leaked:
            print('LEAKED:' + ','.join(leaked))
            raise SystemExit(1)
        """
    )
    res = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)
    assert res.returncode == 0, (
        "import pssc pulled in zuspec.dataclasses:\n" + res.stdout + res.stderr
    )


def test_backends_import_clean_of_dataclasses():
    """Importing the Zuspec backends must not transitively import dataclasses.

    The Python/SV/C backends consume ``zuspec.ir.core`` and own their runtime;
    they reach the dataclasses frontend only via lazy, @zdc-authored-only paths.
    Importing them (as pssc does, lazily, per target) must stay clean.
    """
    import subprocess, sys, textwrap
    for backend in ("zuspec.be.py", "zuspec.be.py.builder", "zuspec.be.sv", "zuspec.be.sw"):
        code = textwrap.dedent(
            f"""
            import sys
            import {backend}  # noqa: F401
            leaked = [m for m in sys.modules
                      if m == 'zuspec.dataclasses' or m.startswith('zuspec.dataclasses.')]
            if leaked:
                print('LEAKED:' + ','.join(sorted(leaked)))
                raise SystemExit(1)
            """
        )
        res = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)
        assert res.returncode == 0, (
            f"import {backend} pulled in zuspec.dataclasses:\n" + res.stdout + res.stderr
        )
