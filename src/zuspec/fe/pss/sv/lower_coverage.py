"""Lower PSS coverage constructs to SV covergroup declarations.

PSS actions can carry covergroups (``covergroup in action`` blocks).
These become SV ``covergroup`` declarations inside the action class,
with coverpoints derived from the action's rand fields.

The mapping:
  PSS covergroup -> SV ``covergroup cg_<action_name>``
      coverpoint field -> SV coverpoint

For simulation, each action class instantiates its covergroup
and samples it in the ``post_solve()`` callback.
"""
from __future__ import annotations

from typing import List, TYPE_CHECKING

from zuspec.dataclasses import ir

if TYPE_CHECKING:
    from .context import LoweringContext


def lower_action_covergroups(
    ctx: 'LoweringContext',
    action_qname: str,
    dtype: ir.DataTypeClass,
) -> List[str]:
    """Generate SV covergroup declaration lines for a PSS action.

    Returns SV source lines to append to the action class body.
    Returns an empty list if the action has no covergroups.

    Args:
        ctx: Lowering context.
        action_qname: Qualified action name (for covergroup naming).
        dtype: The action IR type.

    Returns:
        SV lines for the covergroup block (if any).
    """
    cgs = getattr(dtype, 'covergroups', [])
    if not cgs:
        return []

    sv_name = ctx.mangle_name(action_qname)
    cg_name = f"cg_{sv_name}"

    lines: List[str] = []
    lines.append(f"  covergroup {cg_name};")

    # Emit coverpoints for each rand field on the action as defaults;
    # override with explicit coverpoints when the IR carries them.
    explicit_cps: List[str] = []
    for cg in cgs:
        for cp in getattr(cg, 'coverpoints', []):
            cp_name = getattr(cp, 'name', None)
            target = getattr(cp, 'target', None) or cp_name or 'x'
            if cp_name:
                explicit_cps.append(f"    {cp_name}: coverpoint {target};")

    if explicit_cps:
        lines.extend(explicit_cps)
    else:
        # Fall back to one coverpoint per rand field
        for f in dtype.fields:
            if f.rand_kind in ("rand", "randc"):
                lines.append(f"    cp_{f.name}: coverpoint {f.name};")

    lines.append(f"  endgroup")
    lines.append(f"")
    lines.append(f"  {cg_name} cg_inst;")
    return lines


def lower_covergroup_sample_call(action_qname: str) -> List[str]:
    """Return SV lines to sample the covergroup in ``post_solve()``.

    Args:
        action_qname: Qualified action name.

    Returns:
        SV statement lines to add to the ``post_solve`` body.
    """
    return ["if (cg_inst != null) cg_inst.sample();"]
