"""Phase 6/7: cpp-progseq registration, arg parsing, generation structure."""
import argparse
import os

import pytest

from pssc import driver
from pssc import targets as _targets

_DATA = os.path.join(os.path.dirname(__file__), "..", "..",
                     "examples", "export", "programming_seqs")
_SRCS = [os.path.join(_DATA, "dma_regs.pss"), os.path.join(_DATA, "dma_engine.pss")]


def _gen(out_dir, dispatch="virtual", namespace="wb_dma"):
    ns = argparse.Namespace(progseq_root="dma_engine_c", cpp_namespace=namespace,
                            cpp_dispatch=dispatch, cpp_single_header=True,
                            progseq_core_copy=True, output_dir=str(out_dir))
    return driver.compile(_SRCS, target="cpp-progseq", opts=ns)


def test_registered():
    assert "cpp-progseq" in _targets.list_targets()
    assert _targets.get("progseq-cpp") is _targets.get("cpp-progseq")


def test_missing_root():
    with pytest.raises(ValueError, match="requires --root"):
        driver.compile(_SRCS, target="cpp-progseq",
                       opts=argparse.Namespace(progseq_root=None, output_dir="/tmp/x"))


def test_template_dispatch_not_yet(tmp_path):
    with pytest.raises(NotImplementedError, match="template"):
        _gen(tmp_path, dispatch="template")


@pytest.fixture(scope="module")
def gen(tmp_path_factory):
    out = tmp_path_factory.mktemp("cpp_gen")
    _gen(out)
    return out


def _hpp(d):
    return (d / "wb_dma.hpp").read_text()


def test_outputs(gen):
    assert (gen / "wb_dma.hpp").is_file()
    assert (gen / "pssc_reg.hpp").is_file()       # core copied alongside


def test_value_unions_and_groups(gen):
    h = _hpp(gen)
    assert "namespace wb_dma {" in h
    assert "typedef union { std::uint32_t raw; struct {" in h
    assert "class dma_channel_regs_c {" in h
    assert "pssc::reg<dma_ch_csr_t> CSR;" in h
    # READONLY mapped to access::ro
    assert "pssc::reg<std::uint32_t, pssc::access::ro> INT_SRC_A;" in h
    # array of groups via std::array + index helper
    assert "std::array<dma_channel_regs_c, 31> channels;" in h
    assert "std::make_index_sequence<31>" in h


def test_apis_and_component(gen):
    h = _hpp(gen)
    assert "struct wb_dma_if {" in h
    assert "virtual int mem_to_mem_copy(int channel," in h
    assert "struct wb_dma_import_if : pssc::mem_if {" in h
    # component holds mem_if& and reg model -- no redirect (no implements import_if)
    assert "class wb_dma : public wb_dma_if {" in h
    assert "pssc::mem_if &imp_;" in h
    assert "regs_(imp_, base)" in h
    assert "std::unique_ptr<wb_dma_if> create(pssc::mem_if &imp, pssc::addr_t base)" in h
    # native member-call body + native do...while
    assert "regs_.channels[channel].CSR.read();" in h
    assert "do {" in h and "} while (" in h
