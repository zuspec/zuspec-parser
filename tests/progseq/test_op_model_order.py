"""What file order does, and no longer does, to the WB DMA operation model.

Measured on the whole real model rather than on a minimal repro, using the same
comparison `pssc.Check(order_check: true)` performs. The minimal repros live in
`tests/unit/test_file_order_independence.py`; this file is the scale check, and
scale is not optional here -- every one of the eighteen minimal probes in
`packages/dv-flow-libpss/docs/file-order-probes.md` 9.1 reported "independent"
while the real model was losing 40% of its references.

Two assertions, deliberately separate:

- **No declared type is lost** in either order. This passes. Before the
  three-pass elaboration in `ast2ir` it failed by 13 actions -- every action in
  this model arrives through an `extend` in a companion file.
- **The dumps are byte-identical.** Still a strict xfail, now for a much
  narrower reason than the original D3: a field type reaches the IR as the bound
  type or as a DataTypeRef depending on whether it was registered yet, so four
  nodes differ in spelling. Nothing is missing and every name resolves.

Note what is *not* asserted: an exit status. Both orders elaborate with zero
errors and would exit 0 -- that is precisely why D3 survived, and why the
assertions are on IR content instead.
"""
import os

import pytest

from pssc.driver import translate
from pssc.dvflow.check import _ir_signature, _normalized_dump

_MODEL = os.path.normpath(os.path.join(
    os.path.dirname(__file__), "..", "..", "examples", "op_model", "pss"))


def _sources():
    with open(os.path.join(_MODEL, "files.f")) as fp:
        rel = [ln.strip() for ln in fp if ln.strip() and not ln.startswith("#")]
    return [os.path.join(_MODEL, os.path.relpath(p, "src/pss")) for p in rel]


def _reordered():
    """The sources in the most adverse order the LANGUAGE permits.

    Reversed -- except that the build-profile package stays first, and that
    exception is the spec's, not a concession to the implementation. The model
    gates its blocking layer on `compile if wb_dma_cfg_pkg::WB_DMA_HAS_BLOCKING`,
    and PSS 3.1 §19.1.2 lets a compile-time expression reference only constants
    declared in this source unit or in a *previously-processed* one. A build
    profile that arrives after the code it configures is not a reordering the
    language allows; it is an error, and the front end says so.

    This exception did not exist when the test was written. It arrived with the
    two-profile split, and the checked-in copy of the model predated it -- so
    the test went on passing against a model that no longer looked like this
    one. That is the drift `scripts/sync_op_model.py` exists to catch.

    What is still asserted is what the test was always for: extends and actions
    arriving in companion files must not be lost when those files move.
    """
    src = _sources()
    cfg = [p for p in src if "wb_dma_cfg_pkg" in p]
    return cfg + list(reversed([p for p in src if p not in cfg]))


def _link(paths):
    ctx = translate(paths)
    assert ctx.errors == [], \
        "both orders must elaborate cleanly for this test to mean anything"
    return ctx.ir_context


def test_the_documented_order_elaborates_the_whole_model():
    """The baseline: in `files.f` order, everything resolves."""
    sig = _ir_signature(_link(_sources()))

    assert sig["_types"] > 100
    assert sig.get("_refs", 0) > 300


def test_no_declared_type_is_lost_in_either_file_order():
    """The part that is now guaranteed: the file *set* decides what the model
    contains, not the order it arrives in.

    Before the three-pass elaboration in `ast2ir` this failed hard -- reversing
    the order dropped all 13 actions, because every action in this model is
    declared by an `extend` in a companion file. It is asserted separately from
    the byte-identity test below because it is the assertion that matters: a
    missing type is a missing test, while the residual difference below is a
    difference in how a present type is spelled.
    """
    forward = _link(_sources())
    reverse = _link(_reordered())

    assert set(forward.type_m) == set(reverse.type_m)

    fwd_sig, rev_sig = _ir_signature(forward), _ir_signature(reverse)
    # Every count except the two that track bound-vs-reference spelling.
    presentation = {"DataTypeRef", "_refs"}
    assert {k: v for k, v in fwd_sig.items() if k not in presentation} == \
           {k: v for k, v in rev_sig.items() if k not in presentation}


@pytest.mark.xfail(
    strict=True,
    reason="A field type is bound to the type object when it is already "
           "registered and left as a DataTypeRef when it is not, so the file "
           "order still decides which of the two spellings reaches the IR "
           "(DataTypeRef 28 vs 32). Nothing is lost -- see the test above -- "
           "and both spellings resolve, but the dump is not byte-identical. "
           "Remove this marker when _translate_type_identifier stops "
           "consulting the registry mid-pass.")
def test_model_elaborates_identically_in_either_file_order():
    sources = _sources()

    forward = _link(sources)
    reverse = _link(list(reversed(sources)))

    assert _ir_signature(forward) == _ir_signature(reverse)
    assert _normalized_dump(forward) == _normalized_dump(reverse)
