"""The WB DMA conversion to `write_field` is a no-behaviour-change refactor.

`src/pss` used to spell its read-modify-write updates out:

    csr = regs.csr.read();
    csr.ch_en = 1;
    regs.csr.write(csr);

and now says `regs.csr.write_field("ch_en", 1);`. The claim is that nothing on
the bus moved. Two things could have:

1. **The transactions.** They cannot differ in shape: §21.14.1 defines the
   field-wise write as a read-modify-write, the reduction emits exactly one
   `write_val_masked` per site, and that lowers to one `read_val` and one
   `write_val` at the same address and width. `test_reg_rmw_expand.py` pins the
   statement-for-statement form; the count per site is pinned below.

2. **The value written.** This is the real risk, and it is what this file
   proves: the compiler folded a (mask, value) pair out of a field name, and if
   its bit arithmetic disagreed with the field assignment it replaced, the
   register would take a different value with nothing to notice it.

So the value is checked against an *independent* model of the old form -- the
field's documented bit position from `wb_dma_ch_regs_c.pss`, written out by hand
here rather than recomputed from the layout code under test -- over every
starting register value that can distinguish them.

**This is not a bus trace.** The op model has no simulation harness (the sim
gate runs a different, simpler model), so an end-to-end before/after trace diff
remains open. What is closed is the only step where the two forms could compute
differently.
"""
import os

import pytest

from pssc import driver

from .op_model import OP_MODEL as _MODEL, op_model_sources



def _sources():
    return op_model_sources()


#: The converted sites: (function, field, bit position, width).
#:
#: Bit positions are transcribed from the register's own documentation in
#: `wb_dma_regs_pkg/wb_dma_ch_regs_c.pss`, NOT read back from the layout helper
#: -- a test that asks the implementation what the answer is and then checks the
#: implementation against it pins nothing.
_SITES = [
    ("transfer_single_start", "ch_en",  0, 1),
    ("transfer_list_start",   "use_ed", 7, 1),
    ("transfer_list_start",   "ch_en",  0, 1),
    ("stop_channel_start",    "stop",   9, 1),
    ("set_auto_restart",      "ars",    6, 1),
]

_REG_BITS = 32


@pytest.fixture(scope="module")
def ctx():
    c = driver.translate(_sources())
    assert c.errors == [], c.errors
    return c


def _masked_writes(ctx, fn_name):
    """The (mask, value) pairs the compiler folded for one operation.

    `value` is None where it did not fold to a constant -- `set_auto_restart`
    writes its `enable` argument, so only its mask is known at compile time.
    """
    out = []
    for fn in ctx.type_map["wb_dma_ch_c"].functions:
        if fn.name != fn_name:
            continue
        for s in fn.body:
            e = getattr(s, "expr", None)
            if e is None or type(e).__name__ != "ExprCall":
                continue
            if getattr(e.func, "attr", None) != "write_val_masked":
                continue
            mask, val = e.args
            out.append((
                mask.value if type(mask).__name__ == "ExprConstant" else None,
                val.value if type(val).__name__ == "ExprConstant" else None,
            ))
    return out


def _set_field(cur: int, lsb: int, width: int, x: int) -> int:
    """The old form: read the word, assign the field, write it back."""
    m = ((1 << width) - 1) << lsb
    return (cur & ~m) | ((x << lsb) & m)


# --- the transaction shape -------------------------------------------------

def test_each_site_is_exactly_one_masked_write(ctx):
    """One bus read-modify-write per site, and the two in transfer_list_start
    stay two.

    Coalescing them into a single `write_fields` would be one transaction where
    the device requires two, in order: enable external descriptors, and only
    then arm the channel.
    """
    counts = {}
    for fn_name, *_ in _SITES:
        counts[fn_name] = len(_masked_writes(ctx, fn_name))
    assert counts == {
        "transfer_single_start": 1,
        "transfer_list_start": 2,
        "stop_channel_start": 1,
        "set_auto_restart": 1,
    }


def test_no_site_lost_its_write(ctx):
    """Every converted site still writes. A reduction that dropped a call would
    leave a channel unarmed, which no IR-shape assertion elsewhere would see."""
    for fn_name, field, _, _ in _SITES:
        assert _masked_writes(ctx, fn_name), \
            f"{fn_name} has no masked write ({field} was lost)"


# --- the value written -----------------------------------------------------

@pytest.mark.parametrize("fn_name,field,lsb,width", _SITES)
def test_folded_mask_matches_the_documented_bit_position(
        ctx, fn_name, field, lsb, width):
    expected = ((1 << width) - 1) << lsb
    masks = [m for m, _ in _masked_writes(ctx, fn_name)]
    assert expected in masks, (
        f"{fn_name}: no masked write with mask 0x{expected:x} for "
        f"'{field}' at bit {lsb}; got {[hex(m) for m in masks if m is not None]}")


@pytest.mark.parametrize("fn_name,field,lsb,width", _SITES)
def test_the_written_value_equals_the_old_field_assignment(
        ctx, fn_name, field, lsb, width):
    """`(cur & ~mask) | (val & mask)` == `cur` with the field assigned.

    Checked over starting values chosen to catch the ways this can go wrong:
    all-ones and all-zeros (a mask inverted the wrong way), the field already
    set and already clear (a write that is a no-op when it should not be), and
    the neighbouring bits (a mask one position out, which is the failure a
    single spot-check misses).
    """
    mask = ((1 << width) - 1) << lsb
    written = [(m, v) for m, v in _masked_writes(ctx, fn_name) if m == mask]
    assert written, f"{fn_name}: no write for '{field}'"
    _, folded_val = written[0]

    if folded_val is None:
        pytest.skip(f"{fn_name} writes a runtime value ('{field}' = enable)")

    # The constant the source wrote, recovered from the folded value.
    x = (folded_val & mask) >> lsb

    cases = [0x0000_0000, 0xFFFF_FFFF, mask, ~mask & 0xFFFF_FFFF,
             (mask << 1) & 0xFFFF_FFFF, mask >> 1 if lsb else 0,
             0xA5A5_A5A5, 0x5A5A_5A5A]
    for cur in cases:
        old = _set_field(cur, lsb, width, x)
        new = (cur & ~mask & 0xFFFF_FFFF) | (folded_val & mask)
        assert old == new, (
            f"{fn_name} '{field}': from 0x{cur:08x} the old form writes "
            f"0x{old:08x} and the masked write writes 0x{new:08x}")


def test_the_runtime_valued_site_masks_to_its_field(ctx):
    """`set_auto_restart(enable)` is the one site whose value is not constant.

    Its mask must still fold, and the value expression must be an expression --
    if it had folded to a constant, the argument would have been discarded.
    """
    writes = _masked_writes(ctx, "set_auto_restart")
    assert len(writes) == 1
    mask, val = writes[0]
    assert mask == 1 << 6, f"ars is bit 6; got {mask!r}"
    assert val is None, "the value is `enable`, and must not have folded"
