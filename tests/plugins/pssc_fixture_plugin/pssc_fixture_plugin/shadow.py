"""An entry point that tries to take a built-in's name without saying so.

The single most damaging plugin bug, because it is the one with no symptom: the
user runs `pssc compile -t op-model-c`, gets output, and it came from somewhere
else. Registration refuses it; `replaces = ("op-model-c",)` would allow it.
"""
from __future__ import annotations

from pathlib import Path
from typing import List

from pssc.targets import Target


class ShadowTarget(Target):
    name = "op-model-c"
    description = "fixture: an accidental shadow of a built-in"

    def run(self, ctx, opts) -> List[Path]:   # pragma: no cover - never reached
        raise AssertionError(
            "the shadowing target ran; registration should have refused it")
