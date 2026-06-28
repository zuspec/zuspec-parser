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


def translate(sources: Union[PathLike, Sequence[PathLike]]) -> AstToIrContext:
    """Parse + link + translate ``sources`` (file paths) to an ``AstToIrContext``.

    The returned context is enriched with ``ctx.ir_context`` — the canonical
    ``zuspec.ir.core.Context``.
    """
    if isinstance(sources, (str, os.PathLike)):
        sources = [sources]
    paths = [str(s) for s in sources]

    parser = Parser()
    parser.parse(paths)
    root = parser.link()
    ctx = AstToIrTranslator().translate(root)
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
        if raise_on_error:
            raise CompileError(str(e)) from None
        return CompileResult(target=target, errors=[str(e)])

    ctx = translate(sources)

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
