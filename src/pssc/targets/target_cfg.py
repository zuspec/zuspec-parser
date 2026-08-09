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
        static const int  TARGET_CFG_VERSION  = 1;
        static const bool HAVE_BLOCKING       = true;
        static const bool HAVE_RUNTIME_SOLVER = true;
    }

``TARGET_CFG_VERSION`` is the marker a model tests for. ``compile has`` needs a
member path, so there is no way to ask "does this package exist"; the version
constant is what a model names instead, and making it a version rather than a
bare CONFIGURED flag lets the contract grow.

THE COMPLETENESS OBLIGATION
---------------------------

A provider that declares ``TARGET_CFG_VERSION = N`` declares EVERY constant in
contract version N. :func:`render` enforces this rather than filling in
defaults, and the enforcement is the point: it is what lets a model write

    compile if (compile has(target_cfg_pkg::TARGET_CFG_VERSION)) {
        static const bool HAS_BLOCKING = target_cfg_pkg::HAVE_BLOCKING;
    } else {
        static const bool HAS_BLOCKING = true;
    }

and reference ``HAVE_BLOCKING`` directly, without a second guard. It is also
what turns a misspelled constant name in a model into a hard resolution error
instead of a silent fallback to the default branch.

WHY MODELS MUST NOT FOLD THE TWO TESTS INTO ONE EXPRESSION
----------------------------------------------------------

The shape in the LRM's own Example275 (§19.3) --
``compile has(V) && target_cfg_pkg::HAVE_BLOCKING`` -- does not work in
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
TARGET_CFG_VERSION = 1

#: The constants a version-1 provider is obliged to declare, in emission order.
CONTRACT_V1 = ("HAVE_BLOCKING", "HAVE_RUNTIME_SOLVER")

#: One-line rationale emitted beside each constant, so a reader of a dumped
#: prelude can tell what the target is actually claiming.
_DOC = {
    "HAVE_BLOCKING":
        "can the target runtime suspend a thread?",
    "HAVE_RUNTIME_SOLVER":
        "does the image carry a solver, or is the model pre-solved?",
}

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
        if name not in CONTRACT_V1:
            known = ", ".join(CONTRACT_V1)
            raise TargetCfgError(
                f"unknown target_cfg constant {name!r}; contract v1 defines: {known}")
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
    missing = [n for n in CONTRACT_V1 if n not in cfg]
    if missing:
        raise TargetCfgError(
            f"target '{target_name}' publishes an incomplete target_cfg_pkg: "
            f"contract v{TARGET_CFG_VERSION} requires "
            f"{', '.join(CONTRACT_V1)}; missing {', '.join(missing)}. "
            "A provider that declares TARGET_CFG_VERSION declares every "
            "constant in that version.")
    extra = [n for n in cfg if n not in CONTRACT_V1]
    if extra:
        raise TargetCfgError(
            f"target '{target_name}' publishes unknown target_cfg constant(s): "
            f"{', '.join(sorted(extra))}")

    width = max(len(n) for n in CONTRACT_V1 + ("TARGET_CFG_VERSION",))
    lines: List[str] = [
        f"// Generated by pssc for target '{target_name}'. Do not edit.",
        "//",
        "// Injected ahead of the user sources so a model can read it with a",
        "// plain `compile if`. Describes the EXECUTION TARGET, not any device.",
        "package target_cfg_pkg {",
        f"    static const int  {'TARGET_CFG_VERSION'.ljust(width)} = {TARGET_CFG_VERSION};",
    ]
    for name in CONTRACT_V1:
        val = "true" if cfg[name] else "false"
        lines.append(
            f"    static const bool {name.ljust(width)} = {val};"
            f"   // {_DOC[name]}")
    lines.append("}")
    return "\n".join(lines) + "\n"
