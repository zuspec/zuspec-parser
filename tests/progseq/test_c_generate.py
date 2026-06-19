"""Phase 4/5: structural assertions on emitted C (no compiler needed).

Robust regex/structure checks, plus the design's backbone invariant: the
operation bodies are byte-identical across the three link styles.
"""
import argparse
import os

import pytest

from pssc import driver

_DATA = os.path.join(os.path.dirname(__file__), "..", "..",
                     "examples", "export", "programming_seqs")
_SRCS = [os.path.join(_DATA, "dma_regs.pss"), os.path.join(_DATA, "dma_engine.pss")]


def _gen(out_dir, link_style="vtable", reg_style="bitfields", prefix="wb_dma"):
    ns = argparse.Namespace(progseq_root="dma_engine_c", c_prefix=prefix,
                            c_link_style=link_style, c_reg_style=reg_style,
                            c_header_only=False, progseq_core_copy=True,
                            output_dir=str(out_dir))
    driver.compile(_SRCS, target="c-progseq", opts=ns)
    return out_dir


@pytest.fixture(scope="module")
def vtable(tmp_path_factory):
    return _gen(tmp_path_factory.mktemp("c_vtable"))


def _h(d):
    return (d / "wb_dma.h").read_text()


def _c(d):
    return (d / "wb_dma.c").read_text()


def test_value_unions(vtable):
    h = _h(vtable)
    for t in ("dma_ch_csr_t", "dma_ch_sz_t", "dma_ch_swptr_t", "dma_csr_t"):
        assert f"}} {t};" in h, t
    # LSB-first (declaration order): CH_EN [0] precedes INT_CHK_DONE [22]
    assert h.index("CH_EN") < h.index("INT_CHK_DONE")
    assert "uint32_t PRIORITY     :  3;" in h
    assert "uint32_t TOT_SZ       : 12;" in h


def test_baked_accessors(vtable):
    h = _h(vtable)
    assert "wb_dma_regs_channels_CSR_addr" in h
    assert "0x20u + (pssc_addr_t)i0 * 0x20u" in h     # channel base + stride
    # READONLY -> read accessor present, write suppressed
    assert "wb_dma_regs_INT_SRC_A_read" in h
    assert "wb_dma_regs_INT_SRC_A_write" not in h
    assert "_reserved" not in h                       # reserved gap omitted


def test_export_api_native(vtable):
    h, c = _h(vtable), _c(vtable)
    # native int return, opaque handle first arg, no output-status
    assert "int wb_dma_mem_to_mem_copy(wb_dma_t *s, int channel," in h
    assert "do {" in c and "} while (" in c           # native do...while
    assert "output" not in c
    # vtable create takes the bus
    assert "wb_dma_create(const pssc_mem_if *bus, pssc_addr_t base)" in h


def _op_body(text, sig_substr):
    """Return the inner lines of the function whose signature contains
    ``sig_substr`` (between its opening { and the column-0 closing })."""
    lines = text.splitlines()
    start = next(i for i, ln in enumerate(lines) if sig_substr in ln and ln.rstrip().endswith("{"))
    body = []
    for ln in lines[start + 1:]:
        if ln == "}":
            break
        body.append(ln)
    return body


def test_body_identical_across_link_styles(tmp_path):
    bodies = {}
    for style in ("vtable", "direct", "mmio"):
        d = _gen(tmp_path / style, link_style=style)
        src = (d / "wb_dma.h").read_text() if style == "mmio" else (d / "wb_dma.c").read_text()
        bodies[style] = _op_body(src, "wb_dma_mem_to_mem_copy(")
    assert bodies["vtable"] == bodies["direct"] == bodies["mmio"], \
        "operation bodies must be byte-identical across link styles"


def test_reg_style_accessors(tmp_path):
    d = _gen(tmp_path / "acc", reg_style="accessors")
    h = _h(d)
    # layout-independent path: plain raw word + shift/mask helpers
    assert "dma_ch_csr_t_PRIORITY_get" in h
    assert "dma_ch_csr_t_PRIORITY_set" in h
