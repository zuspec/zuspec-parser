"""A tier-3 target: a new emitter over a model pssc already elaborates.

Tier A restyles a backend and tier B overrides parts of one. This is the tier
above: the OUTPUT SHAPE is the plugin's own, so there is nothing to override --
but everything before emission is still pssc's. Parsing, translation, `--root`
resolution, the component walk, the offset fold, the register groups and the
call-legality gate have all already run by the time `emit` is called, and their
results are on the `OpModel` it is handed.

What that costs is this file. What it buys is that the listing describes the
same API the C target generates, because both read one elaboration.
"""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import List

from pssc.targets.op_model import OpModel, OpModelTarget


class ApiListingTarget(OpModelTarget):
    """One line per operation: `component  name(params) -> returns`."""

    name = "api-listing"
    description = "flat listing of the export API (pssc-fixture-plugin)"

    #: Everything a target needs and this file does not state -- the CLI
    #: options, what calls may be lowered, what the execution target can do --
    #: comes from the ancestor. Without it a legal `print` in a model would be
    #: reported as an unknown function by a target that never emits code.
    derives_from = "op-model-c"

    def add_args(self, parser: argparse.ArgumentParser) -> None:
        super().add_args(parser)        # --root, --ctor-name, --emit-manifest
        parser.add_argument(
            "--api-listing-sep", dest="api_listing_sep", default="  ",
            help="api-listing: column separator")

    def emit(self, model: OpModel, opts: argparse.Namespace) -> List[Path]:
        sep = getattr(opts, "api_listing_sep", "  ")
        lines = []
        for node in model.components:           # children first, then parents
            comp = node.dtype
            name = (getattr(comp, "name", "") or "").split("::")[-1]
            for fn in model.operations(comp):
                params = ", ".join(a.arg for a in fn.args.args)
                lines.append(f"{name}{sep}{fn.name}({params})")

        out = model.out_dir / "api_listing.txt"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text("\n".join(lines) + "\n")
        return [out]                            # in COMPILATION order
