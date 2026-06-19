"""SystemVerilog target (output style 1): SV classes solved by the SV constraint
solver.

Wraps the preserved PSS->SV lowering (``pssc.targets.sv``). Two package shapes
are available via ``--projection``:

  * ``oo_api`` (default) -- an interface-class export API (``import_api_if`` /
    ``export_api_if``) plus a factory, driven by an external testbench:
    ``export_api_if ep = pss_top::type_id().create(imp); ep.Entry();``
  * ``harness`` -- the legacy standalone ``zsp_test_top`` module (self-contained,
    no testbench).
"""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import List

from .base import Target


class SvTarget(Target):
    name = "sv-native"
    description = "Pure SystemVerilog classes solved by the SV solver (style 1)"

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
        parser.add_argument(
            "--projection",
            dest="sv_projection",
            choices=("oo_api", "harness"),
            default="oo_api",
            help="sv target: package shape -- 'oo_api' (export API + factory, "
            "default) or 'harness' (standalone zsp_test_top module)",
        )
        # `--export-action` is the shared compile-level option (cli.build_parser);
        # consumed below via opts.export_actions.
        parser.add_argument(
            "--package-name",
            dest="sv_package_name",
            default="zsp_gen_pkg",
            help="sv target: name of the generated package (default: zsp_gen_pkg)",
        )

    def run(self, ctx, opts: argparse.Namespace) -> List[Path]:
        from .. import _generate_sv_from_ctx

        return _generate_sv_from_ctx(
            ctx,
            str(getattr(opts, "output_dir", ".") or "."),
            multi_file=getattr(opts, "sv_multi_file", True),
            include_runtime=getattr(opts, "rt_pkg", True),
            projection=getattr(opts, "sv_projection", "oo_api"),
            export_actions=getattr(opts, "export_actions", None),
            package_name=getattr(opts, "sv_package_name", "zsp_gen_pkg"),
        )
