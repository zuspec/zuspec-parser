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


def register(target: Target, aliases=()) -> None:
    """Register a target instance under its ``name`` (and any ``aliases``)."""
    if not target.name:
        raise ValueError(f"{type(target).__name__} has no 'name'")
    _REGISTRY[target.name] = target
    for alias in aliases:
        _REGISTRY[alias] = target


def get(name: str) -> Target:
    """Return the registered target ``name`` or raise a clear ``KeyError``."""
    try:
        return _REGISTRY[name]
    except KeyError:
        avail = ", ".join(list_targets()) or "(none)"
        raise KeyError(f"unknown target '{name}'; available: {avail}") from None


def list_targets() -> List[str]:
    """Return the sorted canonical target names (aliases excluded)."""
    return sorted(name for name, t in _REGISTRY.items() if name == t.name)


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
    from .sv_pure_tgt import SvPureTarget
    from .progseq_tgt import ProgSeqTarget
    from .c_progseq_tgt import CProgSeqTarget
    from .cpp_progseq_tgt import CppProgSeqTarget
    from .sw_tgt import (CHostTarget, CHostPresolvedTarget,
                         CEmbeddedTarget, CEmbeddedPresolvedTarget, SvDpiTarget,
                         SvDpiBridgeTarget)

    register(PythonTarget())
    register(SvTarget(), aliases=("sv",))   # `sv` kept as a back-compat alias
    register(SvPureTarget())                # incremental-traversal pure-SV path
    # The operation-model family. Named `op-model-<kind>` so the three read as
    # one family and sort together; the former `<kind>-progseq` names are kept
    # as aliases so existing command lines and flows keep working.
    register(ProgSeqTarget(), aliases=("progseq", "sv-progseq"))
    register(CProgSeqTarget(), aliases=("progseq-c", "c-progseq"))
    register(CppProgSeqTarget(), aliases=("progseq-cpp", "cpp-progseq"))
    for tgt in (CHostTarget(), CHostPresolvedTarget(),
                CEmbeddedTarget(), CEmbeddedPresolvedTarget(), SvDpiTarget(),
                SvDpiBridgeTarget()):
        register(tgt)


_register_builtins()
