"""Compile-time constraint pre-solving via **dv-solve** (PSS output style 5).

Translates an action's ``rand`` integer fields and its constraint functions into a
dv-solve problem, solves it, and returns concrete values. Used to initialize the
fields hoisted into the generated C coroutine, so randomized fields get real
(constraint-satisfying) values baked in rather than zero.

Graceful by design: if dv-solve is unavailable, a constraint can't be translated,
or the problem is UNSAT, ``solve_action`` returns ``{}`` (or omits that field) and
the caller falls back to zero-initialization.
"""
from __future__ import annotations

import dataclasses as _dc
import zlib
from collections import namedtuple

import zuspec.ir.core as ir

#: One solver variable, identified by a ``path`` from the action ``self`` — a tuple
#: of field-name (str) / array-index (int) segments. Examples:
#:   scalar ``v``        -> ``("v",)``
#:   array  ``arr[i]``   -> ``("arr", i)``
#:   struct ``p.x``      -> ``("p", "x")``
#:   nested ``o.i.x``    -> ``("o", "i", "x")``
#:   array-of-struct     -> ``("pts", i, "x")``
#: ``cname`` (``"_".join`` of the path) is the C identifier suffix for the hoisted
#: local / solved global.
Slot = namedtuple("Slot", ["path", "cname", "var_id", "bits", "signed"])


def _cname(path):
    return "_".join(str(seg) for seg in path)

# pssc BinOp -> dv-solve BIN_* opcodes (see dv_solve.problem)
_BINOP = {
    ir.BinOp.Add: 0, ir.BinOp.Sub: 1, ir.BinOp.Mult: 2, ir.BinOp.Div: 3,
    ir.BinOp.Mod: 4, ir.BinOp.BitAnd: 5, ir.BinOp.BitOr: 6, ir.BinOp.BitXor: 7,
    ir.BinOp.LShift: 8, ir.BinOp.RShift: 9, ir.BinOp.Eq: 10, ir.BinOp.NotEq: 11,
    ir.BinOp.Lt: 12, ir.BinOp.LtE: 13, ir.BinOp.Gt: 14, ir.BinOp.GtE: 15,
    ir.BinOp.And: 16, ir.BinOp.Or: 17,
}


def _is_rand_int(fld) -> bool:
    return (getattr(fld, "rand_kind", None) == "rand"
            and isinstance(fld.datatype, ir.DataTypeInt))


def _bounds(dt) -> tuple:
    if dt.signed:
        return -(1 << (dt.bits - 1)), (1 << (dt.bits - 1)) - 1
    return 0, (1 << dt.bits) - 1


# integer-arithmetic BinOps that can be constant-folded (comparisons/logical excluded)
_FOLD = {
    ir.BinOp.Add: lambda a, c: a + c, ir.BinOp.Sub: lambda a, c: a - c,
    ir.BinOp.Mult: lambda a, c: a * c, ir.BinOp.Mod: lambda a, c: a % c if c else None,
    ir.BinOp.Div: lambda a, c: a // c if c else None,
    ir.BinOp.LShift: lambda a, c: a << c, ir.BinOp.RShift: lambda a, c: a >> c,
    ir.BinOp.BitAnd: lambda a, c: a & c, ir.BinOp.BitOr: lambda a, c: a | c,
    ir.BinOp.BitXor: lambda a, c: a ^ c,
}


def _const_value(expr, bindings):
    """Evaluate a constant integer expression (literals, ``foreach`` index vars,
    and arithmetic over them), or ``None`` if not constant."""
    if isinstance(expr, ir.ExprConstant) and isinstance(expr.value, int):
        return expr.value
    if isinstance(expr, ir.ExprRefLocal) and expr.name in bindings:
        return bindings[expr.name]
    if isinstance(expr, ir.ExprBin) and expr.op in _FOLD:
        a, c = _const_value(expr.lhs, bindings), _const_value(expr.rhs, bindings)
        return _FOLD[expr.op](a, c) if (a is not None and c is not None) else None
    return None


def _resolve_path(expr, bindings):
    """Resolve a self-rooted field reference of arbitrary depth to its ``path``
    tuple, or ``None`` if it is not such a reference. Array subscripts must be
    constant (literals or folded ``foreach`` indices). ``self`` alone -> ``()``."""
    if isinstance(expr, ir.TypeExprRefSelf):
        return ()
    if isinstance(expr, ir.ExprAttribute):
        base = _resolve_path(expr.value, bindings)
        return base + (expr.attr,) if base is not None else None
    if isinstance(expr, ir.ExprSubscript):
        base = _resolve_path(expr.value, bindings)
        idx = _const_value(expr.slice, bindings)
        return base + (idx,) if (base is not None and idx is not None) else None
    return None


def _translate(b, expr, var_id, bindings):
    """Translate a constraint expr to a dv-solve ExprRef, or ``None`` if it uses a
    construct we don't yet support (the constraint is then skipped). ``bindings``
    maps ``foreach`` loop vars to their (unrolled) constant index."""
    folded = _const_value(expr, bindings)   # fold `i*2`, `i+1`, literals, ...
    if folded is not None:
        return b.expr_const(folded, is_signed=folded < 0)
    if isinstance(expr, ir.ExprBin):
        op = _BINOP.get(expr.op)
        if op is None:
            return None
        lhs = _translate(b, expr.lhs, var_id, bindings)
        rhs = _translate(b, expr.rhs, var_id, bindings)
        if lhs is None or rhs is None:
            return None
        return b.expr_binary(op, lhs, rhs)
    if isinstance(expr, ir.ExprUnary):
        operand = _translate(b, expr.operand, var_id, bindings)
        if operand is None:
            return None
        # UN_NEG=0, UN_NOT=1, UN_INVERT=2
        un = {"USub": 0, "Not": 1, "Invert": 2}.get(getattr(expr.op, "name", ""), None)
        return b.expr_unary(un, operand) if un is not None else None
    if isinstance(expr, ir.ExprIn) and isinstance(expr.container, ir.ExprRangeList):
        # `x in [lo..hi, v, ...]` -> membership over a union of inclusive ranges
        # (a single value `v` is the degenerate range [v..v]).
        val = _translate(b, expr.value, var_id, bindings)
        if val is None:
            return None
        ranges = []
        for rng in expr.container.ranges:
            lo = _translate(b, rng.lower, var_id, bindings)
            hi = _translate(b, rng.upper, var_id, bindings) if rng.upper is not None else lo
            if lo is None or hi is None:
                return None
            ranges.append((lo, hi))
        return b.expr_in_ranges(val, ranges) if ranges else None
    if (isinstance(expr, ir.ExprCall)
            and isinstance(expr.func, ir.ExprRefUnresolved)
            and expr.func.name == "implies" and len(expr.args) == 2):
        # `a -> c`  ==  (NOT a) OR c     (UN_NOT=1, BIN_OR=17)
        ante = _translate(b, expr.args[0], var_id, bindings)
        cons = _translate(b, expr.args[1], var_id, bindings)
        if ante is None or cons is None:
            return None
        return b.expr_binary(_BINOP[ir.BinOp.Or], b.expr_unary(1, ante), cons)
    path = _resolve_path(expr, bindings)           # self.f / self.s.m / self.pts[i].x / ...
    if path:
        vid = var_id.get(path)
        return b.expr_var(vid) if vid is not None else None
    if isinstance(expr, ir.ExprRefLocal) and expr.name in bindings:
        return b.expr_const(bindings[expr.name])   # foreach index used as a value
    if isinstance(expr, ir.ExprConstant) and isinstance(expr.value, int):
        return b.expr_const(expr.value, is_signed=expr.value < 0)
    return None


_OR, _AND, _NOT = 17, 16, 1  # dv_solve BIN_OR / BIN_AND / UN_NOT


def _and(b, terms):
    """Conjoin a list of dv-solve ExprRefs, or ``None`` if empty."""
    terms = [t for t in terms if t is not None]
    if not terms:
        return None
    root = terms[0]
    for t in terms[1:]:
        root = b.expr_binary(_AND, root, t)
    return root


def _array_indices(var_id, field):
    """Sorted element indices of array ``field`` (from its flattened slot paths;
    works for array-of-int and array-of-struct)."""
    return sorted({p[1] for p in var_id
                   if len(p) >= 2 and p[0] == field and isinstance(p[1], int)})


def _translate_stmt(b, stmt, var_id, bindings):
    """Translate a constraint *statement* to a dv-solve ExprRef.

    Handles ``StmtExpr``; ``StmtIf`` (``if (T) {A} else {B}`` ==
    ``(T -> A) && (!T -> B)``); and ``StmtForeach`` over an array, which is
    **unrolled** — the body is re-translated once per element with the loop var
    bound to that constant index."""
    if isinstance(stmt, ir.StmtExpr):
        return _translate(b, stmt.expr, var_id, bindings)
    if isinstance(stmt, ir.StmtIf):
        test = _translate(b, stmt.test, var_id, bindings)
        if test is None:
            return None
        terms = []
        then_c = _and(b, [_translate_stmt(b, s, var_id, bindings) for s in stmt.body])
        if then_c is not None:
            terms.append(b.expr_binary(_OR, b.expr_unary(_NOT, test), then_c))  # T -> A
        else_c = _and(b, [_translate_stmt(b, s, var_id, bindings)
                          for s in (stmt.orelse or [])])
        if else_c is not None:
            terms.append(b.expr_binary(_OR, test, else_c))                      # !T -> B
        return _and(b, terms)
    if isinstance(stmt, ir.StmtForeach):
        if not (isinstance(stmt.iter, ir.ExprAttribute)
                and isinstance(stmt.iter.value, ir.TypeExprRefSelf)
                and isinstance(stmt.target, ir.ExprRefLocal)):
            return None
        idx_var = stmt.target.name
        terms = []
        for i in _array_indices(var_id, stmt.iter.attr):
            bnd = dict(bindings, **{idx_var: i})
            terms += [_translate_stmt(b, s, var_id, bnd) for s in stmt.body]
        return _and(b, terms)
    return None


def _is_plain_struct(dt) -> bool:
    """A PSS struct value type (not an action/component)."""
    return isinstance(dt, ir.DataTypeStruct) and not isinstance(dt, ir.DataTypeClass)


def _collect_field(path, fld, next_id):
    """Slots for a rand ``fld`` reached at ``path`` (``(slots, next_id)``).
    Only ``rand`` fields contribute; recurses through arrays and structs."""
    if getattr(fld, "rand_kind", None) != "rand":
        return [], next_id
    return _collect_type(path, fld.datatype, next_id)


def _collect_type(path, dt, next_id):
    """Slots for a value of type ``dt`` reached at ``path``: int -> one slot;
    array -> recurse each element; struct -> recurse each (rand) sub-field."""
    if isinstance(dt, ir.DataTypeInt):
        return [Slot(path, _cname(path), next_id, dt.bits, dt.signed)], next_id + 1
    if isinstance(dt, ir.DataTypeArray) and isinstance(dt.size, int):
        slots, nid = [], next_id
        for i in range(dt.size):
            ss, nid = _collect_type(path + (i,), dt.element_type, nid)
            slots += ss
        return slots, nid
    if _is_plain_struct(dt):
        slots, nid = [], next_id
        for sf in dt.fields:
            ss, nid = _collect_field(path + (sf.name,), sf, nid)
            slots += ss
        return slots, nid
    return [], next_id   # other element types not yet solved


def _collect_constraints(path, dt):
    """Constraint statements contributed by a struct/array value at ``path``, with
    ``self`` rebased to the value's path (so ``Point``'s ``x<y`` becomes
    ``pts[i].x < pts[i].y`` etc.). Recurses into sub-fields and array elements."""
    stmts = []
    if _is_plain_struct(dt):
        for fn in dt.functions:
            if fn.metadata.get("_is_constraint"):
                stmts += [_rebase_to_path(s, path) for s in fn.body]
        for sf in dt.fields:
            stmts += _collect_constraints(path + (sf.name,), sf.datatype)
    elif isinstance(dt, ir.DataTypeArray) and isinstance(dt.size, int):
        for i in range(dt.size):
            stmts += _collect_constraints(path + (i,), dt.element_type)
    return stmts


def _path_to_expr(path):
    """Build the self-rooted expr for a ``path`` (``("pts", 0, "x")`` ->
    ``self.pts[0].x``)."""
    e = ir.TypeExprRefSelf()
    for seg in path:
        if isinstance(seg, int):
            e = ir.ExprSubscript(value=e, slice=ir.ExprConstant(value=seg))
        else:
            e = ir.ExprAttribute(value=e, attr=seg)
    return e


def _rebase_to_path(expr, path):
    """Rewrite ``self`` -> ``self.<path>`` in a constraint expr (so a struct's own
    constraints, written against the struct instance, resolve against the action
    field/element that holds it)."""
    if isinstance(expr, ir.TypeExprRefSelf):
        return _path_to_expr(path)
    if not _dc.is_dataclass(expr):
        return expr
    changes = {}
    for f in _dc.fields(expr):
        v = getattr(expr, f.name)
        if isinstance(v, ir.Base):
            nv = _rebase_to_path(v, path)
            if nv is not v:
                changes[f.name] = nv
        elif isinstance(v, list) and v:
            nl = [_rebase_to_path(x, path) if isinstance(x, ir.Base) else x for x in v]
            if any(a is not b for a, b in zip(nl, v)):
                changes[f.name] = nl
    return _dc.replace(expr, **changes) if changes else expr


def build_problem(action):
    """Build the dv-solve problem for ``action``'s rand fields + constraints.

    Returns ``(builder, slots)`` (see :data:`Slot`), or ``(None, [])`` if dv-solve
    is unavailable or the action has no solvable rand fields.
    """
    try:
        from dv_solve.builder import SolveProblemBuilder
    except Exception:
        return None, []

    b = SolveProblemBuilder()
    slots, next_id = [], 0
    for fld in getattr(action, "fields", []):
        fslots, next_id = _collect_field((fld.name,), fld, next_id)
        for s in fslots:
            lo, hi = (-(1 << (s.bits - 1)), (1 << (s.bits - 1)) - 1) if s.signed \
                else (0, (1 << s.bits) - 1)
            b.add_var(s.var_id, s.bits, s.signed, lo, hi)
            slots.append(s)
    if not slots:
        return None, []

    var_id = {s.path: s.var_id for s in slots}

    def add_stmt(stmt):
        if isinstance(stmt, ir.StmtUnique):
            vids = [var_id[(v,)] for v in stmt.vars if (v,) in var_id]
            if len(vids) >= 2:
                b.add_all_different(vids)
            return
        root = _translate_stmt(b, stmt, var_id, {})
        if root is not None:
            b.add_constraint(root)

    # Action's own constraints.
    for fn in getattr(action, "functions", []):
        if fn.metadata.get("_is_constraint"):
            for stmt in fn.body:
                add_stmt(stmt)
    # Struct/array-of-struct field constraints, rebased to each instance's path.
    for fld in getattr(action, "fields", []):
        if getattr(fld, "rand_kind", None) == "rand":
            for stmt in _collect_constraints((fld.name,), fld.datatype):
                add_stmt(stmt)
    return b, slots


def problem_bytes(action):
    """Serialized dv-solve problem (relocatable; embeddable in generated C) plus
    its ``slots``, or ``(None, [])``."""
    b, slots = build_problem(action)
    if b is None:
        return None, []
    return b.finalize_bytes(), slots


def solve_action(action, seed: int = 0) -> dict:
    """Return ``{cname: value}`` solving ``action``'s rand fields against its
    constraints (scalar field -> its name; array element -> ``<field>_<i>``).
    Empty/partial on any failure (caller zero-fills the rest)."""
    try:
        from dv_solve.ctx import SolveCtx, SOLVE_OK
    except Exception:
        return {}
    b, slots = build_problem(action)
    if b is None:
        return {}
    prob, _ = b.finalize()
    try:
        ctx = SolveCtx(prob)   # may raise CompileIncompleteError / CompileUnsatError
    except Exception:
        return {}              # a constraint the native solver can't compile -> zero-fill
    try:
        if ctx.solve(seed=seed) != SOLVE_OK:
            return {}
        return {s.cname: ctx.get_value(s.var_id) for s in slots}
    finally:
        ctx.destroy()


def seed_for(prefix: str) -> int:
    """Stable per-traversal seed so sibling instances get distinct values."""
    return zlib.crc32(prefix.encode()) & 0x7FFF_FFFF
