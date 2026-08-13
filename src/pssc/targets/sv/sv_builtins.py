"""PSS exec-block built-in calls -> SV system tasks (WS1 increment 2).

PSS exec bodies call a small set of library built-ins (``message``, ``print``,
``error``, ``fatal``, ``yield``). These are PSS *semantics*, so the mapping onto
SV system tasks lives here in the frontend rather than in be-sv's dumb
``core_to_sv`` translator.

The mapping is delivered as an :class:`SVExprEmitter` ``call_hook``: be-sv already
consults ``call_hook(ExprCall) -> Optional[str]`` before rendering any call, so a
``message(...)`` call anywhere in a procedural body (including nested statements)
is intercepted and rendered as ``$display(...)``. This replaces the string-based
``lower_stmts._lower_pss_call`` and keeps a single expression-rendering path.
"""
from __future__ import annotations

from typing import Callable, Optional

import zuspec.ir.core as ir
from zuspec.be.sv.ir.expr_emit import SVExprEmitter


# PSS exec built-in names (matched on the call target).
#
# `yield` is NOT here, and must not be added back: it is a procedural STATEMENT
# (`procedural_yield_stmt ::= yield ;`, Syntax 111), which parses to
# ProceduralStmtYield and reaches the IR as ir.StmtYield -- never as a call. The
# entry that used to sit here could not match anything, so its "// yield" text
# was unreachable in every target. The statement is lowered where it belongs,
# in lower_progseq's statement dispatch.
#
# The authority for what belongs here is `targets/call_legality.py`: this set is
# the SV target's RENDERINGS, and the registry is what says which names a target
# claims. A name claimed there with no rendering here would fall through to
# verbatim emission, which is the defect the registry exists to prevent.
PSS_BUILTINS = frozenset({
    "message", "print", "error", "fatal",
    "urandom", "urandom_range",          # std_pkg 21.4
    "format", "format_string",           # std_pkg 21.1.2 / 19
})


def builtin_name(func) -> Optional[str]:
    """Return the built-in name a call targets, or ``None``.

    Recognizes both ``ExprAttribute`` (``self.message(...)`` / ``pkg.message``)
    and ``ExprRefUnresolved`` (bare ``message(...)``) call targets.
    """
    if isinstance(func, ir.ExprAttribute):
        return func.attr
    if isinstance(func, ir.ExprRefUnresolved):
        return func.name
    return None


def make_pss_builtin_call_hook(
    emit: Callable[[object], str],
) -> Callable[[object], Optional[str]]:
    """Build an :class:`SVExprEmitter` ``call_hook`` mapping PSS built-ins.

    Args:
        emit: The owning emitter's ``.emit`` — used to render call arguments so
            they share the emitter's ``self_ref`` / ``field_resolver`` config.

    Returns a hook returning the SV call text, or ``None`` to fall through to the
    default call rendering.
    """
    def _args(args) -> str:
        return ", ".join(emit(a) for a in args)

    def hook(call) -> Optional[str]:
        name = builtin_name(call.func)
        if name not in PSS_BUILTINS:
            return None
        args = call.args
        if name == "message":
            # message(verbosity, fmt, args...) -> $display(fmt, args...)
            # The leading verbosity argument has no SV analog and is dropped.
            return f"$display({_args(args[1:])})" if len(args) >= 2 else "$display()"
        if name == "print":
            # print is printf-style with no newline -> $write (not $display).
            return f"$write({_args(args)})" if args else "$write()"
        if name == "error":
            return f"$error({_args(args)})"
        if name == "fatal":
            # fatal(exit_code, fmt, args...) -> $fatal(exit_code, fmt, args...)
            return f"$fatal({_args(args)})"
        if name == "urandom":
            return "$urandom()"
        if name == "urandom_range":
            # PSS is urandom_range(min, max); SV's $urandom_range takes
            # (maxval, minval) -- the operands are REVERSED, and getting that
            # wrong is silent for a symmetric range and wrong everywhere else.
            if len(args) == 2:
                return f"$urandom_range({emit(args[1])}, {emit(args[0])})"
            return f"$urandom_range({_args(args)})"
        if name in ("format", "format_string"):
            # Both return a formatted string; SV's is $sformatf.
            return f"$sformatf({_args(args)})"
        return None

    return hook


def make_sv_expr_emitter(**kwargs) -> SVExprEmitter:
    """Construct an :class:`SVExprEmitter` wired with the PSS built-in hook.

    Any ``call_hook`` in *kwargs* is ignored: this factory owns the call hook so
    every procedural body rendered through it maps PSS built-ins consistently.
    """
    kwargs.pop("call_hook", None)
    emitter = SVExprEmitter(**kwargs)
    emitter._call_hook = make_pss_builtin_call_hook(emitter.emit)
    return emitter
