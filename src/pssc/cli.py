"""``pssc`` command-line entry point.

Subcommands:
  * ``compile`` — sources -> selected target
  * ``parse``   — front-end only; optionally dump canonical IR as YAML
  * ``targets`` — list available targets

Exit codes: ``0`` success, ``1`` user error (bad target, parse/translate
failure), ``2`` internal error.
"""
from __future__ import annotations

import argparse
import sys
import traceback
from pathlib import Path

from .__version__ import version
from . import driver
from . import targets as _targets
from .ir import dump_ir


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="pssc", description="The PSS compiler")
    p.add_argument("--version", action="version", version=f"pssc {version}")
    sub = p.add_subparsers(dest="command")

    # --- compile -----------------------------------------------------------
    c = sub.add_parser("compile", help="compile PSS sources to a target")
    c.add_argument("sources", nargs="+", help="PSS source file(s)")
    c.add_argument(
        "-t", "--target", default="python",
        help="output target (see `pssc targets`); default: python",
    )
    c.add_argument(
        "-o", "--output-dir", dest="output_dir", default=".",
        help="directory for generated files (created if absent); default: .",
    )
    c.add_argument(
        "--dump-ir", dest="dump_ir", metavar="FILE",
        help="also write the canonical IR Context as YAML to FILE",
    )
    c.add_argument("-q", "--quiet", action="store_true",
                   help="do not print written file paths")
    # per-target options (names are unique across targets)
    _targets.discover()
    for name in _targets.list_targets():
        _targets.get(name).add_args(c)
    c.set_defaults(func=_cmd_compile)

    # --- parse -------------------------------------------------------------
    pa = sub.add_parser("parse", help="run the front end only; optionally dump IR")
    pa.add_argument("sources", nargs="+", help="PSS source file(s)")
    pa.add_argument(
        "--dump-ir", dest="dump_ir", metavar="FILE",
        help="write the canonical IR Context as YAML to FILE",
    )
    pa.add_argument("-q", "--quiet", action="store_true")
    pa.set_defaults(func=_cmd_parse)

    # --- targets -----------------------------------------------------------
    t = sub.add_parser("targets", help="list available targets")
    t.set_defaults(func=_cmd_targets)

    return p


def _cmd_compile(args: argparse.Namespace) -> int:
    res = driver.compile(args.sources, target=args.target, opts=args,
                         raise_on_error=True)
    if args.dump_ir:
        Path(args.dump_ir).write_text(dump_ir(res.context))
    if not args.quiet:
        for path in res.outputs:
            print(path)
    return 0


def _cmd_parse(args: argparse.Namespace) -> int:
    ctx = driver.translate(args.sources)
    if ctx.errors:
        raise driver.CompileError(
            f"PSS translation failed with {len(ctx.errors)} error(s)", ctx.errors
        )
    if args.dump_ir:
        Path(args.dump_ir).write_text(dump_ir(ctx.ir_context))
        if not args.quiet:
            print(f"wrote {args.dump_ir}")
    elif not args.quiet:
        print(f"parsed OK: {len(ctx.type_map)} types")
    return 0


def _cmd_targets(args: argparse.Namespace) -> int:
    _targets.discover()
    for name in _targets.list_targets():
        print(f"{name:24} {_targets.get(name).description}")
    return 0


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    parser = build_parser()
    args = parser.parse_args(argv)

    func = getattr(args, "func", None)
    if func is None:
        parser.print_help()
        return 0

    try:
        return func(args)
    except driver.CompileError as e:
        print(f"pssc: error: {e}", file=sys.stderr)
        for err in e.errors:
            print(f"  {err}", file=sys.stderr)
        return 1
    except Exception:  # pragma: no cover - internal error path
        traceback.print_exc()
        print("pssc: internal error (see traceback above)", file=sys.stderr)
        return 2


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
