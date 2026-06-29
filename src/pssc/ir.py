"""IR hand-off helpers.

Canonicalize the PSS-specific :class:`pssc.ast2ir.AstToIrContext` into the
standard :class:`zuspec.ir.core.Context` that every Zuspec backend understands,
and serialize it to YAML for debugging / decoupled backend runs.
"""
from __future__ import annotations

import enum
from typing import TYPE_CHECKING

import zuspec.ir.core as ir

if TYPE_CHECKING:  # pragma: no cover
    from .ast2ir import AstToIrContext


class IRLayer(enum.Enum):
    """IR layer tag stamped into serialized artifacts.

    ``zuspec-synth`` owns the canonical ``IRLayer``; when it is not installed we
    fall back to this local definition so pssc can still serialize IR.
    """

    PSS = "PSS"


_DEFAULT_LAYER_CACHE = None


def _default_layer():
    """Return the default IR layer, preferring ``zuspec-synth``'s canonical enum.

    Computed lazily and cached: importing ``zuspec.synth`` is deferred until the
    layer is actually needed (only ``dump_ir`` / explicit ``DEFAULT_LAYER``
    access), so ``import pssc`` does not eagerly pull in ``zuspec-synth`` (and,
    transitively, ``zuspec-dataclasses``).
    """
    global _DEFAULT_LAYER_CACHE
    if _DEFAULT_LAYER_CACHE is None:
        try:  # prefer the canonical enum when zuspec-synth is present
            from zuspec.synth.ir.layers import IRLayer as _SynthLayer  # type: ignore
            _DEFAULT_LAYER_CACHE = list(_SynthLayer)[0]
        except Exception:
            _DEFAULT_LAYER_CACHE = IRLayer.PSS
    return _DEFAULT_LAYER_CACHE


def __getattr__(name):
    """PEP 562: resolve ``pssc.ir.DEFAULT_LAYER`` lazily (avoids eager synth import)."""
    if name == "DEFAULT_LAYER":
        return _default_layer()
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def to_core_context(ast_ctx: "AstToIrContext") -> ir.Context:
    """Canonicalize an ``AstToIrContext`` into a ``zuspec.ir.core.Context``.

    The translator's ``type_map`` is copied into the standard ``type_m`` field.
    Node objects are **shared** (identity preserved), not deep-copied. PSS-only
    side tables (``parent_comp_names``, ``errors``) are not part of the core
    ``Context`` schema; they remain on the ``AstToIrContext`` and are surfaced
    via the driver's ``CompileResult``.
    """
    return ir.Context(type_m=dict(ast_ctx.type_map))


def dump_ir(obj, layer=None) -> str:
    """Serialize an IR object (``Context`` or node) to YAML via ``IRSerializer``."""
    return ir.IRSerializer().serialize(obj, layer if layer is not None else _default_layer())
