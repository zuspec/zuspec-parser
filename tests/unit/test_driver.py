"""Phase-2: driver.compile — happy path per built-in target + error propagation."""
import pytest

import pssc
from pssc import driver

SRC = "component pss_top { action A { rand bit[8] x; constraint x > 3; } }"
BAD = "component pss_top { action A {"  # truncated -> parse/translate failure


def _write(tmp_path, text=SRC):
    p = tmp_path / "m.pss"
    p.write_text(text)
    return str(p)


def test_compile_python_happy_path(tmp_path):
    res = pssc.compile(_write(tmp_path), target="python")
    assert res.ok and res.target == "python"
    assert res.value is not None
    assert "pss_top::A" in res.value
    assert res.context is not None  # canonical IR carried on the result


def test_compile_python_emit_repr_writes_file(tmp_path):
    out = tmp_path / "out"
    res = pssc.compile(_write(tmp_path), target="python",
                       output_dir=str(out), emit="repr")
    assert res.outputs and res.outputs[0].name == "pss_classes.txt"
    assert res.outputs[0].read_text().strip()


def test_compile_sv_happy_path(tmp_path):
    out = tmp_path / "sv"
    res = pssc.compile(_write(tmp_path), target="sv", output_dir=str(out))
    assert res.ok
    names = sorted(p.name for p in res.outputs)
    assert "zsp_gen_pkg.sv" in names


def test_unknown_target_raises(tmp_path):
    with pytest.raises(driver.CompileError) as exc:
        pssc.compile(_write(tmp_path), target="nope")
    assert "nope" in str(exc.value)


def test_unknown_target_no_raise_mode(tmp_path):
    res = pssc.compile(_write(tmp_path), target="nope", raise_on_error=False)
    assert not res.ok and res.errors


def test_translation_error_propagates(tmp_path):
    with pytest.raises(Exception):
        pssc.compile(_write(tmp_path, BAD), target="python")
