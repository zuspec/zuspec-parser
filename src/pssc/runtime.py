"""Back-compat shim for the IR → live-Python builder.

The builder moved to the ``zuspec.be.py`` backend package
(:mod:`zuspec.be.py.builder`).  This module re-exports it so existing
``from pssc.runtime import IrToRuntimeBuilder, ClassRegistry`` imports keep
working unchanged.

PSS callers construct the builder with a :class:`pssc.ast2ir.AstToIrContext`.
This shim forwards that context's action→component ownership table
(``parent_comp_names``) to the backend as its ``owner_map``, so the result is
identical to the pre-migration in-tree builder.  (The backend reads the
context's ``type_map`` as the IR type set; a canonical
:class:`zuspec.ir.core.Context` with ``type_m`` works too.)
"""
from __future__ import annotations

from zuspec.be.py.builder import (
    IrToRuntimeBuilder as _IrToRuntimeBuilder,
    ClassRegistry,
    build_runtime,
)

__all__ = ["IrToRuntimeBuilder", "ClassRegistry", "build_runtime"]


class IrToRuntimeBuilder(_IrToRuntimeBuilder):
    """PSS-facing adapter over :class:`zuspec.be.py.builder.IrToRuntimeBuilder`.

    Forwards the PSS ``AstToIrContext.parent_comp_names`` as the explicit
    ``owner_map`` (authoritative for PSS); falls back to the backend's IR-based
    derivation when the context carries no such table.
    """

    def __init__(self, ctx, *, owner_map=None):
        if owner_map is None:
            owner_map = getattr(ctx, "parent_comp_names", None)
        super().__init__(ctx, owner_map=owner_map)
