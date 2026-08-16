"""Compilation driver: orchestrate sources -> AST -> IR -> selected target.

This is the single entry point shared by the CLI and the public
:func:`pssc.compile` API.
"""
from __future__ import annotations

import argparse
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, List, Optional, Sequence, Union

from .frontend import Parser
from .ast2ir import AstToIrTranslator, AstToIrContext
from .ir import to_core_context
from . import reg_rmw as _reg_rmw
from . import targets as _targets

PathLike = Union[str, os.PathLike]


@dataclass
class CompileResult:
    """Outcome of a :func:`compile` run."""

    target: str
    outputs: List[Path] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    #: The canonical ``zuspec.ir.core.Context`` produced by the front end.
    context: Any = None
    #: Target-specific in-memory artifact (e.g. the Python ``ClassRegistry``).
    value: Any = None

    @property
    def ok(self) -> bool:
        return not self.errors


class CompileError(Exception):
    """Raised by :func:`compile` for user-facing errors (bad target, parse/translate
    failures) when ``raise_on_error=True``."""

    def __init__(self, message: str, errors: Optional[Sequence[str]] = None) -> None:
        self.errors = list(errors or [])
        super().__init__(message)


def _normalize_opts(opts: Optional[argparse.Namespace],
                    output_dir: Optional[PathLike],
                    overrides: dict) -> argparse.Namespace:
    if opts is None:
        opts = argparse.Namespace()
    for k, v in overrides.items():
        setattr(opts, k, v)
    if output_dir is not None:
        opts.output_dir = str(output_dir)
    if getattr(opts, "output_dir", None) is None:
        opts.output_dir = "."
    return opts


def translate(sources: Union[PathLike, Sequence[PathLike]],
              reg_rmw: str = "native",
              prelude: Sequence[tuple] = (),
              comments: bool = True) -> AstToIrContext:
    """Parse + link + translate ``sources`` (file paths) to an ``AstToIrContext``.

    The returned context is enriched with ``ctx.ir_context`` — the canonical
    ``zuspec.ir.core.Context``.

    ``reg_rmw`` selects how far the §21.14.1 masked register writes are lowered.
    The reduction to ``write_val_masked`` happens unconditionally inside
    translation (it is what keeps field names out of the IR); ``"expand"``
    additionally rewrites that into ``read_val`` + ``write_val``.

    ``prelude`` is a sequence of ``(name, text)`` in-memory source units
    processed BEFORE ``sources`` — a target's ``target_cfg_pkg``, or anything
    else a backend needs in scope first. :func:`compile` fills this from the
    selected target; callers that translate without a target (``pssc.Check``)
    pass nothing and the model takes its own defaults.
    """
    if isinstance(sources, (str, os.PathLike)):
        sources = [sources]
    paths = [str(s) for s in sources]

    parser = Parser(collect_comments=comments)
    parser.parse(paths, prelude=prelude)
    root = parser.link()
    ctx = AstToIrTranslator().translate(root)
    if reg_rmw == "expand":
        _reg_rmw.expand_all(ctx)
    ctx.ir_context = to_core_context(ctx)
    return ctx


def compile(
    sources: Union[PathLike, Sequence[PathLike]],
    target: str = "python",
    output_dir: Optional[PathLike] = None,
    opts: Optional[argparse.Namespace] = None,
    raise_on_error: bool = True,
    **overrides: Any,
) -> CompileResult:
    """Compile PSS ``sources`` (file paths) with ``target``.

    Flow: ``Parser.parse`` -> ``link`` -> ``AstToIrTranslator.translate`` ->
    ``to_core_context`` -> ``targets.get(target).run(ctx, opts)``.

    ``opts`` may be a pre-built argparse ``Namespace`` (from the CLI); extra
    keyword ``overrides`` are applied on top (e.g. ``emit="repr"``). With
    ``raise_on_error`` (default), unknown targets and translation errors raise
    :class:`CompileError`; otherwise they are returned in ``CompileResult.errors``.
    """
    opts = _normalize_opts(opts, output_dir, overrides)

    # Resolve the target first so a bad name fails fast and clearly.
    _targets.discover()
    try:
        tgt = _targets.get(target)
    except KeyError as e:
        # `e.args[0]`, not `str(e)`: KeyError renders through repr(), which
        # wraps the whole sentence in quotes and escapes anything in it. The
        # message already names any plugin that failed to load, which is the
        # usual reason a target the user expects is not registered.
        msg = e.args[0] if e.args else str(e)
        if raise_on_error:
            raise CompileError(msg) from None
        return CompileResult(target=target, errors=[msg])

    # The target speaks first. Its prelude (typically `target_cfg_pkg`) must be
    # processed ahead of the user's sources -- see `translate`.
    try:
        prelude = tgt.prelude(opts)
    except ValueError as e:
        if raise_on_error:
            raise CompileError(str(e)) from None
        return CompileResult(target=target, errors=[str(e)])

    ctx = translate(sources, reg_rmw=getattr(opts, "reg_rmw", "native"),
                    comments=not getattr(opts, "no_comments", False),
                    prelude=prelude)

    if ctx.errors:
        if raise_on_error:
            raise CompileError(
                f"PSS translation failed with {len(ctx.errors)} error(s)",
                ctx.errors,
            )
        return CompileResult(
            target=target, errors=list(ctx.errors), context=ctx.ir_context
        )

    outputs = tgt.run(ctx, opts)
    return CompileResult(
        target=target,
        outputs=list(outputs),
        context=ctx.ir_context,
        value=getattr(tgt, "_last_value", None),
    )
