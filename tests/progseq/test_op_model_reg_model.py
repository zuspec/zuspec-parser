"""The operation model's register file, as lowered to SystemVerilog.

Exercises `lower_register_model` directly rather than the whole target, because
the rest of the package (sub-components, operation bodies) is still being built:
the register model is finished and can be locked down now.

Assertions include **absences**. Every defect this phase closed produced output
that looked plausible -- an empty group class, a register type emitted as an
operation interface -- so a test that only checked for presence would have
passed on all of them.
"""
import os
import re

import pytest

from pssc import driver
from pssc.targets.sv.lower_reg_model import lower_register_model

_MODEL = os.path.normpath(os.path.join(
    os.path.dirname(__file__), "..", "..", "examples", "op_model", "pss"))


def _sources():
    with open(os.path.join(_MODEL, "files.f")) as fp:
        rel = [ln.strip() for ln in fp if ln.strip() and not ln.startswith("#")]
    return [os.path.join(_MODEL, os.path.relpath(p, "src/pss")) for p in rel]


def assert_generated(text, *, has=(), has_not=()):
    """Assert on the presence AND absence of constructs in generated text."""
    for frag in has:
        assert frag in text, f"missing from generated output: {frag!r}"
    for frag in has_not:
        assert frag not in text, f"should not appear in generated output: {frag!r}"


@pytest.fixture(scope="module")
def ctx():
    c = driver.translate(_sources())
    assert not c.errors, c.errors
    return c


@pytest.fixture(scope="module")
def engine_regs(ctx):
    return lower_register_model(ctx.type_map["wb_dma_c"])


@pytest.fixture(scope="module")
def channel_regs(ctx):
    return lower_register_model(ctx.type_map["wb_dma_ch_c"])


# --- value structs ---------------------------------------------------------

def test_value_structs_emitted(engine_regs, channel_regs):
    sv, structs, _ = engine_regs
    assert_generated(sv, has=["typedef struct packed", "} wb_dma_gcsr_s;",
                              "} wb_dma_intvec_s;"])
    ch_sv, ch_structs, _ = channel_regs
    assert_generated(ch_sv, has=["} wb_dma_ch_csr_s;", "} wb_dma_ch_sz_s;",
                                 "} wb_dma_swptr_s;"])
    assert "wb_dma_ch_csr_s" in ch_structs


def test_value_struct_fields_are_msb_first(channel_regs):
    """SV packed structs are declared MSB-first, so the highest-numbered field
    leads. `int_chk_done` is bit 22, `ch_en` is bit 0."""
    sv, _, _ = channel_regs
    assert sv.index("int_chk_done") < sv.index("ch_en")


def test_field_widths_carried(channel_regs):
    sv, _, _ = channel_regs
    assert_generated(sv, has=["bit [2:0] prio;", "bit [11:0] tot_sz;"])


# --- register groups -------------------------------------------------------

def test_reg_group_has_members(engine_regs):
    """The signature of defect B: a register group whose registers are named
    types came out as a class with nothing in it but an empty constructor."""
    sv, _, groups = engine_regs
    assert "wb_dma_regs_c" in groups
    assert_generated(sv,
                     has=["class wb_dma_regs_c;", "csr;", "int_msk_a;"],
                     has_not=["class wb_dma_regs_c;\n\n    function new"])


def test_named_register_types_carry_access_mode(engine_regs):
    """`int_src_a` is declared `reg_c<wb_dma_intvec_s, READONLY, 32>` through a
    named type. READONLY must survive; READWRITE is the default and is omitted."""
    sv, _, _ = engine_regs
    assert_generated(sv,
                     has=["reg_c #(wb_dma_intvec_s, READONLY) int_src_a;",
                          "reg_c #(wb_dma_gcsr_s)"],
                     has_not=["reg_c #(wb_dma_gcsr_s, READWRITE)"])


def test_offsets_folded(engine_regs, channel_regs):
    sv, _, _ = engine_regs
    assert_generated(sv, has=["csr = new(bus, base + 64'h0);",
                              "int_src_b = new(bus, base + 64'h10);"])
    ch_sv, _, _ = channel_regs
    assert_generated(ch_sv, has=["swptr = new(bus, base + 64'h1c);"])


def test_channel_bank_lowered(channel_regs):
    """The per-channel bank is a top-level group reached through the channel
    component, not nested in the device group -- it must lower on its own."""
    ch_sv, _, groups = channel_regs
    assert "wb_dma_ch_regs_c" in groups
    for reg in ("csr", "sz", "adr0", "am0", "adr1", "am1", "desc", "swptr"):
        assert re.search(rf"\b{reg};", ch_sv), reg


def test_no_register_type_emitted_as_a_class(engine_regs, channel_regs):
    """The misclassification signature: named register types used to become
    components, so each got its own (empty) class or interface class."""
    for sv, _, _ in (engine_regs, channel_regs):
        assert_generated(sv, has_not=[
            "class wb_dma_gcsr_r", "class wb_dma_intsrc_r",
            "class wb_dma_ch_csr_r", "class wb_dma_word_r",
            "interface class wb_dma_gcsr_r_if",
        ])
