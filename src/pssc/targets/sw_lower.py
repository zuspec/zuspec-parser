"""IR lowering for the C (software) targets.

`zuspec-be-sw`'s ``CGenerator`` emits C only for ``DataTypeComponent`` (and
``DataTypeProtocol``). PSS **actions** are ``DataTypeClass`` (a ``DataTypeStruct``
subtype), so their coroutine ``body`` is skipped by the component walk.

``to_sw_context`` produces a *new* ``Context`` in which each PSS action is
re-expressed as a ``DataTypeComponent`` carrying the same fields/functions, so the
backend lowers its ``is_async`` body to a C coroutine. The original context (used
by the SV/Python paths) is left untouched.

It also maps the PSS reporting builtins ``print`` / ``message`` onto the backend's
``print()`` → ``fprintf`` path (see ``_lower_builtin_call``).

Scope: this slice handles the action -> component bridge and print/message.
Activities, flow-object scheduling, and constraint solving are future work tracked
in the implementation plan (Phase 3).
"""
from __future__ import annotations

import dataclasses as _dc

import zuspec.ir.core as ir


# ---------------------------------------------------------------------------
# PSS builtin -> C mapping
#
# pssc emits PSS reporting builtins as method calls on self:
#   print(x)                -> ExprCall(ExprAttribute(self, 'print'),   [x])
#   message(VERB, fmt, ...) -> ExprCall(ExprAttribute(self, 'message'), [VERB, fmt, ...])
# zuspec-be-sw recognises print() only as a *bare* call (ExprRefUnresolved
# 'print') and renders it to fprintf; it supports a single %-format value
# (print(fmt % value)). We rewrite the PSS forms into that bare-print form.
# ---------------------------------------------------------------------------

def _lower_builtin_call(expr):
    """Map a ``self.print(...)`` / ``self.message(...)`` call to zuspec-be-sw's
    bare ``print()`` form. Return the rewritten ``ExprCall`` or ``None`` if this
    expression is not a mappable PSS builtin."""
    if not (isinstance(expr, ir.ExprCall)
            and isinstance(expr.func, ir.ExprAttribute)
            and isinstance(expr.func.value, ir.TypeExprRefSelf)):
        return None
    name = expr.func.attr
    if name == "print":
        return ir.ExprCall(func=ir.ExprRefUnresolved(name="print"), args=list(expr.args))
    if name == "message":
        # message(verbosity, fmt, *values): drop the verbosity level.
        rest = list(expr.args[1:])
        if not rest:
            return None
        fmt, values = rest[0], rest[1:]
        if not values:
            new_args = [fmt]
        elif len(values) == 1:
            # print(fmt % value) -> fprintf(stdout, fmt, value)
            new_args = [ir.ExprBin(lhs=fmt, op=ir.BinOp.Mod, rhs=values[0])]
        else:
            # zuspec-be-sw's print renders a single format value only; leave
            # multi-value message untouched (documented limitation).
            return None
        return ir.ExprCall(func=ir.ExprRefUnresolved(name="print"), args=new_args)
    return None


def _rewrite_stmt(stmt):
    """Return ``stmt`` with PSS builtin calls lowered, rebuilding only the nodes
    that change (originals are never mutated, so the shared SV/Python IR is safe)."""
    if isinstance(stmt, ir.StmtExpr):
        lowered = _lower_builtin_call(stmt.expr)
        return _dc.replace(stmt, expr=lowered) if lowered is not None else stmt

    changes = {}
    for f in _dc.fields(stmt):
        val = getattr(stmt, f.name)
        if isinstance(val, list) and val and all(isinstance(x, ir.Stmt) for x in val):
            new_list = [_rewrite_stmt(x) for x in val]
            if any(a is not b for a, b in zip(new_list, val)):
                changes[f.name] = new_list
        elif isinstance(val, ir.Stmt):
            new_val = _rewrite_stmt(val)
            if new_val is not val:
                changes[f.name] = new_val
    return _dc.replace(stmt, **changes) if changes else stmt


def _lower_builtins_in_function(func: "ir.Function") -> "ir.Function":
    new_body = [_rewrite_stmt(s) for s in func.body]
    if any(a is not b for a, b in zip(new_body, func.body)):
        return _dc.replace(func, body=new_body)
    return func


def _lower_builtins_in_type(dt):
    """Return ``dt`` with builtin calls lowered in its functions (new node only if
    something changed)."""
    funcs = getattr(dt, "functions", None)
    if not funcs:
        return dt
    new_funcs = [_lower_builtins_in_function(f) for f in funcs]
    if any(a is not b for a, b in zip(new_funcs, funcs)):
        return _dc.replace(dt, functions=new_funcs)
    return dt


def _is_action(dt) -> bool:
    """A PSS action: a DataTypeClass that is not itself a component.

    Flow objects are ``DataTypeStruct`` (not ``DataTypeClass``) and components are
    ``DataTypeComponent``, so neither is matched.
    """
    return isinstance(dt, ir.DataTypeClass) and not isinstance(dt, ir.DataTypeComponent)


# ---------------------------------------------------------------------------
# Activity lowering (sequential)
#
# zuspec-be-sw emits C only for action *bodies*; PSS activity scheduling
# (`activity { a; b; }`) is not lowered by the Context-first path, and the
# zdc-only action-inlining pass is unavailable here. We therefore inline a
# sequential activity into a synthesized ``body`` coroutine: each traversed
# sub-action's (builtin-lowered) body is spliced in order, with ``self``
# rebound to ``self.<handle>`` so the sub-action's own references resolve.
#
# Scope (first slice): flat/nested ``ActivitySequenceBlock`` of
# ``ActivityTraversal``s. Parallel/select/repeat and sub-action *field* access
# (which needs child-instance allocation) are future work.
# ---------------------------------------------------------------------------

def _rebind_self(node, handle):
    """Functional rewrite of ``self`` -> ``self.<handle>`` throughout ``node``."""
    if isinstance(node, ir.TypeExprRefSelf):
        return ir.ExprAttribute(value=ir.TypeExprRefSelf(), attr=handle)
    if not _dc.is_dataclass(node):
        return node
    changes = {}
    for f in _dc.fields(node):
        v = getattr(node, f.name)
        if isinstance(v, ir.Base):
            nv = _rebind_self(v, handle)
            if nv is not v:
                changes[f.name] = nv
        elif isinstance(v, list) and v:
            nl = [_rebind_self(x, handle) if isinstance(x, ir.Base) else x for x in v]
            if any(a is not b for a, b in zip(nl, v)):
                changes[f.name] = nl
    return _dc.replace(node, **changes) if changes else node


def _scope_of(qual_name: str) -> str:
    """Enclosing scope of a qualified name (``pss_top::Root`` -> ``pss_top``)."""
    return qual_name.rsplit("::", 1)[0] if "::" in qual_name else ""


def _resolve_sub_action(action, handle, type_m, scope):
    """Resolve a traversal ``handle`` to ``(qualified_key, sub_action)``.

    Field refs use the simple type name (``Leaf``), but ``type_m`` is keyed by the
    qualified name (``pss_top::Leaf``), so try the scope-qualified key, then a
    unique simple-name match.
    """
    for fld in getattr(action, "fields", []):
        if fld.name != handle:
            continue
        ref = getattr(fld.datatype, "ref_name", None)
        if ref is None:
            return None, None
        for cand in (ref, f"{scope}::{ref}" if scope else None):
            if cand and cand in type_m:
                return cand, type_m[cand]
        matches = [(k, v) for k, v in type_m.items() if k.split("::")[-1] == ref]
        return matches[0] if len(matches) == 1 else (None, None)
    return None, None


def _action_body_stmts(qual_name, action, type_m, seen):
    """(builtin-lowered) body statements for ``action`` — explicit exec ``body``
    or, failing that, its inlined sequential activity."""
    for fn in getattr(action, "functions", []):
        if fn.name == "body":
            return list(fn.body)
    act_ir = getattr(action, "activity_ir", None)
    if act_ir is not None:
        return _inline_sequential_activity(qual_name, action, act_ir, type_m, seen)
    return []


def _inline_sequential_activity(qual_name, action, act_ir, type_m, seen):
    """Inline a sequential activity into a flat list of body statements."""
    if not isinstance(act_ir, ir.ActivitySequenceBlock):
        return []  # only sequential supported in this slice
    scope = _scope_of(qual_name)
    out = []
    for stmt in act_ir.stmts:
        if not isinstance(stmt, ir.ActivityTraversal):
            continue  # parallel/select/etc. not yet supported
        sub_key, sub = _resolve_sub_action(action, stmt.handle, type_m, scope)
        if sub is None or sub_key in seen:
            continue
        for s in _action_body_stmts(sub_key, sub, type_m, seen | {sub_key}):
            out.append(_rebind_self(s, stmt.handle))
    return out


def _synthesize_activity_body(qual_name, action, type_m):
    """If ``action`` has an activity but no explicit body, synthesize a ``body``
    coroutine from the inlined activity."""
    if any(fn.name == "body" for fn in getattr(action, "functions", [])):
        return action
    act_ir = getattr(action, "activity_ir", None)
    if act_ir is None:
        return action
    stmts = _inline_sequential_activity(qual_name, action, act_ir, type_m,
                                        frozenset({qual_name}))
    if not stmts:
        return action
    body = ir.Function(name="body", is_async=True, body=stmts)
    return _dc.replace(action, functions=list(action.functions) + [body])


def _action_to_component(act: "ir.DataTypeClass", name: str) -> "ir.DataTypeComponent":
    return ir.DataTypeComponent(
        loc=act.loc,
        name=name,
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


def _iter_traversals(act_ir):
    """Yield ``ActivityTraversal`` nodes from a (possibly nested) activity."""
    if isinstance(act_ir, ir.ActivitySequenceBlock):
        for s in act_ir.stmts:
            yield from _iter_traversals(s)
    elif isinstance(act_ir, ir.ActivityTraversal):
        yield act_ir


def find_root_action(core: "ir.Context"):
    """Return the qualified name of the single top-level activity-bearing action
    (one with an ``activity_ir`` that no other activity traverses), or ``None``."""
    activity_actions = {
        name for name, dt in core.type_m.items()
        if _is_action(dt) and getattr(dt, "activity_ir", None) is not None
    }
    traversed = set()
    for name in activity_actions:
        dt = core.type_m[name]
        for trav in _iter_traversals(dt.activity_ir):
            key, _ = _resolve_sub_action(dt, trav.handle, core.type_m, _scope_of(name))
            if key:
                traversed.add(key)
    roots = activity_actions - traversed
    return next(iter(roots)) if len(roots) == 1 else None


def to_sw_context(core: "ir.Context") -> "ir.Context":
    """Return a new ``Context`` with PSS actions lowered to components.

    Node objects for non-action types are shared (identity preserved); only
    actions are wrapped into fresh ``DataTypeComponent`` instances.
    """
    # Phase 1: lower PSS builtins (print/message) in every type's functions, so
    # that activity inlining below splices already-lowered sub-action bodies.
    lowered = {name: _lower_builtins_in_type(dt) for name, dt in core.type_m.items()}

    # Phase 2: synthesize bodies for activity-only actions, then lower actions to
    # components (named by their qualified type_m key to avoid file collisions).
    new_type_m = {}
    for name, dt in lowered.items():
        if _is_action(dt):
            dt = _synthesize_activity_body(name, dt, lowered)
            dt = _action_to_component(dt, name)
        new_type_m[name] = dt
    return ir.Context(type_m=new_type_m)
