"""C (software) targets via ``zuspec-be-sw`` — Context-first, no ``zuspec-dataclasses``.

``c-host`` (output style 3): host-targeted C coroutine runtime. The translated PSS
IR ``Context`` is lowered (actions -> components) and handed to
``zuspec.be.sw.CGenerator.generate(ctx)``, which emits the C coroutine runtime.
"""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import List

from .base import Target
from .sw_lower import to_sw_context
from ..ir import to_core_context


class CHostTarget(Target):
    name = "c-host"
    description = "Host C coroutine runtime via zuspec-be-sw (style 3)"

    def run(self, ctx, opts: argparse.Namespace) -> List[Path]:
        from zuspec.be.sw import CGenerator

        core = getattr(ctx, "ir_context", None)
        if core is None:
            core = to_core_context(ctx)
        sw_ctx = to_sw_context(core)

        out = str(getattr(opts, "output_dir", ".") or ".")
        Path(out).mkdir(parents=True, exist_ok=True)
        return list(CGenerator(output_dir=out).generate(sw_ctx))
