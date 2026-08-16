"""`op-model-py`: the generated module is imported and DRIVEN, not grepped.

Every other backend's tests can only read the text they produce -- checking
generated C means compiling it, which is a slow marked test, and checking
generated SystemVerilog means a simulator. This one runs in-process, so the
questions a golden snapshot cannot answer ("is the address right", "does the
completion poll terminate", "does the read-modify-write preserve the bits it
should") are asked of the RUNNING model here.

That is also why this file matters beyond its own target: the addresses it
checks come from `targets/reg_layout.py`, which is the same walk the C backend
folds its accessors from. An offset wrong here is wrong in three languages.

Plan: P8.T1.
"""
from __future__ import annotations

import importlib
import subprocess
import sys
import textwrap

import pytest

from pssc.testing import compile_op_model, conformance

from .op_model import op_model_sources as wb_dma_sources

#: The WB DMA operation model exercises what the bundled one does not: a
#: component TREE, a sub-component array, channels, declared imports and
#: `yield`. Both are used here, and the split is deliberate -- the bundled
#: model is what a plugin author has, so anything checked only against the real
#: one is a claim they cannot reproduce.
WB_DMA_ROOT = "wb_dma_c"


def _load(outcome, module: str):
    """Import a freshly generated module out of its output directory."""
    sys.path.insert(0, str(outcome.out_dir))
    try:
        for name in (module, "pssc_rt"):
            sys.modules.pop(name, None)
        rt = importlib.import_module("pssc_rt")
        mod = importlib.import_module(module)
        return mod, rt
    finally:
        sys.path.remove(str(outcome.out_dir))


@pytest.fixture(scope="module")
def bundled():
    """The bundled model, generated, imported and ready to drive."""
    with compile_op_model("op-model-py") as outcome:
        mod, rt = _load(outcome, "dma_engine")
        yield mod, rt, outcome


@pytest.fixture(scope="module")
def wb_dma():
    """The real WB DMA operation model: a tree, channels, imports, `yield`."""
    with compile_op_model("op-model-py", sources=wb_dma_sources(),
                          root=WB_DMA_ROOT) as outcome:
        mod, rt = _load(outcome, "wb_dma")
        yield mod, rt, outcome


# --- what is produced -------------------------------------------------------

def test_it_produces_a_module_and_the_runtime(bundled):
    _, _, outcome = bundled
    assert outcome.names == ["dma_engine.py", "pssc_rt.py"]


def test_the_generated_module_imports_nothing_when_the_model_has_no_channels(
        bundled):
    """The zero-dependency property, asserted rather than hoped for.

    A generated driver gets copied onto a lab machine. A single file that
    imports nothing still runs there, and that is worth a test because it is
    the kind of property one convenience import silently ends.
    """
    _, _, outcome = bundled
    statements = [l for l in outcome.read("dma_engine.py").splitlines()
                  if l.startswith(("import ", "from "))]
    assert statements == [], statements


def test_a_model_with_channels_imports_the_channel_and_says_why(wb_dma):
    _, _, outcome = wb_dma
    text = outcome.read("wb_dma.py")
    assert "from pssc_rt import Chan1" in text
    assert "declares channels" in text


def test_no_core_copy_leaves_the_module_alone(tmp_path):
    with compile_op_model("op-model-py", output_dir=str(tmp_path),
                          progseq_core_copy=False) as outcome:
        assert outcome.names == ["dma_engine.py"]


def test_py_module_renames_the_module(tmp_path):
    with compile_op_model("op-model-py", output_dir=str(tmp_path),
                          py_module="acme_dma") as outcome:
        assert "acme_dma.py" in outcome.names
        assert "from acme_dma import DmaEngine" in outcome.read("acme_dma.py")


# --- addresses --------------------------------------------------------------

def test_folded_addresses_match_the_model(bundled):
    """The offsets in `dma_regs.pss`, recomputed by the accessor methods.

    Hard-coded on purpose. These come from the map the model's own header
    comment documents, so a change to the offset fold that agreed with itself
    would still fail here.
    """
    mod, rt, _ = bundled
    dut = mod.DmaEngine(rt.MemoryBus(), 0x4000)
    assert dut.regs_CSR_addr() == 0x4000
    assert dut.regs_INT_MSK_A_addr() == 0x4004
    assert dut.regs_INT_SRC_B_addr() == 0x4010
    # channels[] is at 0x20, stride 0x20; CSR is +0x00 and SWPTR is +0x1c.
    assert dut.regs_channels_CSR_addr(0) == 0x4020
    assert dut.regs_channels_CSR_addr(3) == 0x4080
    assert dut.regs_channels_SWPTR_addr(3) == 0x409c


def test_reserved_registers_are_not_surfaced(bundled):
    """`_reserved0..2` hold the 0x14..0x1f gap open and get no accessor."""
    mod, _, _ = bundled
    assert not [n for n in dir(mod.DmaEngine) if "_reserved" in n]


def test_a_sub_component_carries_its_own_base(wb_dma):
    """The same physical register, reached two ways, is the same address.

    `ch[2].regs.csr` and the root's `regs.bank[2].csr` are one register. The
    channel object was constructed at its own base, so its accessor folds a
    different constant and must arrive at the same place -- which is the
    property `conformance._group_bases` exists to allow for, checked here on a
    live object rather than by grepping for a number.
    """
    mod, rt, _ = wb_dma
    dut = mod.WbDma(rt.MemoryBus(), 0x2000)
    assert dut.regs_bank_csr_addr(2) == dut.ch_at(2).regs_csr_addr()
    assert dut.ch_at(2).regs_csr_addr() == 0x2000 + 0x20 + 2 * 0x20


# --- value classes ----------------------------------------------------------

def test_a_value_class_round_trips(bundled):
    mod, _, _ = bundled
    v = mod.dma_ch_csr_s(CH_EN=1, PRIORITY=5, DONE=1)
    raw = v.pack()
    assert raw == (1 << 0) | (5 << 13) | (1 << 11)
    back = mod.dma_ch_csr_s.unpack(raw)
    assert back == v and back.PRIORITY == 5


def test_a_field_is_masked_to_its_own_width(bundled):
    """An out-of-range assignment corrupts its own field and no other."""
    mod, _, _ = bundled
    v = mod.dma_ch_csr_s(PRIORITY=0xff, REST_EN=1)
    assert mod.dma_ch_csr_s.unpack(v.pack()).REST_EN == 1


def test_a_misspelled_field_is_refused(bundled):
    mod, _, _ = bundled
    with pytest.raises(TypeError) as exc:
        mod.dma_ch_csr_s(PRIORTY=1)
    assert "has no field" in str(exc.value)


# --- driving ----------------------------------------------------------------

def test_an_operation_issues_the_accesses_the_model_states(bundled):
    mod, rt, _ = bundled
    bus = rt.MemoryBus()
    dut = mod.DmaEngine(bus, 0x1000)
    dut.configure_channel(2, 3, 1, 0, 1)
    # One write, to channel 2's CSR, with exactly the fields the body sets and
    # CH_EN LEFT CLEAR -- which is the whole contract of configure_channel.
    assert [(k, hex(a)) for k, _, a, _ in bus.log] == [("write", "0x1060")]
    csr = mod.dma_ch_csr_s.unpack(bus.log[0][3])
    assert (csr.PRIORITY, csr.MODE, csr.SRC_SEL, csr.DST_SEL) == (3, 1, 0, 1)
    assert (csr.INC_SRC, csr.INC_DST, csr.CH_EN) == (1, 1, 0)


def test_the_arming_write_is_a_read_modify_write(bundled):
    """The bits a previous configure left in the CSR survive being armed.

    The model says so in its own comment ("never a blind write"), and this is
    the check that the lowering kept it: a blind write would clear PRIORITY.
    """
    mod, rt, _ = bundled
    bus = _completing_bus(rt, channel_base=0x1000 + 0x20 + 2 * 0x20)
    dut = mod.DmaEngine(bus, 0x1000)
    dut.configure_channel(2, 3, 1, 0, 1)
    bus.log.clear()
    assert dut.mem_to_mem_copy(2, 0xdead0000, 0xbeef0000, 64) == 0
    armed = [e for e in bus.log if e[0] == "write" and e[2] == 0x1060][-1]
    csr = mod.dma_ch_csr_s.unpack(armed[3])
    assert csr.CH_EN == 1 and csr.PRIORITY == 3


def test_sizes_are_programmed_in_words(bundled):
    """`nbytes / 4` is INTEGER division in PSS, and `/` in Python is not.

    64 bytes is 16 words. Rendered with Python's `/` this would be `16.0`, and
    `pack()` would raise or the bus would be handed a float -- so the failure
    is loud, but the point is that the operator is a translation and not a
    spelling.
    """
    mod, rt, _ = bundled
    bus = _completing_bus(rt, channel_base=0x1020)
    dut = mod.DmaEngine(bus, 0x1000)
    dut.mem_to_mem_copy(0, 0, 0, 64)
    sz = [e for e in bus.log if e[0] == "write" and e[2] == 0x1024][0]
    assert isinstance(sz[3], int)
    assert mod.dma_ch_sz_s.unpack(sz[3]).TOT_SZ == 16


def test_the_completion_poll_returns_the_devices_error(bundled):
    """ERR set on the first read returns 1 and stops polling."""
    mod, rt, _ = bundled
    bus = rt.MemoryBus()
    bus.mem[0x1020] = 1 << 12         # channel 0 CSR: ERR
    dut = mod.DmaEngine(bus, 0x1000)
    assert dut.mem_to_mem_copy(0, 0, 0, 4) == 1


def test_the_poll_reads_at_least_once(bundled):
    """`repeat {} while` is a do-while, and the rewrite has to preserve that.

    With DONE already set, a `while` would read zero times and a `do-while`
    reads once. The device that completed before the poll began is exactly the
    case the model wrote `repeat` for.
    """
    mod, rt, _ = bundled
    bus = _completing_bus(rt, channel_base=0x1020)
    dut = mod.DmaEngine(bus, 0x1000)
    bus.log.clear()
    dut.mem_to_mem_copy(0, 0, 0, 4)
    reads = [e for e in bus.log if e[0] == "read" and e[2] == 0x1020]
    assert len(reads) >= 2      # the read-modify-write's, then the poll's


def _completing_bus(rt, *, channel_base: int):
    """A bus whose channel reports DONE once the channel has been armed.

    `MemoryBus` alone cannot terminate a completion poll -- it is a memory, and
    a status bit nobody sets never sets. Its own docstring says so. This is the
    smallest thing that is a DEVICE.
    """
    class Device(rt.MemoryBus):
        def read32(self, addr):
            v = super().read32(addr)
            return (v | (1 << 11)) if (addr == channel_base and v & 1) else v

    return Device()


# --- the tree, channels, imports --------------------------------------------

def test_the_component_tree_is_constructed_with_folded_bases(wb_dma):
    mod, rt, _ = wb_dma
    dut = mod.WbDma(rt.MemoryBus(), 0x2000)
    assert dut.ch_size() == 4
    assert [dut.ch_at(i)._base for i in range(4)] == [
        0x2000 + 0x20 + 0x20 * i for i in range(4)]


def test_a_channel_output_local_is_a_cell(wb_dma):
    """`try_get(tok)` writes an output argument, which Python cannot do.

    The local is a one-element list and every read of it is `tok[0]`. Checked
    against the generated text as well as by driving, because the defect this
    replaced -- the token silently never assigned -- produced a module that
    imported, ran, and handed the wrong value back.
    """
    mod, rt, outcome = wb_dma
    text = outcome.read("wb_dma.py")
    assert "tok = [0]" in text
    assert "self.inflight.try_get(tok)" in text
    assert "self.inflight.try_put(tok[0])" in text


def test_a_completion_token_survives_a_probe_that_finds_it_running(wb_dma):
    """`check_completion` takes the token, finds the channel busy, returns it.

    The round trip is the whole reason `try_get`'s output argument matters: the
    value handed back by `try_put` is the one `try_get` wrote.
    """
    mod, rt, _ = wb_dma
    bus = rt.MemoryBus()
    dut = mod.WbDma(bus, 0x2000)
    ch = dut.ch_at(0)
    ch.inflight.try_put(0x5a)
    bus.mem[ch._base] = 1 << 10          # BUSY, not DONE: still running
    ch.check_completion()
    assert ch.inflight.full and ch.inflight.value == 0x5a


def test_a_blocking_channel_call_raises_rather_than_inventing_an_answer(wb_dma):
    _, rt, _ = wb_dma
    with pytest.raises(rt.ChannelEmpty):
        rt.Chan1().get()


def test_yield_lowers_to_a_comment_and_the_suite_still_parses(wb_dma):
    """A body of only `yield` is a C block with nothing in it and a Python
    syntax error. `block()` supplies the `pass`; the module imported, which is
    the check."""
    _, _, outcome = wb_dma
    text = outcome.read("wb_dma.py")
    assert "# yield: nothing to yield to on this target" in text
    assert "\n            pass\n" in text or "\n        pass\n" in text


def test_an_import_function_is_called_on_the_bus(wb_dma):
    """A declared `import` is a PLATFORM function, so it is not a method of the
    component and is not invented as one."""
    _, _, outcome = wb_dma
    text = outcome.read("wb_dma.py")
    assert "self._bus.message(" in text


# --- the contracts every target is held to ----------------------------------

def test_it_conforms():
    report = conformance.run("op-model-py")
    assert report.ok, str(report)


def test_it_refuses_exactly_what_the_c_target_refuses_on_the_real_model():
    """The two targets reach the same verdict on the same model, call for call.

    `conformance.run` is NOT used here, and the reason is worth recording. Its
    `_elaborate` translates without a target, so `wake.get()` -- which the model
    guards with `compile if (target_cfg_pkg::HAVE_EVENT_WAIT)` and which a real
    compile therefore elides -- survives into the IR and the gate refuses it.
    That happens identically for `op-model-c`, which is the point: it is a
    property of the harness and the model, not of this backend. Asserting the
    two AGREE is the check that survives the difference.
    """
    from pssc.targets.validate_calls import validate_calls

    model = conformance._elaborate(wb_dma_sources(), WB_DMA_ROOT)
    py = validate_calls(model.root, model.ctx, "op-model-py")
    c = validate_calls(model.root, model.ctx, "op-model-c")
    assert len(py) == len(c) == 1
    assert all("wait_hint" in m and "'get'" in m for m in py + c)


def test_it_renders_the_common_tier():
    from pssc.testing import assert_common_tier
    assert_common_tier("op-model-py")


def test_the_generated_module_compiles_under_the_bare_interpreter(wb_dma):
    """`py_compile` on a SUBPROCESS interpreter, not the one running the tests.

    Importing it here already proves it parses. This proves it parses with no
    pssc on the path and nothing else imported -- which is the situation the
    file is actually shipped into.
    """
    _, _, outcome = wb_dma
    res = subprocess.run(
        [sys.executable, "-c", textwrap.dedent(f"""
            import py_compile, sys
            py_compile.compile({str(outcome.out_dir / 'wb_dma.py')!r},
                               doraise=True, cfile=None)
        """)], capture_output=True, text=True)
    assert res.returncode == 0, res.stderr
