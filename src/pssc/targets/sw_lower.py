"""IR lowering for the C (software) targets.

`zuspec-be-sw`'s ``CGenerator`` emits C only for ``DataTypeComponent`` (and
``DataTypeProtocol``). PSS **actions** are ``DataTypeClass`` (a ``DataTypeStruct``
subtype), so their coroutine ``body`` is skipped by the component walk.

``to_sw_context`` produces a *new* ``Context`` in which each PSS action is
re-expressed as a ``DataTypeComponent`` carrying the same fields/functions, so the
backend lowers its ``is_async`` body to a C coroutine. The original context (used
by the SV/Python paths) is left untouched.

Scope: this first slice handles the action -> component bridge. Activities,
flow-object scheduling, constraint solving, and PSS builtin mapping
(``message``/``print`` currently emit ``/* unsupported statement */``) are future
work tracked in the implementation plan (Phase 3).
"""
from __future__ import annotations

import zuspec.ir.core as ir


def _is_action(dt) -> bool:
    """A PSS action: a DataTypeClass that is not itself a component.

    Flow objects are ``DataTypeStruct`` (not ``DataTypeClass``) and components are
    ``DataTypeComponent``, so neither is matched.
    """
    return isinstance(dt, ir.DataTypeClass) and not isinstance(dt, ir.DataTypeComponent)


def _action_to_component(act: "ir.DataTypeClass") -> "ir.DataTypeComponent":
    return ir.DataTypeComponent(
        loc=act.loc,
        name=act.name,
        py_type=act.py_type,
        super=act.super,
        fields=list(act.fields),
        functions=list(act.functions),
        is_abstract=act.is_abstract,
        flow_kind=act.flow_kind,
        has_initial_constraint=act.has_initial_constraint,
        covergroups=list(act.covergroups),
        activity_ir=act.activity_ir,
    )


def to_sw_context(core: "ir.Context") -> "ir.Context":
    """Return a new ``Context`` with PSS actions lowered to components.

    Node objects for non-action types are shared (identity preserved); only
    actions are wrapped into fresh ``DataTypeComponent`` instances.
    """
    new_type_m = {}
    for name, dt in core.type_m.items():
        new_type_m[name] = _action_to_component(dt) if _is_action(dt) else dt
    return ir.Context(type_m=new_type_m)
