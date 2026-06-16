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


def _default_layer():
    try:  # prefer the canonical enum when zuspec-synth is present
        from zuspec.synth.ir.layers import IRLayer as _SynthLayer  # type: ignore
        return list(_SynthLayer)[0]
    except Exception:
        return IRLayer.PSS


DEFAULT_LAYER = _default_layer()


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
    return ir.IRSerializer().serialize(obj, layer if layer is not None else DEFAULT_LAYER)
