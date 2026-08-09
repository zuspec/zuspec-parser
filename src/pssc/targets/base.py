"""The :class:`Target` ABC — the contract every pssc code-generation backend
implements.
"""
from __future__ import annotations

import abc
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from . import target_cfg as _target_cfg


class Target(abc.ABC):
    """A pssc code-generation target.

    Subclasses set :attr:`name`, optionally publish capabilities via
    :attr:`target_cfg`, optionally contribute CLI options via :meth:`add_args`,
    and emit artifacts via :meth:`run`.
    """

    #: The ``--target`` selector name (e.g. ``"op-model-sv"``, ``"python"``).
    name: str = ""

    #: One-line description shown by ``pssc targets``.
    description: str = ""

    #: Capabilities published to the model as ``target_cfg_pkg``, injected
    #: ahead of the user's sources -- or ``None`` to inject nothing, which
    #: leaves the model to take its own defaults.
    #:
    #: A target that sets this must supply EVERY constant in the contract
    #: version (see :mod:`pssc.targets.target_cfg`); a partial mapping is an
    #: error rather than a package with holes in it. ``None`` is the right
    #: value for a target whose capabilities have not been established --
    #: publishing a guess is worse than publishing nothing, because a model
    #: that sees the version marker trusts every flag beside it.
    target_cfg: Optional[Dict[str, bool]] = None

    def add_args(self, parser: argparse.ArgumentParser) -> None:  # noqa: B027
        """Contribute target-specific options to the ``compile`` parser.

        Optional; the default contributes nothing. Option names must be unique
        across targets (they are all registered on the one ``compile`` parser).
        """

    def prelude(self, opts: argparse.Namespace) -> List[Tuple[str, str]]:
        """PSS source units to process BEFORE the user's sources.

        Returns ``(name, text)`` pairs. ``name`` is reported in diagnostics and
        is deliberately not a real path.

        The default renders :attr:`target_cfg` as ``target_cfg_pkg``, with any
        ``--target-cfg NAME=VALUE`` overrides applied on top. Order matters and
        is the caller's responsibility to preserve: ``compile if`` reads
        constants only from previously-processed source units (PSS 3.1 §19.1.2),
        so a prelude that arrives late is not a diagnostic -- it is a silent
        fallback to whatever default the model declares.

        Override this to inject anything else a target needs in scope first.
        """
        overrides = _target_cfg.parse_overrides(
            getattr(opts, "target_cfg", None))
        if self.target_cfg is None and not overrides:
            return []
        cfg: Dict[str, bool] = dict(self.target_cfg or {})
        cfg.update(overrides)
        return [(_target_cfg.source_name(self.name),
                 _target_cfg.render(self.name, cfg))]

    @abc.abstractmethod
    def run(self, ctx, opts: argparse.Namespace) -> List[Path]:
        """Generate output for ``ctx`` under ``opts``; return written file paths.

        ``ctx`` is the PSS :class:`pssc.ast2ir.AstToIrContext`, which the driver
        enriches with ``ctx.ir_context`` — the canonical
        :class:`zuspec.ir.core.Context`. Built-in targets read the PSS context
        directly (the SV path needs ``parent_comp_names``; the Python path needs
        the whole context); external Phase-3 backends consume ``ctx.ir_context``.
        """
