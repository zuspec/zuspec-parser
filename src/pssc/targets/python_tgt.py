"""Python target (output style 6): live ``zdc`` Python classes for early
evaluation/testing.

Wraps :class:`pssc.runtime.IrToRuntimeBuilder` to turn the translated IR into a
:class:`pssc.runtime.ClassRegistry`. The registry is exposed in-memory via the
driver's ``CompileResult.value``; ``--emit`` controls the on-disk artifact.
"""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import List

from .base import Target
from ..runtime import IrToRuntimeBuilder


class PythonTarget(Target):
    name = "python"
    description = "Live Python (zdc) classes for early evaluation (style 6)"

    def add_args(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "--emit",
            choices=("none", "repr", "pickle"),
            default="none",
            help="python target: on-disk artifact to write "
            "(none: in-memory only; repr: class-name manifest; "
            "pickle: pickled class-name manifest). Default: none.",
        )

    def run(self, ctx, opts: argparse.Namespace) -> List[Path]:
        registry = IrToRuntimeBuilder(ctx).build()
        # surface the live registry to the driver (CompileResult.value)
        self._last_value = registry

        emit = getattr(opts, "emit", "none")
        if emit == "none":
            return []

        out = Path(getattr(opts, "output_dir", ".") or ".")
        out.mkdir(parents=True, exist_ok=True)
        names = sorted(registry.keys())

        if emit == "repr":
            path = out / "pss_classes.txt"
            path.write_text("\n".join(names) + ("\n" if names else ""))
            return [path]

        # emit == "pickle": a portable manifest of class names (the dynamically
        # built classes themselves are not reliably picklable).
        import pickle

        path = out / "pss_classes.pkl"
        path.write_bytes(pickle.dumps(names))
        return [path]
