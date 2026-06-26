"""Subset-gating tests for the pure-SV path (`is_pure_supported`).

The pure path must correctly recognize what it can lower and fall back to
sv-native otherwise — never emit broken SV. These are fast (no simulator).
"""
import pytest

from pssc.driver import translate
from pssc.targets.sv.lower_pure import is_pure_supported


def _supported(tmp_path, pss_text, export):
    src = tmp_path / "m.pss"
    src.write_text(pss_text)
    ctx = translate([str(src)])
    assert not ctx.errors, ctx.errors
    return is_pure_supported(ctx, [export])


_ATOMIC = """
component pss_top { action A { rand bit[8] x; constraint c { x == 5; } } }
"""

_BUFFER_FWD = """
component pss_top {
    buffer Data { rand bit[8] x; }
    pool Data dp; bind dp *;
    action P { output Data o; }
    action C { input Data i; constraint c { i.x == 5; } }
    action T { P p; C c; activity { p; c; bind p.o c.i; } }
}
"""

_COUPLED_LOCAL_RAND = """
component pss_top {
    buffer Data { rand bit[8] x; }
    pool Data dp; bind dp *;
    action P { output Data o; }
    action C { input Data i; rand bit[8] k; constraint c { i.x == k; } }
    action T { P p; C c; activity { p; c; bind p.o c.i; } }
}
"""


def test_atomic_supported(tmp_path):
    assert _supported(tmp_path, _ATOMIC, "A") is True


def test_buffer_value_forwarding_supported(tmp_path):
    assert _supported(tmp_path, _BUFFER_FWD, "T") is True


def test_input_coupled_to_local_rand_falls_back(tmp_path):
    # `i.x == k` (k is the consumer's own rand) is the residual joint case:
    # not expressible via forwarding -> must fall back to sv-native.
    assert _supported(tmp_path, _COUPLED_LOCAL_RAND, "T") is False
