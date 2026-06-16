"""pssc code-generation targets.

Holds the :class:`~pssc.targets.base.Target` ABC and a small internal registry.
Built-in targets register themselves when this package is imported; third-party
targets can later be discovered via the ``pssc.targets`` entry-point group (see
:func:`discover`, off by default until Phase 4).
"""
from __future__ import annotations

from typing import Dict, List

from .base import Target

__all__ = ["Target", "register", "get", "list_targets", "discover"]

_REGISTRY: Dict[str, Target] = {}
_discovered = False


def register(target: Target) -> None:
    """Register a target instance under its ``name``."""
    if not target.name:
        raise ValueError(f"{type(target).__name__} has no 'name'")
    _REGISTRY[target.name] = target


def get(name: str) -> Target:
    """Return the registered target ``name`` or raise a clear ``KeyError``."""
    try:
        return _REGISTRY[name]
    except KeyError:
        avail = ", ".join(list_targets()) or "(none)"
        raise KeyError(f"unknown target '{name}'; available: {avail}") from None


def list_targets() -> List[str]:
    """Return the sorted names of all registered targets."""
    return sorted(_REGISTRY)


def discover() -> None:
    """Load third-party targets from the ``pssc.targets`` entry-point group.

    No-op stub for now (entry-point discovery is enabled in Phase 4); kept so the
    CLI/driver can call it unconditionally without behavior change.
    """
    global _discovered
    if _discovered:
        return
    _discovered = True
    # Phase 4:
    #   from importlib.metadata import entry_points
    #   for ep in entry_points(group="pssc.targets"):
    #       register(ep.load()())


def _register_builtins() -> None:
    from .python_tgt import PythonTarget
    from .sv_tgt import SvTarget
    from .sw_tgt import CHostTarget

    for tgt in (PythonTarget(), SvTarget(), CHostTarget()):
        register(tgt)


_register_builtins()
