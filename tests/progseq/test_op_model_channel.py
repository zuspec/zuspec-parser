"""``sync_pkg::channel_c<Te, DEPTH>`` -- IR translation and SV projection.

A channel is the one core-library type whose implementation belongs to the
RUNTIME rather than to the generated model, and every defect in getting there
looked like ordinary generated code:

  * the specialization reached the IR as a plain ``DataTypeComponent``, so its
    element type and depth -- the whole content of ``channel_c<bit,1>`` -- were
    gone by the time a backend saw it;
  * the backend then lowered it as a user component, emitting
    ``interface class channel_c_if; endclass`` and a ``class channel_c`` with a
    constructor and no methods. That names every type the model mentions and
    fails only at the first ``get``.

So the absence assertions below are load-bearing, not decoration: `has_not` is
what distinguishes "the channel came from the runtime" from "the channel was
generated, empty".
"""
import argparse
import os
import shutil
import subprocess

import pytest

from pssc import driver
from zuspec.ir.core import DataTypeChannel


_MODEL = """
import sync_pkg::*;

component chan_c {
    channel_c<bit, 1>       wake;
    channel_c<bit[8], 4>    deep;

    target function bit take() {
        bit t;
        t = wake.get();
        return t;
    }
}

component chan_top_c {
    chan_c ch[2];

    target function void notify() {
        bool posted;
        foreach (ch[i]) {
            posted = ch[i].wake.try_put(1);
        }
    }
}
"""


@pytest.fixture(scope="module")
def gen(tmp_path_factory):
    out = tmp_path_factory.mktemp("chan_sv")
    src = out / "chan.pss"
    src.write_text(_MODEL)
    ns = argparse.Namespace(progseq_root="chan_top_c",
                            progseq_package="chan_pkg",
                            output_dir=str(out))
    res = driver.compile([str(src)], target="sv-progseq", opts=ns)
    return out, res, str(src)


@pytest.fixture(scope="module")
def sv(gen):
    out, _, _ = gen
    return (out / "chan_pkg.sv").read_text()


# --- IR --------------------------------------------------------------------

def test_channel_reaches_the_ir_with_its_template_arguments(gen):
    """Element type AND depth. A channel that arrives as a bare component has
    neither, and no backend can invent them."""
    _, _, src = gen
    ctx = driver.translate([src]).ir_context
    fields = {f.name: f.datatype for f in ctx.type_m["chan_c"].fields}

    assert isinstance(fields["wake"], DataTypeChannel)
    assert fields["wake"].depth == 1
    assert fields["wake"].element_type.bits == 1

    assert isinstance(fields["deep"], DataTypeChannel)
    assert fields["deep"].depth == 4
    assert fields["deep"].element_type.bits == 8


def test_depth_defaults_to_one(tmp_path):
    """§21.9.1's default, and it is behaviour rather than sizing: depth 1 is
    what makes a channel coalesce."""
    src = tmp_path / "d.pss"
    src.write_text("import sync_pkg::*;\n"
                   "component d_c { channel_c<bit> c;\n"
                   "  target function void f() { c.put(1); } }\n")
    ctx = driver.translate([str(src)]).ir_context
    dt = {f.name: f.datatype for f in ctx.type_m["d_c"].fields}["c"]
    assert dt.depth == 1


def test_zero_depth_is_rejected(tmp_path):
    """"DEPTH, if specified, shall be positive". Caught here because SV's
    `mailbox #(T) m = new(0)` is UNBOUNDED -- a zero that got through would
    produce a channel that never coalesces, with no error anywhere."""
    src = tmp_path / "z.pss"
    src.write_text("import sync_pkg::*;\n"
                   "component z_c { channel_c<bit, 0> c;\n"
                   "  target function void f() { c.put(1); } }\n")
    res = driver.translate([str(src)])
    assert any("DEPTH shall be positive" in e for e in res.errors), res.errors


# --- SV projection ---------------------------------------------------------

def test_channel_comes_from_the_runtime_not_the_model(sv):
    """The parameterized runtime class is referenced; no channel class or
    interface is generated for it."""
    assert "channel_c #(bit, 1) wake;" in sv
    assert "channel_c #(bit [7:0], 4) deep;" in sv
    assert "class channel_c" not in sv
    assert "channel_c_if" not in sv


def test_channels_are_constructed(sv):
    """An unconstructed handle is null, and SV reports that at the first
    `get`/`try_put` -- far from the constructor that should have built it."""
    assert "wake = new();" in sv
    assert "deep = new();" in sv


def test_channel_member_keeps_its_pss_name(sv):
    """No `m_` prefix, and not `protected`.

    A channel is the one field another component reaches THROUGH an instance
    handle (`ch[i].wake.try_put(1)`), and the trailing `.wake` there is emitted
    from the PSS name. Renaming the declaration to `m_wake` produced code that
    spelled one field two ways; `protected` made the cross-component access a
    compile error.
    """
    assert "    channel_c #(bit, 1) wake;" in sv
    assert "protected channel_c" not in sv
    assert "m_wake" not in sv
    assert ".wake.try_put(1);" in sv


def test_blocking_get_becomes_a_task_call(sv):
    """`t = c.get()` -> `c.get(t)`. `get` blocks, so it is a task, and a task
    has no return value -- `x = some_task()` is a syntax error."""
    assert "wake.get(t);" in sv
    assert "= wake.get()" not in sv


def test_non_blocking_calls_keep_their_return_value(sv):
    """`try_put`/`try_get` are functions returning a bit and must NOT get the
    output-argument rewrite that `get` needs."""
    assert "posted = m_ch[i].wake.try_put(1);" in sv


# --- the runtime it depends on ---------------------------------------------

def test_runtime_package_provides_the_channel(gen):
    out, _, _ = gen
    core = (out / "pssc_reg_pkg.sv").read_text()
    assert "class channel_c #(type Te = bit, int DEPTH = 1);" in core
    for fn in ("task get(", "task put(", "function bit try_get(",
               "function bit try_put("):
        assert fn in core, fn


# --- the backends that do NOT support channels -----------------------------

@pytest.mark.parametrize("target,label", [("c-progseq", "C"),
                                          ("cpp-progseq", "C++")])
def test_c_and_cpp_refuse_channels(tmp_path, target, label):
    """Neither has a channel runtime, and lowering one anyway emitted a struct
    with no channel member whose bodies still called `wake.get()` -- a complete
    looking API that exits 0 and does not compile. Refusing is the same policy
    as `_assert_api_is_not_empty`.

    Delete this test when a C/C++ channel runtime lands; until then it is the
    thing standing between a user and a silently broken header.
    """
    src = tmp_path / "chan.pss"
    src.write_text(_MODEL)
    ns = argparse.Namespace(progseq_root="chan_c", progseq_package="chan_pkg",
                            output_dir=str(tmp_path))
    with pytest.raises(ValueError, match="does not support channels"):
        driver.compile([str(src)], target=target, opts=ns)


@pytest.mark.skipif(not shutil.which("verilator"), reason="verilator not on PATH")
def test_generated_package_lints_clean(gen):
    out, _, _ = gen
    r = subprocess.run(
        ["verilator", "--lint-only", "-sv", "--timing",
         str(out / "pssc_reg_pkg.sv"), str(out / "chan_pkg.sv")],
        capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
