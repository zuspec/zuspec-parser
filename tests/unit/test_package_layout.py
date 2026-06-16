"""Gate-1 guardrail: the `pssc` package imports, exposes its frozen public API,
and ships its data files (migration from zuspec-fe-pss)."""
from importlib.resources import files

import pytest

import pssc

FROZEN_API = [
    "Parser", "PssAnnotation", "ParseException", "PssTranslationError",
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
