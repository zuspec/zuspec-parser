"""The :class:`Target` ABC — the contract every pssc code-generation backend
implements.
"""
from __future__ import annotations

import abc
import argparse
from pathlib import Path
from typing import List


class Target(abc.ABC):
    """A pssc code-generation target.

    Subclasses set :attr:`name`, optionally contribute CLI options via
    :meth:`add_args`, and emit artifacts via :meth:`run`.
    """

    #: The ``--target`` selector name (e.g. ``"sv"``, ``"python"``).
    name: str = ""

    #: One-line description shown by ``pssc targets``.
    description: str = ""

    def add_args(self, parser: argparse.ArgumentParser) -> None:  # noqa: B027
        """Contribute target-specific options to the ``compile`` parser.

        Optional; the default contributes nothing. Option names must be unique
        across targets (they are all registered on the one ``compile`` parser).
        """

    @abc.abstractmethod
    def run(self, ctx, opts: argparse.Namespace) -> List[Path]:
        """Generate output for ``ctx`` under ``opts``; return written file paths.

        ``ctx`` is the PSS :class:`pssc.ast2ir.AstToIrContext`, which the driver
        enriches with ``ctx.ir_context`` — the canonical
        :class:`zuspec.ir.core.Context`. Built-in targets read the PSS context
        directly (the SV path needs ``parent_comp_names``; the Python path needs
        the whole context); external Phase-3 backends consume ``ctx.ir_context``.
        """
