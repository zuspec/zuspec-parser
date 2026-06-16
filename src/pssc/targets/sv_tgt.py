"""SystemVerilog target (output style 1): SV classes solved by the SV constraint
solver.

Wraps the preserved PSS->SV lowering (``pssc.targets.sv``). The default emission
is byte-identical to the legacy :func:`pssc.generate_sv_files`, achieved by
delegating to the same ``_generate_sv_from_ctx`` code path.
"""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import List

from .base import Target


class SvTarget(Target):
    name = "sv"
    description = "SystemVerilog classes solved by the SV solver (style 1)"

    def add_args(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "--no-rt-pkg",
            dest="rt_pkg",
            action="store_false",
            default=True,
            help="sv target: do not emit the bundled zsp_rt_pkg.sv runtime package",
        )
        parser.add_argument(
            "--single-file",
            dest="sv_multi_file",
            action="store_false",
            default=True,
            help="sv target: emit one zsp_pkg.sv instead of one file per type",
        )

    def run(self, ctx, opts: argparse.Namespace) -> List[Path]:
        # Delegate to the exact legacy code path to guarantee output parity.
        from .. import _generate_sv_from_ctx

        return _generate_sv_from_ctx(
            ctx,
            str(getattr(opts, "output_dir", ".") or "."),
            multi_file=getattr(opts, "sv_multi_file", True),
            include_runtime=getattr(opts, "rt_pkg", True),
        )
