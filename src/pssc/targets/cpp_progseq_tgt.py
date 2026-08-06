"""``cpp-progseq`` target: generate a reusable C++ programming API from a PSS
component tree.

Emits a single header: register value unions (shared with the C backend),
``pssc::reg<T,ACC>`` register-group classes, the pure-virtual export/import APIs,
and the component class + factory. The user subclasses ``pssc::mem_if`` (virtual
dispatch) -- no redirect trick.

Design: design/pss-c-cpp-progseq-gen-design.md (§4)
Plan:   design/pss-c-cpp-progseq-gen-impl-plan.md
"""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import List, Optional

from .base import Target
from .progseq_tgt import ProgSeqTarget
from .c_progseq_tgt import CProgSeqTarget


class CppProgSeqTarget(Target):
    name = "cpp-progseq"
    description = "C++ programming-sequence API generated from a component tree"

    def add_args(self, parser: argparse.ArgumentParser) -> None:
        # --root / --no-core-copy come from ProgSeqTarget (shared parser).
        parser.add_argument(
            "--namespace", dest="cpp_namespace", metavar="NAME",
            help="cpp-progseq: namespace + class prefix (default: root sans _c)",
        )
        parser.add_argument(
            "--dispatch", dest="cpp_dispatch",
            choices=("virtual", "template"), default="virtual",
            help="cpp-progseq: dispatch model (default: virtual)",
        )
        parser.add_argument(
            "--no-single-header", dest="cpp_single_header", action="store_false",
            default=True,
            help="cpp-progseq: (reserved) split declarations and bodies",
        )

    def run(self, ctx, opts: argparse.Namespace) -> List[Path]:
        root_name: Optional[str] = getattr(opts, "progseq_root", None)
        if not root_name:
            raise ValueError("cpp-progseq requires --root <component>")

        ProgSeqTarget._apply_ctor_name(opts)
        root = ProgSeqTarget._resolve_root(ctx, root_name)
        ns = getattr(opts, "cpp_namespace", None) or CProgSeqTarget.default_prefix(
            root_name.split("::")[-1])
        dispatch = getattr(opts, "cpp_dispatch", "virtual")
        out_dir = Path(str(getattr(opts, "output_dir", ".") or "."))
        copy_core = getattr(opts, "progseq_core_copy", True)

        from .cpp.cpp_progseq_gen import generate
        return generate(ctx, root, ns, out_dir, dispatch=dispatch,
                        copy_core=copy_core)
