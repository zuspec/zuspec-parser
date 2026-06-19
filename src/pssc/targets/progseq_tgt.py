"""``sv-progseq`` target: generate a reusable SystemVerilog programming API from
a PSS component tree.

Transforms the subtree rooted at ``--root`` into an SV package: register value
structs + register-model classes, per-component export-API interface classes, an
import-API interface (extends the core ``pss_mem_if``), implementation
classes, a parameterized import adapter, and a factory.

Design: design/pss-programming-seq-gen-design.md
Plan:   design/pss-programming-seq-gen-impl-plan.md
"""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import List, Optional

from .base import Target


class ProgSeqTarget(Target):
    name = "sv-progseq"
    description = "SystemVerilog programming-sequence API generated from a component tree"

    def add_args(self, parser: argparse.ArgumentParser) -> None:
        # Note: option names are global across the shared `compile` parser, so
        # `--root` cannot be argparse-`required` (it would break other targets);
        # it is validated in run() when this target is selected.
        # --root and --no-core-copy are shared by all progseq targets (sv/c/cpp),
        # since add_args contributes to one global `compile` parser.
        parser.add_argument(
            "--root", dest="progseq_root", metavar="COMP",
            help="progseq: root component type to generate the API for",
        )
        parser.add_argument(
            "--package", dest="progseq_package", metavar="NAME",
            help="sv-progseq: generated package name (default: <root>_pkg)",
        )
        parser.add_argument(
            "--no-core-copy", dest="progseq_core_copy", action="store_false",
            default=True,
            help="progseq: do not copy the core seam header(s) into the output dir",
        )

    # -- helpers ------------------------------------------------------------

    @staticmethod
    def _resolve_root(ctx, root_name: str):
        """Resolve the root component datatype from the type table by name.

        Accepts either the bare name (``wb_dma_c``) or a qualified name
        (``pkg::wb_dma_c``). Raises ValueError with available candidates.
        """
        tm = getattr(ctx, "type_map", {}) or {}
        if root_name in tm:
            return tm[root_name]
        # try suffix match against qualified names
        cands = [n for n in tm if n.split("::")[-1] == root_name]
        if len(cands) == 1:
            return tm[cands[0]]
        if len(cands) > 1:
            raise ValueError(
                f"ambiguous --root '{root_name}'; matches: {', '.join(sorted(cands))}")
        comps = sorted({n for n, dt in tm.items()
                        if type(dt).__name__ == "DataTypeComponent"})
        raise ValueError(
            f"unknown --root '{root_name}'; available components: "
            + (", ".join(comps) or "(none)"))

    # -- entry point --------------------------------------------------------

    def run(self, ctx, opts: argparse.Namespace) -> List[Path]:
        root_name: Optional[str] = getattr(opts, "progseq_root", None)
        if not root_name:
            raise ValueError("sv-progseq requires --root <component>")

        root = self._resolve_root(ctx, root_name)

        pkg_name = getattr(opts, "progseq_package", None) or f"{root_name}_pkg"
        out_dir = Path(str(getattr(opts, "output_dir", ".") or "."))
        copy_core = getattr(opts, "progseq_core_copy", True)

        from .progseq_gen import generate
        return generate(ctx, root, pkg_name, out_dir, copy_core=copy_core)
