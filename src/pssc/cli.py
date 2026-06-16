"""pssc command-line entry point.

Phase 1 ships a minimal stub that supports ``--version`` so the ``pssc``
console script is wired end-to-end. Phase 2 (task 2.6) replaces this with the
full argparse CLI: ``compile`` / ``parse`` / ``targets`` subcommands.
"""
import argparse
import sys

from .__version__ import version


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    parser = argparse.ArgumentParser(prog="pssc", description="The PSS compiler")
    parser.add_argument("--version", action="version", version=f"pssc {version}")
    # Phase 2: compile / parse / targets subcommands land here.
    parser.parse_args(argv)
    parser.print_help()
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
