"""A minimal out-of-tree pssc target.

Deliberately small. It is not a demonstration of how to write a good backend --
it exists so pssc's own tests can prove that a target living in another
distribution is discovered, listed, selected, given options and asked to
generate, using nothing but the public surface: `pssc.targets.Target`,
`Target.opt`, and `pssc.targets.call_legality.register_extension`.

Anything this file needs that pssc does not export is a gap in the plugin API,
and that is the point of keeping it honest.
"""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import List

from pssc.targets import Target
from pssc.targets.call_legality import (BOTH, Disposition, Entry,
                                        register_extension)


class FixtureTarget(Target):
    name = "fixture"
    description = "test-fixture target (pssc-fixture-plugin)"
    aliases = ("fixture-alias",)

    def __init__(self):
        # Tier 2 is declared here rather than at module scope, so it follows
        # the target's lifecycle instead of the module's. Import happens once
        # per process; construction happens once per registration, which is
        # what makes the two stay in step -- a re-discovery that re-registers
        # the target must also re-register what the target can render.
        register_extension(self.name, [
            Entry("print", Disposition.UTILITY, BOTH, lrm="21.1.2"),
        ], replace=True)

    def add_args(self, parser: argparse.ArgumentParser) -> None:
        # Namespaced, as the option policy requires of a plugin.
        parser.add_argument(
            "--fixture-note", dest="fixture_note", default="",
            help="fixture: text to include in the generated file",
        )

    def run(self, ctx, opts: argparse.Namespace) -> List[Path]:
        out_dir = Path(getattr(opts, "output_dir", "."))
        out_dir.mkdir(parents=True, exist_ok=True)
        # `-X` is the un-namespaced escape hatch; reading it here is what proves
        # a plugin can take options without claiming a `--flag`.
        style = self.opt(opts, "fixture-style", default="plain",
                         choices=("plain", "loud"))
        note = getattr(opts, "fixture_note", "")
        types = sorted(getattr(ctx, "type_map", {}) or {})
        body = "\n".join(t.upper() if style == "loud" else t for t in types)
        path = out_dir / "fixture.txt"
        path.write_text(f"# fixture target: {note}\n{body}\n")
        return [path]
