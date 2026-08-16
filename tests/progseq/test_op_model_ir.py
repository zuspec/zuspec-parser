"""The WB DMA operation model, as it reaches the IR.

`examples/op_model/` is the component-tree model (one component per channel,
named register types, operations in `extend component`, `yield` for blocking).
Everything asserted here is measured on the **IR**, before any backend, so a
codegen failure and a translation failure cannot be confused for each other.

Assertions are counts and names. Every defect this example exists to chase
produced a clean exit and a smaller model, so "it translated" proves nothing --
see the operation-model export plan §2.1.
"""
import os

import pytest

from pssc import driver

from .op_model import OP_MODEL as _MODEL, op_model_sources


#: Operations exposed by each component, from the model's own documentation.
#: `initialize` is the constructor and is deliberately listed apart from them.
_ENGINE_OPS = {"configure_interrupt_routing", "pause_engine",
               "read_descriptor_residual", "write_descriptor"}
_CHANNEL_OPS = {"configure_channel", "set_auto_restart", "set_software_pointer",
                "stop_channel", "transfer_list", "transfer_single",
                "wait_completion"}
_ACTIONS = {"wb_dma_c::configure_interrupt_routing_a",
            "wb_dma_ch_c::set_auto_restart_a",
            "wb_dma_ch_c::set_software_pointer_a",
            "wb_dma_ch_c::stop_channel_a",
            "wb_dma_ch_c::transfer_list_a",
            "wb_dma_ch_c::transfer_single_a"}


def _sources():
    """The model's files, in the dependency order `files.f` records.

    The order is load-bearing until pssparser D3 is fixed: presented wrongly,
    references silently fail to resolve and the run still exits 0.
    """
    return op_model_sources()


@pytest.fixture(scope="module")
def ctx():
    c = driver.translate(_sources())
    assert not c.errors, c.errors
    return c


def test_components_present(ctx):
    for name in ("wb_dma_c", "wb_dma_ch_c"):
        assert name in ctx.type_map, sorted(k for k in ctx.type_map if "wb_dma" in k)


def test_all_operations_present(ctx):
    """The count that defect A destroyed: 4 engine ops + 7 channel ops, all of
    them declared in `extend component` files."""
    engine = {f.name for f in ctx.type_map["wb_dma_c"].functions}
    channel = {f.name for f in ctx.type_map["wb_dma_ch_c"].functions}
    assert _ENGINE_OPS <= engine, f"missing: {sorted(_ENGINE_OPS - engine)}"
    assert _CHANNEL_OPS <= channel, f"missing: {sorted(_CHANNEL_OPS - channel)}"


def test_constructors_present(ctx):
    """`initialize` is the model's constructor.

    It was `\\init` -- an escaped identifier, since `init` is reserved -- and was
    renamed to drop the backslash. Both spellings are recognised as the
    constructor (progseq_model.DEFAULT_CTOR_NAMES); the rename is what proved that
    mattered, since a constructor classified as an ordinary export function
    generates a class that builds its register model from an undeclared
    variable."""
    for comp in ("wb_dma_c", "wb_dma_ch_c"):
        fn = next((f for f in ctx.type_map[comp].functions if f.name == "initialize"), None)
        assert fn is not None and fn.is_solve, comp


def test_all_actions_present_and_parented(ctx):
    for qname in _ACTIONS:
        assert qname in ctx.type_map, sorted(k for k in ctx.type_map if k.endswith("_a"))
        comp = qname.split("::")[0]
        assert ctx.parent_comp_names.get(qname) == comp, qname


def test_channel_array_declared(ctx):
    """The engine owns an array of channel components -- the sub-component
    exposure phase depends on this reaching the IR as an array."""
    ch = next((f for f in ctx.type_map["wb_dma_c"].fields if f.name == "ch"), None)
    assert ch is not None
    assert type(ch.datatype).__name__ == "DataTypeArray", type(ch.datatype).__name__


def test_no_field_name_reaches_the_ir_of_the_real_model(ctx):
    """The §1.1 invariant, on the model rather than on a synthetic snippet.

    `tests/unit/test_reg_ir_equivalence.py` proves the reduction is correct;
    this proves it actually runs over every body in a real multi-file component
    tree -- including exec bodies, which reach registers through `comp` and are
    resolved against a different type than the one that owns them.

    It is deliberately not conditional on the model currently using the masked
    forms. Today it passes vacuously; the moment the model adopts `write_field`
    (plan phase 6) it starts carrying weight, and it is here first so that
    adoption cannot quietly regress the invariant.
    """
    from tests.unit.test_reg_ir_equivalence import assert_no_field_names_in_ir
    assert_no_field_names_in_ir(ctx)
