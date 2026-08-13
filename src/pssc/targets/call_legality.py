"""What a call may lower to, per target and per context.

THE PROBLEM THIS SOLVES. Every programming-sequence backend used to render an
unrecognized call by emitting it verbatim, producing output that named a
function the target language does not have. It exits 0, the dv-flow task goes
green, and the failure surfaces much later as an unresolved symbol -- if
anything ever elaborates the generated class at all. See
`docs/lowering-call-legality.md` §1.

THE SHAPE. Three tiers, because the targets genuinely differ in capability and a
flat per-target list has no contract to hold them together:

  Tier 0   what PSS DECLARES. Not a support list: it is what separates
           "core-library function with no lowering here" from "no such
           function" -- two different bugs, and a flat whitelist reports them
           identically.
  Tier 1   COMMON: what EVERY backend must render. A target may extend this;
           it may never shrink it. `test_call_legality.py` enforces that.
  Tier 2   per-target extensions, declared by the target.

The four outcomes below exist so each failure gets an actionable message rather
than one generic "unsupported call".
"""
from __future__ import annotations

import dataclasses as dc
from enum import Enum
from typing import Dict, FrozenSet, Optional, Tuple


class Ctx(Enum):
    """Where a call appears. PSS declares this per function; see `Entry.lrm`."""
    SOLVE = "solve"     # the constructor, and solve functions lowered into it
    TARGET = "target"   # operation bodies -- anything that can consume time


BOTH = frozenset({Ctx.SOLVE, Ctx.TARGET})
SOLVE_ONLY = frozenset({Ctx.SOLVE})
TARGET_ONLY = frozenset({Ctx.TARGET})


class Disposition(Enum):
    """How a recognized call is rendered."""
    UTILITY = "utility"            # host-language analogue ($display, printf)
    ADDR = "addr"                  # folded to arithmetic on a 64-bit address
    FOLD = "fold"                  # evaluated at generation time
    MEM = "mem"                    # import-API memory primitive
    REG = "reg"                    # register-handle method
    CHANNEL = "channel"            # sync_pkg::channel_c method
    MODEL_OP = "model_op"          # an operation of the lowered model
    IMPORT = "import"              # a declared import function
    SUBCOMP_CTOR = "subcomp_ctor"  # a sub-component constructor, in an init
    STRUCTURAL = "structural"      # consumed by the lowering (set_handle)


class Outcome(Enum):
    SUPPORTED = "supported"
    UNSUPPORTED_HERE = "unsupported_here"   # Tier 0, no lowering for this target
    WRONG_CONTEXT = "wrong_context"         # renderable, but not here
    UNKNOWN = "unknown"                     # not declared at all


@dc.dataclass(frozen=True)
class Entry:
    name: str
    disposition: Disposition
    contexts: FrozenSet[Ctx]
    lrm: str = ""            # LRM section, quoted in diagnostics
    unsupported: str = ""    # non-empty => Tier 0 only; the reason


@dc.dataclass(frozen=True)
class Result:
    outcome: Outcome
    entry: Optional[Entry]
    message: str

    @property
    def ok(self) -> bool:
        return self.outcome is Outcome.SUPPORTED


def _e(name, disp, contexts, lrm="", unsupported=""):
    return Entry(name, disp, contexts, lrm, unsupported)


# --- Tier 1: COMMON --------------------------------------------------------
#
# Membership rule (docs §3.2): declared in Tier 0 (or structural to the
# lowering), renderable by every target with no runtime dependency that target
# may not have, and typed within the common subset of the type mapper.

_COMMON_LIST = [
    # std_pkg utilities. `print` is NOT here -- it is platform-specific (Tier 2).
    _e("message", Disposition.UTILITY, BOTH, "21.1.3"),
    _e("error",   Disposition.UTILITY, BOTH, "21.3"),
    _e("fatal",   Disposition.UTILITY, BOTH, "21.3"),

    # addr_reg_pkg handle arithmetic. A handle is opaque in PSS and an address
    # in generated code, so these collapse to `+` and the identity.
    _e("make_handle_from_handle", Disposition.ADDR, BOTH, "21.12"),
    _e("addr_value",              Disposition.ADDR, BOTH, "21.12"),

    # Register-group offsets: evaluated, never emitted. `pure function`, so
    # legal in both contexts -- and a constructor is where they are actually
    # used, to place a sub-component array.
    _e("get_offset_of_instance",       Disposition.FOLD, BOTH, "21.14.6"),
    _e("get_offset_of_instance_array", Disposition.FOLD, BOTH, "21.14.6"),

    # Memory primitives. TARGET-only HERE even though addr_reg_pkg declares them
    # as plain `function`: there is no bus while the model is being
    # constructed, so a solve-context access has nothing to issue against. This
    # is the lowering being stricter than the front end, deliberately.
    _e("read8",   Disposition.MEM, TARGET_ONLY, "21.12"),
    _e("read16",  Disposition.MEM, TARGET_ONLY, "21.12"),
    _e("read32",  Disposition.MEM, TARGET_ONLY, "21.12"),
    _e("read64",  Disposition.MEM, TARGET_ONLY, "21.12"),
    _e("write8",  Disposition.MEM, TARGET_ONLY, "21.12"),
    _e("write16", Disposition.MEM, TARGET_ONLY, "21.12"),
    _e("write32", Disposition.MEM, TARGET_ONLY, "21.12"),
    _e("write64", Disposition.MEM, TARGET_ONLY, "21.12"),

    # reg_sized_c / reg_c -- all declared `target function` (21.14.1).
    _e("read",             Disposition.REG, TARGET_ONLY, "21.14.1"),
    _e("write",            Disposition.REG, TARGET_ONLY, "21.14.1"),
    _e("read_val",         Disposition.REG, TARGET_ONLY, "21.14.1"),
    _e("write_val",        Disposition.REG, TARGET_ONLY, "21.14.1"),
    _e("write_val_masked", Disposition.REG, TARGET_ONLY, "21.14.1"),
    _e("write_field",      Disposition.REG, TARGET_ONLY, "21.14.1"),
    _e("write_fields",     Disposition.REG, TARGET_ONLY, "21.14.1"),
    _e("write_masked",     Disposition.REG, TARGET_ONLY, "21.14.1"),
    _e("read_field",       Disposition.REG, TARGET_ONLY, "21.14.1"),

    # Consumed by the lowering: `regs.set_handle(h)` IS the group's construction.
    _e("set_handle", Disposition.STRUCTURAL, SOLVE_ONLY, "21.14.6"),
]

COMMON: Dict[str, Entry] = {e.name: e for e in _COMMON_LIST}


# --- Tier 0: declared, but not lowerable anywhere ---------------------------
#
# Registered so the diagnostic can say WHICH fix applies -- extend the compiler,
# or change the model. A name absent from every tier is a typo or an undeclared
# foreign function, which is a different conversation.

_FLOAT_REASON = (
    "PSS floating-point functions take and return float64 (21.5.2, Annex C) and "
    "pssc has no float64 in its type mapper; no target lowers them")

_MATH = ("log", "log10", "exp", "sqrt", "pow", "round", "floor", "ceil",
         "sin", "cos", "tan", "asin", "acos", "atan")

_TIER0_LIST = [
    _e(n, Disposition.UTILITY, BOTH, "21.5.2", _FLOAT_REASON) for n in _MATH
] + [
    _e("to_float", Disposition.UTILITY, BOTH, "21.5.1", _FLOAT_REASON),

    _e("make_handle_from_claim", Disposition.ADDR, SOLVE_ONLY, "21.12",
       "it takes an addr_claim_base_s -- a solve-time allocation result. A "
       "generated programming API has no address space in it; the environment "
       "passes in a base handle instead"),

    _e("read_bytes",  Disposition.MEM, TARGET_ONLY, "21.12",
       "it takes list<bit[8]>, and the lowering has no list representation"),
    _e("write_bytes", Disposition.MEM, TARGET_ONLY, "21.12",
       "it takes list<bit[8]>, and the lowering has no list representation"),
    _e("read_struct",  Disposition.MEM, TARGET_ONLY, "21.12",
       "generic struct parameters are not lowered; serialize the fields, as "
       "wb_dma_c/functions/write_descriptor.pss does"),
    _e("write_struct", Disposition.MEM, TARGET_ONLY, "21.12",
       "generic struct parameters are not lowered; serialize the fields, as "
       "wb_dma_c/functions/write_descriptor.pss does"),

    _e("get_offset_of_path", Disposition.FOLD, BOTH, "21.14.6",
       "it takes list<node_s>; use get_offset_of_instance[_array]"),

    _e("get_mnemonic_of_instance",       Disposition.UTILITY, SOLVE_ONLY, "21.14.6.1",
       "symbolic register naming is a solve-time facility with no runtime form"),
    _e("get_mnemonic_of_instance_array", Disposition.UTILITY, SOLVE_ONLY, "21.14.6.1",
       "symbolic register naming is a solve-time facility with no runtime form"),
    _e("get_mnemonic_of_path",           Disposition.UTILITY, SOLVE_ONLY, "21.14.6.1",
       "symbolic register naming is a solve-time facility with no runtime form"),
    _e("set_mnemonic",                   Disposition.UTILITY, SOLVE_ONLY, "21.14.6.1",
       "symbolic register naming is a solve-time facility with no runtime form"),
    _e("use_symbolic_reg_names",         Disposition.UTILITY, SOLVE_ONLY, "21.14.6.2",
       "symbolic register naming is a solve-time facility with no runtime form"),

    _e("add_region",                Disposition.ADDR, SOLVE_ONLY, "21.10",
       "address spaces are built by the environment, not by the device model"),
    _e("add_nonallocatable_region", Disposition.ADDR, SOLVE_ONLY, "21.10",
       "address spaces are built by the environment, not by the device model"),
    _e("add_addr_space",            Disposition.ADDR, SOLVE_ONLY, "21.10",
       "address spaces are built by the environment, not by the device model"),
]

TIER0: Dict[str, Entry] = {e.name: e for e in _TIER0_LIST}


# --- Tier 2: per-target extensions ------------------------------------------
#
# A target may ADD to COMMON. It may never remove; the contract test asserts it.

_NO_C_STRING = ("it returns a PSS string, and the C lowering has no string "
                "representation or ownership model")
_NO_C_PRNG = ("it needs a PRNG in the core header, and seeding/determinism is a "
              "policy decision the SV target gets from the simulator for free")
_NO_C_CHANNEL = ("there is no C runtime for sync_pkg::channel_c; see "
                 "targets/c/lower_progseq.py::_reject_channels")

_SV_EXT = [
    # `print` is declared `solve function` (21.1.2) -- the solve platform's
    # console. What it MEANS on a given target is a property of that target, so
    # it is Tier 2, and this backend offers it in both contexts because that is
    # what existing models already do.
    _e("print", Disposition.UTILITY, BOTH, "21.1.2"),
    _e("format",        Disposition.UTILITY, SOLVE_ONLY, "21.1.2"),
    _e("format_string", Disposition.UTILITY, BOTH, "19"),
    _e("urandom",       Disposition.UTILITY, BOTH, "21.4"),
    _e("urandom_range", Disposition.UTILITY, BOTH, "21.4"),
    _e("get",     Disposition.CHANNEL, TARGET_ONLY, "21.9.1"),
    _e("put",     Disposition.CHANNEL, TARGET_ONLY, "21.9.1"),
    _e("try_get", Disposition.CHANNEL, TARGET_ONLY, "21.9.1"),
    _e("try_put", Disposition.CHANNEL, TARGET_ONLY, "21.9.1"),
]

#: What each target adds beyond COMMON, and what it explicitly cannot do.
EXTENSIONS: Dict[str, Dict[str, Entry]] = {
    "op-model-sv": {e.name: e for e in _SV_EXT},
    "c-progseq": {e.name: e for e in [
        _e("print", Disposition.UTILITY, BOTH, "21.1.2"),
        _e("format",        Disposition.UTILITY, SOLVE_ONLY, "21.1.2", _NO_C_STRING),
        _e("format_string", Disposition.UTILITY, BOTH, "19", _NO_C_STRING),
        _e("urandom",       Disposition.UTILITY, BOTH, "21.4", _NO_C_PRNG),
        _e("urandom_range", Disposition.UTILITY, BOTH, "21.4", _NO_C_PRNG),
        _e("get",     Disposition.CHANNEL, TARGET_ONLY, "21.9.1", _NO_C_CHANNEL),
        _e("put",     Disposition.CHANNEL, TARGET_ONLY, "21.9.1", _NO_C_CHANNEL),
        _e("try_get", Disposition.CHANNEL, TARGET_ONLY, "21.9.1", _NO_C_CHANNEL),
        _e("try_put", Disposition.CHANNEL, TARGET_ONLY, "21.9.1", _NO_C_CHANNEL),
    ]},
}
EXTENSIONS["cpp-progseq"] = dict(EXTENSIONS["c-progseq"])

#: Targets bound by the Tier 1 contract.
PROGSEQ_TARGETS = tuple(sorted(EXTENSIONS))


def entries_for(target: str) -> Dict[str, Entry]:
    """Every entry visible to ``target``: Tier 0, then COMMON, then its own.

    Later wins, so a target extension may make a Tier 0 name renderable, and
    COMMON can never be shadowed away by Tier 0.
    """
    merged: Dict[str, Entry] = dict(TIER0)
    merged.update(COMMON)
    merged.update(EXTENSIONS.get(target, {}))
    return merged


def renderable(target: str) -> FrozenSet[str]:
    """Names ``target`` can actually emit, in at least one context."""
    return frozenset(n for n, e in entries_for(target).items() if not e.unsupported)


def classify(name: str, *, context: Ctx, target: str,
             model_ops: FrozenSet[str] = frozenset(),
             imports: FrozenSet[str] = frozenset(),
             subcomps: FrozenSet[str] = frozenset()) -> Result:
    """Classify a call by NAME, in ``context``, for ``target``.

    ``model_ops`` / ``imports`` / ``subcomps`` are the model's own names, which
    are not in any tier: an operation of the component being lowered, a declared
    import function, and a sub-component whose constructor an init may call.

    Name-based, which is what the emitters already do. It cannot tell a user
    component's no-argument `get()` from a channel receive -- a pre-existing
    ambiguity recorded in `_assign_from_call`'s docstring. That produces the
    wrong MAPPING, not an unmapped call, and fixing it needs receiver types the
    emitter does not carry.
    """
    if name in model_ops:
        return Result(Outcome.SUPPORTED,
                      _e(name, Disposition.MODEL_OP, TARGET_ONLY), "")
    if name in imports:
        return Result(Outcome.SUPPORTED, _e(name, Disposition.IMPORT, BOTH), "")
    if name in subcomps:
        return Result(Outcome.SUPPORTED,
                      _e(name, Disposition.SUBCOMP_CTOR, SOLVE_ONLY), "")

    entry = entries_for(target).get(name)
    if entry is None:
        return Result(Outcome.UNKNOWN, None, (
            f"no function named '{name}' is declared by PSS or by this model. "
            f"If it is a foreign function, declare it as an `import` function "
            f"so it is routed through the import API"))

    if entry.unsupported:
        where = f" (PSS {entry.lrm})" if entry.lrm else ""
        return Result(Outcome.UNSUPPORTED_HERE, entry, (
            f"'{name}' is a PSS core-library function{where} that "
            f"'{target}' cannot lower: {entry.unsupported}"))

    if context not in entry.contexts:
        only = "/".join(sorted(c.value for c in entry.contexts))
        return Result(Outcome.WRONG_CONTEXT, entry, (
            f"'{name}' is legal only in a {only} context, and this call is in a "
            f"{context.value} context"))

    return Result(Outcome.SUPPORTED, entry, "")
