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


class _DedupArgGroup:
    """Proxy over a parser whose ``add_argument`` skips already-registered
    options.

    All targets contribute their options to the single ``compile`` parser. Target
    *variants* commonly share inherited options (e.g. the SV family: ``sv-native``
    and ``sv-pure`` both declare ``--no-rt-pkg`` because ``sv-pure`` extends
    ``sv-native`` and calls ``super().add_args()``). Declaring a shared option more
    than once would raise ``argparse.ArgumentError``; this proxy makes the option
    register once (first wins) so the families coexist.
    """

    def __init__(self, parser: argparse.ArgumentParser):
        self._parser = parser

    def add_argument(self, *args, **kwargs):
        existing = self._parser._option_string_actions
        if any(isinstance(a, str) and a.startswith("-") and a in existing
               for a in args):
            return None
        return self._parser.add_argument(*args, **kwargs)

    def __getattr__(self, name):
        return getattr(self._parser, name)


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
    # How far to lower the PSS 3.1 §21.14.1 masked register writes. The
    # field-wise forms always reduce to write_val_masked; this decides whether
    # that survives to the backend or is spelled out as the read/modify/write
    # the LRM defines it to be. Behaviour is identical either way.
    c.add_argument(
        "--reg-rmw", dest="reg_rmw", choices=("native", "expand"),
        default="native",
        help="lowering for masked register writes: 'native' emits "
        "write_val_masked; 'expand' emits read_val + write_val, for a backend "
        "with no read-modify-write primitive; default: native",
    )
    # Shared across the SV export targets (sv-native oo_api, sv-dpi-bridge):
    # which actions to expose as entry points. Added once here so multiple
    # targets can consume it without colliding in the single compile parser.
    c.add_argument(
        "--export-action", dest="export_actions", action="append",
        metavar="NAME", default=None,
        help="action to expose as an export entry point (repeatable; "
        "default: the auto-detected single root action)",
    )
    # per-target options. Shared options inherited across target variants (e.g.
    # the SV family) are registered once via the dedup proxy.
    _targets.discover()
    _c_dedup = _DedupArgGroup(c)
    for name in _targets.list_targets():
        _targets.get(name).add_args(_c_dedup)
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

    # --- sv-core-path ------------------------------------------------------
    scp = sub.add_parser(
        "sv-core-path",
        help="print the path to the bundled SV core package (pssc_reg_pkg)",
    )
    scp.add_argument(
        "--file", action="store_true",
        help="print the path to pssc_reg_pkg.sv instead of its directory",
    )
    scp.set_defaults(func=_cmd_sv_core_path)

    # --- c-core-path / cpp-core-path --------------------------------------
    ccp = sub.add_parser(
        "c-core-path",
        help="print the directory of the bundled C core seam headers (pssc_mem*.h)",
    )
    ccp.add_argument(
        "--file", metavar="NAME", nargs="?", const=C_CORE_HEADER,
        help="print the path to a specific header (default: pssc_mem.h)",
    )
    ccp.set_defaults(func=_cmd_c_core_path)

    xcp = sub.add_parser(
        "cpp-core-path",
        help="print the directory of the bundled C++ core header (pssc_reg.hpp)",
    )
    xcp.add_argument(
        "--file", metavar="NAME", nargs="?", const=CPP_CORE_HEADER,
        help="print the path to a specific header (default: pssc_reg.hpp)",
    )
    xcp.set_defaults(func=_cmd_cpp_core_path)

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


#: Filename of the bundled SV core package under ``pssc/share/sv``.
SV_CORE_PKG = "pssc_reg_pkg.sv"


def sv_core_dir() -> Path:
    """Return the directory of the bundled SV core package (``pssc/share/sv``)."""
    from importlib.resources import files
    return Path(str(files("pssc") / "share" / "sv"))


def _cmd_sv_core_path(args: argparse.Namespace) -> int:
    d = sv_core_dir()
    print(d / SV_CORE_PKG if args.file else d)
    return 0


#: Default header names under ``pssc/share/c`` and ``pssc/share/cpp``.
C_CORE_HEADER = "pssc_mem.h"
CPP_CORE_HEADER = "pssc_reg.hpp"


def c_core_dir() -> Path:
    """Return the directory of the bundled C core seam headers (``pssc/share/c``)."""
    from importlib.resources import files
    return Path(str(files("pssc") / "share" / "c"))


def cpp_core_dir() -> Path:
    """Return the directory of the bundled C++ core header (``pssc/share/cpp``)."""
    from importlib.resources import files
    return Path(str(files("pssc") / "share" / "cpp"))


def _cmd_c_core_path(args: argparse.Namespace) -> int:
    d = c_core_dir()
    print(d / args.file if args.file else d)
    return 0


def _cmd_cpp_core_path(args: argparse.Namespace) -> int:
    d = cpp_core_dir()
    print(d / args.file if args.file else d)
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
