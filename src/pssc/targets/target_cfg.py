"""``target_cfg_pkg`` -- the PSS prelude a target injects to describe itself.

A portable operation model has to compile against targets with different
capabilities: can the runtime suspend a thread, does the image carry a solver.
Those are facts about the EXECUTION TARGET, not about the device being
modelled, and they have exactly one value per build. Before this existed, a
project encoded them by hand-selecting between two copies of a config package
and excluding one from the fileset -- a choice every build had to restate.

A pssc target now answers the question itself, by contributing a source unit
that is processed AHEAD of the user's sources. A model reads the answer with a
plain ``compile if`` and never has to know which tool supplied it.

WHAT IS EMITTED
---------------

::

    package target_cfg_pkg {
        static const int  TARGET_CFG_VERSION  = 2;
        static const bool HAVE_EVENT_WAIT     = true;
        static const bool HAVE_RUNTIME_SOLVER = true;
    }

``TARGET_CFG_VERSION`` is the marker a model tests for. ``compile has`` needs a
member path, so there is no way to ask "does this package exist"; the version
constant is what a model names instead, and making it a version rather than a
bare CONFIGURED flag lets the contract grow.

WHAT ``HAVE_EVENT_WAIT`` ASKS, AND WHAT IT DOES NOT
---------------------------------------------------

It asks ONE question: *can a caller suspend until another party posts an
event?* Concretely, is ``channel_c``'s blocking ``get``/``put`` available.

It deliberately does NOT ask whether a caller may spin. Every target can spin,
including a bare-metal single-threaded one, so a polling wait needs no
capability at all -- see ``procedural_yield_stmt``, which every backend lowers
(to a scheduler yield on a threaded target, to nothing on a bare-metal one).

Contract v1 called this ``HAVE_BLOCKING`` and conflated the two: a target that
merely had no scheduler answered "false" and thereby deleted every operation
that waits, including the ones that could have polled. A model built on v2
keeps its whole operation surface on both kinds of target and varies only the
wait PRIMITIVE. The version bump is what makes the rename loud: a provider
still publishing ``HAVE_BLOCKING`` is rejected by :func:`render` rather than
silently taking a default.

THE COMPLETENESS OBLIGATION
---------------------------

A provider that declares ``TARGET_CFG_VERSION = N`` declares EVERY constant in
contract version N. :func:`render` enforces this rather than filling in
defaults, and the enforcement is the point: it is what lets a model write

    compile if (compile has(target_cfg_pkg::TARGET_CFG_VERSION)) {
        static const bool HAS_EVENT_WAIT = target_cfg_pkg::HAVE_EVENT_WAIT;
    } else {
        static const bool HAS_EVENT_WAIT = true;
    }

and reference ``HAVE_EVENT_WAIT`` directly, without a second guard. It is also
what turns a misspelled constant name in a model into a hard resolution error
instead of a silent fallback to the default branch.

WHY MODELS MUST NOT FOLD THE TWO TESTS INTO ONE EXPRESSION
----------------------------------------------------------

The shape in the LRM's own Example275 (§19.3) --
``compile has(V) && target_cfg_pkg::HAVE_EVENT_WAIT`` -- does not work in
pssparser, which evaluates both operands of a compile-time binary expression
eagerly and fails the whole condition when either is unresolvable. That is
defensible: §8.4.4 makes short-circuiting normative, but it governs EVALUATION,
not name resolution, and nothing normative exempts a short-circuited operand
from §19.1.2's "previously declared" rule. Example275 is non-normative.

Nesting, as above, avoids the question entirely -- the reference sits inside an
already-enabled branch. ``!compile has(V) || ...`` is the same bet mirrored and
should be avoided too.
"""
from __future__ import annotations

from typing import Dict, Iterable, List, Optional

#: The contract version this pssc emits.
TARGET_CFG_VERSION = 2

#: The constants a version-2 provider is obliged to declare, in emission order.
CONTRACT_V2 = ("HAVE_EVENT_WAIT", "HAVE_RUNTIME_SOLVER")

#: The current contract. Code and diagnostics reference this; the versioned
#: name above is what a migration note can point at.
CONTRACT = CONTRACT_V2

#: Constants removed by a contract version, and what replaced them. Naming one
#: is an ERROR with a migration hint rather than "unknown constant": the whole
#: reason for the v1->v2 bump is that a stale `HAVE_BLOCKING=false` must not be
#: mistaken for a considered answer to the narrower question v2 asks.
_RENAMED_IN_V2 = {
    "HAVE_BLOCKING": "HAVE_EVENT_WAIT",
}

#: One-line rationale emitted beside each constant, so a reader of a dumped
#: prelude can tell what the target is actually claiming.
_DOC = {
    "HAVE_EVENT_WAIT":
        "can a caller suspend until another party posts an event?",
    "HAVE_RUNTIME_SOLVER":
        "does the image carry a solver, or is the model pre-solved?",
}


def _renamed_hint(name: str) -> Optional[str]:
    """The migration message for a constant a later contract version renamed."""
    new = _RENAMED_IN_V2.get(name)
    if new is None:
        return None
    return (
        f"target_cfg constant {name!r} was removed in contract "
        f"v{TARGET_CFG_VERSION}; use {new!r}. The two are not synonyms: "
        f"{name} asked 'can the runtime suspend a thread', {new} asks the "
        "narrower 'can a caller wait for an event'. A polling wait needs "
        "neither, so a model that answered 'false' to the old question may "
        "well answer differently to the new one -- re-decide rather than "
        "translate.")

#: The name the injected source unit is reported under in diagnostics. It is
#: deliberately not a real path -- nothing on disk corresponds to it, and a
#: reader who sees it in an error message should be able to tell that at once.
PRELUDE_NAME = "target_cfg_pkg.pss"


class TargetCfgError(ValueError):
    """A target's published capability set is unusable."""


def source_name(target_name: str) -> str:
    """The synthetic source-unit name for ``target_name``'s prelude."""
    return f"<pssc:{target_name}>/{PRELUDE_NAME}"


def parse_overrides(items: Optional[Iterable[str]]) -> Dict[str, bool]:
    """Parse ``NAME=VALUE`` strings from ``--target-cfg`` into a flag mapping.

    Accepts ``true``/``false``, ``1``/``0``, ``yes``/``no`` case-insensitively.
    Unknown constant names are rejected here rather than being emitted into the
    package, where they would be a silent no-op for every model that reads the
    contract.
    """
    out: Dict[str, bool] = {}
    for item in (items or ()):
        if "=" not in item:
            raise TargetCfgError(
                f"--target-cfg expects NAME=VALUE, got {item!r}")
        name, _, raw = item.partition("=")
        name = name.strip()
        raw = raw.strip().lower()
        if name not in CONTRACT:
            hint = _renamed_hint(name)
            if hint is not None:
                raise TargetCfgError(hint)
            known = ", ".join(CONTRACT)
            raise TargetCfgError(
                f"unknown target_cfg constant {name!r}; "
                f"contract v{TARGET_CFG_VERSION} defines: {known}")
        if raw in ("true", "1", "yes"):
            out[name] = True
        elif raw in ("false", "0", "no"):
            out[name] = False
        else:
            raise TargetCfgError(
                f"target_cfg {name}: expected a boolean, got {raw!r}")
    return out


def render(target_name: str, cfg: Dict[str, bool]) -> str:
    """Render ``cfg`` as the text of ``target_cfg_pkg``.

    Raises :class:`TargetCfgError` if ``cfg`` omits any contract constant --
    see the completeness obligation in the module docstring. A partial package
    would be worse than none: a model that has seen the version marker is
    entitled to reference every contract flag without guarding it.
    """
    stale = [n for n in cfg if n in _RENAMED_IN_V2]
    if stale:
        raise TargetCfgError(
            f"target '{target_name}': " + _renamed_hint(stale[0]))
    missing = [n for n in CONTRACT if n not in cfg]
    if missing:
        raise TargetCfgError(
            f"target '{target_name}' publishes an incomplete target_cfg_pkg: "
            f"contract v{TARGET_CFG_VERSION} requires "
            f"{', '.join(CONTRACT)}; missing {', '.join(missing)}. "
            "A provider that declares TARGET_CFG_VERSION declares every "
            "constant in that version.")
    extra = [n for n in cfg if n not in CONTRACT]
    if extra:
        raise TargetCfgError(
            f"target '{target_name}' publishes unknown target_cfg constant(s): "
            f"{', '.join(sorted(extra))}")

    width = max(len(n) for n in CONTRACT + ("TARGET_CFG_VERSION",))
    lines: List[str] = [
        f"// Generated by pssc for target '{target_name}'. Do not edit.",
        "//",
        "// Injected ahead of the user sources so a model can read it with a",
        "// plain `compile if`. Describes the EXECUTION TARGET, not any device.",
        "package target_cfg_pkg {",
        f"    static const int  {'TARGET_CFG_VERSION'.ljust(width)} = {TARGET_CFG_VERSION};",
    ]
    for name in CONTRACT:
        val = "true" if cfg[name] else "false"
        lines.append(
            f"    static const bool {name.ljust(width)} = {val};"
            f"   // {_DOC[name]}")
    lines.append("}")
    return "\n".join(lines) + "\n"
