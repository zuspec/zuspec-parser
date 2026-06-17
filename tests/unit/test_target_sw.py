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
    assert "pss_top__a.c" in names, names
    body = (out / "pss_top__a.c").read_text()
    # the body statement `int v = 1 + 2;` lowered to a real coroutine task
    assert "_body_task" in body
    assert "1 + 2" in body


def test_chost_via_cli(tmp_path):
    from pssc.cli import main
    out = tmp_path / "cli"
    code = main(["compile", _src(tmp_path), "-t", "c-host", "-o", str(out), "-q"])
    assert code == 0 and (out / "pss_top__a.c").is_file()


PRINT_SRC = """
component pss_top {
    action A {
        bit[8] a;
        exec body {
            print("hello");
            message(LOW, "a=%d", a);
            if (a > 0) { print("positive"); }
        }
    }
}
"""


def test_chost_lowers_print_and_message(tmp_path):
    p = tmp_path / "m.pss"
    p.write_text(PRINT_SRC)
    out = tmp_path / "c"
    pssc.compile(str(p), target="c-host", output_dir=str(out))
    body = (out / "pss_top__a.c").read_text()
    assert 'fprintf(stdout, "hello\\n")' in body
    assert 'a=%d' in body and "locals->self->a" in body  # message with one value
    assert 'fprintf(stdout, "positive\\n")' in body       # builtin inside nested if
    assert "unsupported" not in body


def test_builtin_lowering_does_not_mutate_source(tmp_path):
    import zuspec.ir.core as ir
    p = tmp_path / "m.pss"
    p.write_text(PRINT_SRC)
    ctx = pssc.driver.translate(str(p))
    body = [f for f in ctx.ir_context.type_m["pss_top::A"].functions
            if f.name == "body"][0]
    before = type(body.body[0].expr.func).__name__
    to_sw_context(ctx.ir_context)  # must not touch the shared IR
    after = type(body.body[0].expr.func).__name__
    assert before == after == "ExprAttribute"  # still self.print(...), not rewritten


FLAT_PRINT_SRC = """
component pss_top {
    action A {
        bit[8] a;
        exec body {
            print("hello");
            message(LOW, "a=%d", a);
            print("done");
        }
    }
}
"""


COLLIDE_SRC = """
component comp1 { action A { exec body { print("c1"); } } }
component comp2 { action A { exec body { print("c2"); } } }
"""


def test_chost_action_name_collision_avoided(tmp_path):
    # two actions named `A` in different components must not collide on one C file
    p = tmp_path / "m.pss"
    p.write_text(COLLIDE_SRC)
    out = tmp_path / "c"
    names = {x.name for x in pssc.compile(str(p), target="c-host",
                                          output_dir=str(out)).outputs}
    assert "comp1__a.c" in names and "comp2__a.c" in names


ACTIVITY_SRC = """
component pss_top {
    action Leaf { exec body { print("leaf"); } }
    action Root {
        Leaf a;
        Leaf b;
        activity { a; b; }
    }
}
"""

NESTED_ACTIVITY_SRC = """
component pss_top {
    action Leaf { exec body { print("leaf"); } }
    action Mid  { Leaf x; activity { x; } }
    action Root { Mid m; Mid n; activity { m; n; } }
}
"""


def test_sequential_activity_inlined(tmp_path):
    # `activity { a; b; }` inlines both sub-action bodies into Root's coroutine
    p = tmp_path / "m.pss"
    p.write_text(ACTIVITY_SRC)
    out = tmp_path / "c"
    pssc.compile(str(p), target="c-host", output_dir=str(out))
    root_c = (out / "pss_top__root.c").read_text()
    # 2 traversals × 2 emitted variants (sync + coroutine) = 4 inlined prints
    assert root_c.count('fprintf(stdout, "leaf\\n")') == 4


def test_nested_activity_inlined(tmp_path):
    # Root -> Mid -> Leaf : nested activities inline transitively
    p = tmp_path / "m.pss"
    p.write_text(NESTED_ACTIVITY_SRC)
    out = tmp_path / "c"
    pssc.compile(str(p), target="c-host", output_dir=str(out))
    root_c = (out / "pss_top__root.c").read_text()
    # Root traverses m, n; each Mid traverses one Leaf -> 2 leaf prints × 2 variants
    assert root_c.count('fprintf(stdout, "leaf\\n")') == 4


def _sw_runtime_dir() -> Path:
    import zuspec.be.sw as sw
    return Path(sw.__file__).parent / "share" / "rt"


def _link_and_run(out_dir, sources) -> subprocess.CompletedProcess:
    inc, rt = _sw_include_dir(), _sw_runtime_dir()
    gen_c = [str(p) for p in sources if p.suffix == ".c"]
    rt_c = [str(p) for p in rt.glob("*.c")]
    exe = Path(out_dir) / "prog"
    r = subprocess.run(["gcc", "-g", "-O0", "-w", f"-I{inc}", f"-I{out_dir}",
                        "-o", str(exe), *gen_c, *rt_c],
                       capture_output=True, text=True)
    assert r.returncode == 0, f"link failed:\n{r.stderr}"
    return subprocess.run([str(exe)], capture_output=True, text=True, timeout=10)


@pytest.mark.c_toolchain
def test_chost_full_program_links_and_runs(tmp_path):
    if shutil.which("gcc") is None:
        pytest.skip("gcc not available")
    p = tmp_path / "m.pss"
    p.write_text(FLAT_PRINT_SRC)
    out = tmp_path / "c"
    res = pssc.compile(str(p), target="c-host", output_dir=str(out))
    # the complete generated program (incl. main.c) links and runs
    run = _link_and_run(out, res.outputs)
    assert run.returncode == 0, run.stderr


@pytest.mark.c_toolchain
def test_chost_comparison_model_links(tmp_path):
    if shutil.which("gcc") is None:
        pytest.skip("gcc not available")
    p = tmp_path / "m.pss"
    p.write_text(PRINT_SRC)  # contains `if (a > 0)`
    out = tmp_path / "c"
    res = pssc.compile(str(p), target="c-host", output_dir=str(out))
    run = _link_and_run(out, res.outputs)
    assert run.returncode == 0, run.stderr


@pytest.mark.c_toolchain
def test_chost_activity_model_links(tmp_path):
    if shutil.which("gcc") is None:
        pytest.skip("gcc not available")
    p = tmp_path / "m.pss"
    p.write_text(NESTED_ACTIVITY_SRC)
    out = tmp_path / "c"
    res = pssc.compile(str(p), target="c-host", output_dir=str(out))
    run = _link_and_run(out, res.outputs)
    assert run.returncode == 0, run.stderr


def test_chost_emits_root_harness(tmp_path):
    # the generated main.c instantiates the root action and drives its activity
    p = tmp_path / "m.pss"
    p.write_text(ACTIVITY_SRC)
    out = tmp_path / "c"
    pssc.compile(str(p), target="c-host", output_dir=str(out))
    main_c = (out / "main.c").read_text()
    assert "pss_top__Root_body(&root, &tb)" in main_c
    assert "zsp_timebase_run(&tb)" in main_c


@pytest.mark.c_toolchain
def test_chost_activity_runs_and_prints(tmp_path):
    if shutil.which("gcc") is None:
        pytest.skip("gcc not available")
    p = tmp_path / "m.pss"
    p.write_text(ACTIVITY_SRC)  # activity { a; b; }, each Leaf prints "leaf"
    out = tmp_path / "c"
    res = pssc.compile(str(p), target="c-host", output_dir=str(out))
    run = _link_and_run(out, res.outputs)
    assert run.returncode == 0, run.stderr
    # the activity ran the two traversals in order
    assert run.stdout.split() == ["leaf", "leaf"], run.stdout


def test_chost_root_action_option(tmp_path):
    # --root-action selects the harness target explicitly
    p = tmp_path / "m.pss"
    p.write_text(ACTIVITY_SRC)
    out = tmp_path / "c"
    pssc.compile(str(p), target="c-host", output_dir=str(out),
                 root_action="Root")
    assert "pss_top__Root_body(&root, &tb)" in (out / "main.c").read_text()
