"""Smoke-test: parse → IR → SV generation for every bundled PSS test pattern.

Patterns live in ``packages/zuspec-fe-pss/tests/patterns/``.  Each ``.pss``
file is an independent, original model (not copyrighted third-party source)
that exercises a distinct feature of the PSS-to-SV lowering pipeline.

The test verifies:
  - The PSS source parses and links without error
  - The IR translator produces no error markers
  - pss_to_sv() produces at least one SV node
  - The emitted SV text contains a ``class pss_top`` declaration
  - No Python exception is raised during lowering

Tests are parametrized per file so each pattern appears as a distinct item
in the pytest report and can be targeted individually.

Pattern coverage
----------------
hello_world.pss         Basic component/action, rand fields, range constraints,
                        exec body with message()
producer_consumer.pss   Buffer flow objects, produce/consume, activity bind
parallel_resources.pss  Resource pools (lock), parallel fork/join, repeat
pipeline_stream.pss     Stream flow objects, schedule block, labeled traversals,
                        abstract action, inheritance
select_weighted.pss     Weighted select, conditional guards, if/else, repeat
nested_components.pss   Component hierarchy, sub-component nesting, struct fields
"""
from __future__ import annotations

import pathlib
from typing import List

import pytest

from pssc import Parser, AstToIrTranslator
from zuspec.be.sv.ir.sv_emit import SVEmitter
from pssc.targets.sv.pss_to_sv import pss_to_sv

# ---------------------------------------------------------------------------
# Locate pattern files
# ---------------------------------------------------------------------------
# File: packages/zuspec-fe-pss/tests/unit/sv/test_modeling_patterns.py
# parents[0]=sv  [1]=unit  [2]=tests  [3]=zuspec-fe-pss  [4]=packages
_TESTS_ROOT = pathlib.Path(__file__).parents[2]   # …/tests/
_PATTERNS_DIR = _TESTS_ROOT / "patterns"

assert _PATTERNS_DIR.is_dir(), f"Patterns directory not found: {_PATTERNS_DIR}"

_PATTERN_FILES: List[pathlib.Path] = sorted(_PATTERNS_DIR.glob("*.pss"))
assert _PATTERN_FILES, f"No .pss files in {_PATTERNS_DIR}"


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    "pss_file",
    _PATTERN_FILES,
    ids=[f.stem for f in _PATTERN_FILES],
)
def test_pattern_generates_sv(pss_file: pathlib.Path):
    """Parse → IR → SV generation succeeds for *pss_file*."""
    # --- Parse ---
    parser = Parser()
    parser.parse([str(pss_file)])
    ast_root = parser.link()

    # --- IR translation ---
    ctx = AstToIrTranslator().translate(ast_root, annotations=parser.annotations)
    assert not ctx.errors, (
        f"IR translation errors in {pss_file.name}:\n"
        + "\n".join(str(e) for e in ctx.errors)
    )

    # --- SV lowering ---
    sv_nodes = pss_to_sv(ctx)
    assert sv_nodes, f"pss_to_sv() returned no nodes for {pss_file.name}"

    # --- Emit and spot-check ---
    sv_text = SVEmitter().emit_all(sv_nodes)
    assert "class pss_top" in sv_text, (
        f"No 'class pss_top' in generated SV for {pss_file.name}"
    )

    # Report stats (visible with pytest -s or in CI logs)
    user_classes = sv_text.count("\nclass ")
    print(f"\n  [{pss_file.stem}] {len(sv_nodes)} SV nodes, "
          f"{user_classes} classes, {len(sv_text)} chars")
