"""Phase-3: the c-host C target (Context-first via zuspec-be-sw).

Generation runs everywhere; the actual gcc build is gated behind the
``c_toolchain`` marker (and skipped if no compiler is present).
"""
import shutil
import subprocess
from pathlib import Path

import pytest

import pssc
from pssc import targets
from pssc.targets.sw_lower import to_sw_context

SRC = """
component pss_top {
    action A {
        exec body {
            int v = 1 + 2;
        }
    }
}
"""


def _src(tmp_path):
    p = tmp_path / "m.pss"
    p.write_text(SRC)
    return str(p)


def _sw_include_dir() -> Path:
    import zuspec.be.sw as sw
    return Path(sw.__file__).parent / "share" / "include"


def test_chost_registered():
    assert "c-host" in targets.list_targets()


def test_to_sw_context_lowers_actions_to_components():
    import zuspec.ir.core as ir
    core = pssc.to_core_context(_translate_ctx())
    sw_ctx = to_sw_context(core)
    # the action pss_top::A is a bare DataTypeClass in the core context ...
    assert isinstance(core.type_m["pss_top::A"], ir.DataTypeClass)
    assert not isinstance(core.type_m["pss_top::A"], ir.DataTypeComponent)
    # ... and a DataTypeComponent in the lowered context
    assert isinstance(sw_ctx.type_m["pss_top::A"], ir.DataTypeComponent)
    # non-actions are shared unchanged (identity preserved)
    assert sw_ctx.type_m["pss_top"] is core.type_m["pss_top"]


def _translate_ctx():
    import tempfile, os
    d = tempfile.mkdtemp()
    p = os.path.join(d, "m.pss")
    with open(p, "w") as fh:
        fh.write(SRC)
    return pssc.driver.translate(p)


def test_chost_generates_action_coroutine(tmp_path):
    out = tmp_path / "c"
    res = pssc.compile(_src(tmp_path), target="c-host", output_dir=str(out))
    assert res.ok
    names = [p.name for p in res.outputs]
    # the lowered action gets its own C file (name is lowercased by the backend)
    assert "a.c" in names, names
    body = (out / "a.c").read_text()
    # the body statement `int v = 1 + 2;` lowered to a real coroutine task
    assert "_body_task" in body
    assert "1 + 2" in body


def test_chost_via_cli(tmp_path):
    from pssc.cli import main
    out = tmp_path / "cli"
    code = main(["compile", _src(tmp_path), "-t", "c-host", "-o", str(out), "-q"])
    assert code == 0 and (out / "a.c").is_file()


@pytest.mark.c_toolchain
def test_chost_generated_c_compiles(tmp_path):
    if shutil.which("gcc") is None:
        pytest.skip("gcc not available")
    out = tmp_path / "c"
    res = pssc.compile(_src(tmp_path), target="c-host", output_dir=str(out))
    inc = _sw_include_dir()
    # The model's component/action C is what we validate. The backend-emitted
    # top-level `main.c` harness has an upstream zuspec-be-sw bug (it #includes
    # unqualified header names, e.g. "executor_base_c.h", while the files are
    # written qualified as "executor_pkg__executor_base_c.h"), so it is excluded
    # here and tracked as an upstream issue.
    gen_c = [p for p in res.outputs if p.suffix == ".c" and p.name != "main.c"]
    assert gen_c, "no C sources generated"
    for c in gen_c:
        # compile-to-object: validates generated C is well-formed and resolves
        # against the runtime headers, without the per-model link fragility.
        r = subprocess.run(
            ["gcc", "-c", "-w", f"-I{inc}", f"-I{out}", str(c), "-o", str(c) + ".o"],
            capture_output=True, text=True,
        )
        assert r.returncode == 0, f"gcc failed on {c.name}:\n{r.stderr}"
