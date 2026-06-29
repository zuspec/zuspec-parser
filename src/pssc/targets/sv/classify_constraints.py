"""Constraint classification pass (Phase 3).

Classifies each action constraint as one of:
  SV_NATIVE      -- references only local rand fields; SV randomize() handles it
  FLOW_PROP      -- references flow-object input fields but only via coupling to
                    output fields (safe for SV_WITH_INJECT when input is pinned)
  DPI_REQUIRED   -- constrains a flow-object input field value directly
                    (e.g. in_buf.x == 5); the producer must be told what to
                    generate, so this triggers constraint back-propagation and
                    the joint-chain DPI solve

The solve-mode for a traversal is determined by its consumer bindings:
  no bindings              -> SV_NATIVE
  bindings, all FLOW_PROP  -> SV_WITH_INJECT (safe to pin and solve locally)
  any DPI_REQUIRED binding -> DPI_JOINT_CHAIN (full-chain DPI solve needed)
"""
from __future__ import annotations

import enum
from typing import Dict, List, Optional, Set, Tuple, TYPE_CHECKING

import zuspec.ir.core as ir
from zuspec.ir.core import expr as ir_expr
from zuspec.ir.core.fields import FieldKind

if TYPE_CHECKING:
    from .context import LoweringContext


# ------------------------------------------------------------------ #
# Classification constants                                             #
# ------------------------------------------------------------------ #

class ConstraintClass(str, enum.Enum):
    SV_NATIVE    = "sv_native"    # pure local constraint -- SV handles it
    FLOW_PROP    = "flow_prop"    # couples input->output -- safe with injection
    DPI_REQUIRED = "dpi_required" # directly constrains input value

class SolveMode(str, enum.Enum):
    SV_NATIVE     = "sv_native"      # no flow-object inputs
    SV_WITH_INJECT = "sv_with_inject" # inject pinned values, randomize() locally
    DPI_JOINT_CHAIN = "dpi_joint_chain" # need joint chain solve
    DPI_STANDALONE = "dpi_standalone"  # isolated DPI problem (no chain needed)


# ------------------------------------------------------------------ #
# Expression field-reference walker                                    #
# ------------------------------------------------------------------ #

def _collect_top_field_refs(expr: ir.Expr) -> Set[str]:
    """Collect top-level (self.) field names referenced in an expression.

    Returns strings like 'in_buff', 'out_buff', 'val' -- the immediate
    attribute of self.  Sub-field accesses like 'in_buff.image.x' are
    represented by the top field 'in_buff'.
    """
    refs: Set[str] = set()
    _walk_expr(expr, refs)
    return refs


def _walk_expr(expr: ir.Expr, refs: Set[str]) -> None:
    if expr is None:
        return

    if isinstance(expr, ir_expr.ExprAttribute):
        base = expr.value
        if isinstance(base, ir_expr.TypeExprRefSelf):
            # self.field_name -- record direct attribute
            refs.add(expr.attr)
            return
        if isinstance(base, ir_expr.ExprAttribute):
            inner = base.value
            if isinstance(inner, ir_expr.TypeExprRefSelf):
                # self.field.sub_field -- record the top-level field
                refs.add(base.attr)
                return
        # Deeper nesting -- still collect from the base
        _walk_expr(base, refs)
        return

    # Walk child expressions
    for child_name in _child_expr_attrs(expr):
        child = getattr(expr, child_name, None)
        if child is None:
            continue
        if isinstance(child, list):
            for item in child:
                if isinstance(item, ir.Expr):
                    _walk_expr(item, refs)
        elif isinstance(child, ir.Expr):
            _walk_expr(child, refs)


def _child_expr_attrs(expr: ir.Expr) -> List[str]:
    """Return attribute names that might contain child expressions."""
    import dataclasses
    if not dataclasses.is_dataclass(expr):
        return []
    return [f.name for f in dataclasses.fields(expr)
            if f.name not in ('loc',)]


# ------------------------------------------------------------------ #
# Constraint classifier                                                #
# ------------------------------------------------------------------ #

def classify_constraint(
    ctx: 'LoweringContext',
    action_type_name: str,
    constraint_body: List[ir.Stmt],
    input_field_names: Set[str],
    output_field_names: Set[str],
) -> ConstraintClass:
    """Classify a single constraint function body.

    Args:
        ctx: Lowering context.
        action_type_name: Qualified PSS type name of the action.
        constraint_body: IR statement list from the constraint function.
        input_field_names: Set of input flow-object field names on this action.
        output_field_names: Set of output flow-object field names on this action.

    Returns:
        ConstraintClass.SV_NATIVE / .FLOW_PROP / .DPI_REQUIRED
    """
    if not constraint_body:
        return ConstraintClass.SV_NATIVE

    # Collect all top-level field references from all constraint statements
    all_refs: Set[str] = set()
    for stmt in constraint_body:
        if isinstance(stmt, ir.StmtExpr):
            _walk_expr(stmt.expr, all_refs)

    input_refs = all_refs & input_field_names
    output_refs = all_refs & output_field_names
    local_refs = all_refs - input_field_names - output_field_names

    if not input_refs:
        # No flow-object inputs referenced -- purely local
        return ConstraintClass.SV_NATIVE

    if input_refs and not output_refs and not local_refs:
        # Only references input fields, no output coupling.
        # This constrains what the input value must be -- back-propagation needed.
        return ConstraintClass.DPI_REQUIRED

    if input_refs and output_refs:
        # Couples input to output (e.g. in_istate.x == out_istate.x)
        # When the input is pinned externally, this becomes a local constraint.
        # Check for direct-value constraints on the input: if the input field is
        # compared to a constant in a context that does NOT also reference outputs,
        # that specific sub-expression is DPI_REQUIRED.
        if _has_input_constant_constraint(constraint_body, input_field_names,
                                          output_field_names):
            return ConstraintClass.DPI_REQUIRED
        return ConstraintClass.FLOW_PROP

    # input_refs + local_refs but no output_refs
    # e.g. constraint references input field and some other local field
    # This is potentially a constraint that restricts what the input must be.
    return ConstraintClass.DPI_REQUIRED


def _has_input_constant_constraint(
    stmts: List[ir.Stmt],
    input_fields: Set[str],
    output_fields: Set[str],
) -> bool:
    """Return True if any constraint expression equates an input field to a constant.

    Pattern: in_field.x == <constant>  with no output fields in the expression.
    This means the input value is directly constrained, triggering back-propagation.
    """
    for stmt in stmts:
        if isinstance(stmt, ir.StmtExpr):
            expr = stmt.expr
            if _is_input_eq_constant(expr, input_fields, output_fields):
                return True
    return False


def _is_input_eq_constant(
    expr: ir.Expr,
    input_fields: Set[str],
    output_fields: Set[str],
) -> bool:
    """Check if expr is an equality where one side is an input field ref
    and the other side has no output field references (could be a constant
    or expression of only local/constant values).
    """
    from zuspec.ir.core.expr import BinOp as IrBinOp
    if not isinstance(expr, ir_expr.ExprBin):
        # For bool AND chains, recurse
        if isinstance(expr, ir_expr.ExprBool):
            return any(_is_input_eq_constant(v, input_fields, output_fields)
                       for v in expr.values)
        return False

    if expr.op not in (IrBinOp.Eq, IrBinOp.NotEq):
        return False

    lhs_refs: Set[str] = set()
    rhs_refs: Set[str] = set()
    _walk_expr(expr.lhs, lhs_refs)
    _walk_expr(expr.rhs, rhs_refs)

    lhs_input = bool(lhs_refs & input_fields)
    lhs_output = bool(lhs_refs & output_fields)
    rhs_input = bool(rhs_refs & input_fields)
    rhs_output = bool(rhs_refs & output_fields)

    # Input on one side, no output on the other side
    if lhs_input and not lhs_output and not rhs_output:
        return True
    if rhs_input and not rhs_output and not lhs_output:
        return True

    return False


# ------------------------------------------------------------------ #
# Action-level solver mode determination                               #
# ------------------------------------------------------------------ #

def classify_action_constraints(
    ctx: 'LoweringContext',
    action_type_name: str,
) -> Dict[str, ConstraintClass]:
    """Classify all constraints for a given action type.

    Returns:
        Dict mapping constraint function name -> ConstraintClass.
    """
    if ctx.ir_ctx is None:
        return {}

    dtype = None
    for qname, dt in ctx.ir_ctx.type_map.items():
        if qname == action_type_name or qname.endswith(f"::{action_type_name}"):
            dtype = dt
            break

    if dtype is None:
        return {}

    # Get flow field sets
    input_fields: Set[str] = set()
    output_fields: Set[str] = set()
    for field in getattr(dtype, 'fields', []):
        if field.kind == FieldKind.Input:
            input_fields.add(field.name)
        elif field.kind == FieldKind.Output:
            output_fields.add(field.name)

    result: Dict[str, ConstraintClass] = {}
    for func in getattr(dtype, 'functions', []):
        if not func.metadata.get('_is_constraint'):
            continue
        cls = classify_constraint(
            ctx, action_type_name, func.body or [],
            input_fields, output_fields,
        )
        result[func.name] = cls

    return result


def determine_solve_mode(
    ctx: 'LoweringContext',
    action_type_name: str,
    has_consumer_bindings: bool,
) -> SolveMode:
    """Determine the solve mode for one action traversal.

    Args:
        ctx: Lowering context.
        action_type_name: Qualified PSS action type.
        has_consumer_bindings: True if this action consumes any flow-object inputs.

    Returns:
        The SolveMode for this traversal.
    """
    if not has_consumer_bindings:
        return SolveMode.SV_NATIVE

    classifications = classify_action_constraints(ctx, action_type_name)

    if not classifications:
        # No constraints at all -- safe with injection
        return SolveMode.SV_WITH_INJECT

    if any(c == ConstraintClass.DPI_REQUIRED for c in classifications.values()):
        return SolveMode.DPI_JOINT_CHAIN

    return SolveMode.SV_WITH_INJECT
