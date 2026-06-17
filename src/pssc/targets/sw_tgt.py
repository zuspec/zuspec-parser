"""C (software) targets via ``zuspec-be-sw`` — Context-first, no ``zuspec-dataclasses``.

``c-host`` (output style 3): host-targeted C coroutine runtime. The translated PSS
IR ``Context`` is lowered (actions -> components, activities inlined) and handed to
``zuspec.be.sw.CGenerator.generate(ctx)``, which emits the C coroutine runtime.

When a single top-level activity-bearing action is identified (or named via
``--root-action``), the default backend ``main.c`` is replaced with a harness that
instantiates that action and drives its activity to completion via the timebase.
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import List, Optional

from .base import Target
from .sw_lower import to_sw_context, find_root_action
from ..ir import to_core_context


def _sanitize(name: str) -> str:
    """Mirror zuspec-be-sw's ``sanitize_c_name`` (``pss_top::Root`` -> ``pss_top__Root``)."""
    return re.sub(r"[^a-zA-Z0-9_]", "_", name)


def _resolve_root(core, requested: Optional[str]) -> Optional[str]:
    """Resolve the root action to a qualified ``type_m`` key."""
    if requested:
        if requested in core.type_m:
            return requested
        matches = [k for k in core.type_m if k.split("::")[-1] == requested]
        return matches[0] if len(matches) == 1 else None
    return find_root_action(core)


def _root_harness(root_qual: str) -> str:
    """C ``main`` that runs ``root_qual``'s activity to completion."""
    t = _sanitize(root_qual)          # C type / function prefix
    hdr = t.lower()                   # header file base name
    return f"""#include <stdlib.h>
#include "zsp_alloc.h"
#include "zsp_init_ctxt.h"
#include "zsp_timebase.h"
#include "{hdr}.h"

int main(int argc, char **argv) {{
    (void)argc; (void)argv;
    zsp_alloc_t alloc;
    zsp_alloc_malloc_init(&alloc);

    zsp_timebase_t tb;
    zsp_timebase_init(&tb, &alloc, ZSP_TIME_PS);

    zsp_init_ctxt_t ctxt;
    ctxt.alloc = &alloc;
    ctxt.timebase = &tb;

    {t} root;
    {t}_init(&ctxt, &root, "root", NULL);
    {t}_body(&root, &tb);
    zsp_timebase_run(&tb);
    return 0;
}}
"""


class CHostTarget(Target):
    name = "c-host"
    description = "Host C coroutine runtime via zuspec-be-sw (style 3)"

    def add_args(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "--root-action", dest="root_action", metavar="NAME", default=None,
            help="c-host: action whose activity the generated main runs "
            "(simple or qualified name; default: auto-detect the single top action)",
        )

    def run(self, ctx, opts: argparse.Namespace) -> List[Path]:
        from zuspec.be.sw import CGenerator

        core = getattr(ctx, "ir_context", None)
        if core is None:
            core = to_core_context(ctx)
        sw_ctx = to_sw_context(core)

        out = str(getattr(opts, "output_dir", ".") or ".")
        Path(out).mkdir(parents=True, exist_ok=True)
        files = list(CGenerator(output_dir=out).generate(sw_ctx))

        # Replace the default backend main.c with a root-activity harness.
        root = _resolve_root(core, getattr(opts, "root_action", None))
        if root is not None:
            main_c = Path(out) / "main.c"
            main_c.write_text(_root_harness(root))
            if main_c not in files:
                files.append(main_c)
        return files
