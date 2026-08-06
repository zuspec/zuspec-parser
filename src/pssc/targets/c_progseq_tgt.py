"""``c-progseq`` target: generate a reusable C programming API from a PSS
component tree.

Transforms the subtree rooted at ``--root`` into a C header (+ optional ``.c``):
register value unions, baked inline register accessors, per-component export
functions, and a component struct + factory. The memory-access seam is selected
by ``--link-style`` (vtable / direct / mmio); the register accessors and every
operation body are emitted identically across the three styles.

Design: design/pss-c-cpp-progseq-gen-design.md (§3)
Plan:   design/pss-c-cpp-progseq-gen-impl-plan.md
"""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import List, Optional

from .base import Target
from .progseq_tgt import ProgSeqTarget


class CProgSeqTarget(Target):
    name = "c-progseq"
    description = "C programming-sequence API generated from a component tree"

    def add_args(self, parser: argparse.ArgumentParser) -> None:
        # --root and --no-core-copy are contributed by ProgSeqTarget (shared
        # across all progseq targets on the one `compile` parser). Add only the
        # C-specific options here.
        parser.add_argument(
            "--prefix", dest="c_prefix", metavar="NAME",
            help="c-progseq: symbol/file prefix (default: root name sans _c)",
        )
        parser.add_argument(
            "--link-style", dest="c_link_style",
            choices=("vtable", "direct", "mmio"), default="vtable",
            help="c-progseq: memory-access seam (default: vtable)",
        )
        parser.add_argument(
            "--reg-style", dest="c_reg_style",
            choices=("bitfields", "accessors"), default="bitfields",
            help="c-progseq: register value layout (default: bitfields, LE)",
        )
        parser.add_argument(
            "--header-only", dest="c_header_only", action="store_true",
            default=False,
            help="c-progseq: emit a single self-contained .h (forced for mmio)",
        )

    # -- helpers ------------------------------------------------------------

    @staticmethod
    def default_prefix(root_name: str) -> str:
        """Default symbol prefix: the root name with a trailing ``_c`` stripped."""
        return root_name[:-2] if root_name.endswith("_c") else root_name

    # -- entry point --------------------------------------------------------

    def run(self, ctx, opts: argparse.Namespace) -> List[Path]:
        root_name: Optional[str] = getattr(opts, "progseq_root", None)
        if not root_name:
            raise ValueError("c-progseq requires --root <component>")

        ProgSeqTarget._apply_ctor_name(opts)
        root = ProgSeqTarget._resolve_root(ctx, root_name)

        prefix = getattr(opts, "c_prefix", None) or self.default_prefix(
            root_name.split("::")[-1])
        link_style = getattr(opts, "c_link_style", "vtable")
        reg_style = getattr(opts, "c_reg_style", "bitfields")
        header_only = getattr(opts, "c_header_only", False) or link_style == "mmio"
        out_dir = Path(str(getattr(opts, "output_dir", ".") or "."))
        copy_core = getattr(opts, "progseq_core_copy", True)

        from .c.c_progseq_gen import generate
        return generate(ctx, root, prefix, out_dir,
                        link_style=link_style, reg_style=reg_style,
                        header_only=header_only, copy_core=copy_core)
