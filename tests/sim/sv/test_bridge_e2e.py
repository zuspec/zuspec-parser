"""Phase C1 end-to-end: drive libpssc_scenario.so from Verilator over DPI.

Generates the sv-dpi-bridge target (which builds the .so), then a testbench that
uses the generated pssc_bridge_pkg trampoline to spawn two actions and run each
to completion, and checks the C scenario output crosses the DPI boundary.

Uses verilator directly (it links the prebuilt .so via -LDFLAGS); the matrix is
Verilator-first per the project directive.
"""
import shutil
import subprocess
from pathlib import Path

import pytest

import pssc

pytestmark = pytest.mark.skipif(
    shutil.which("verilator") is None or shutil.which("gcc") is None,
    reason="verilator + gcc required")


_MODEL = """
component pss_top {
    action Hello { exec body { print("hello from C\\n"); } }
    action World { exec body { print("world from C\\n"); } }
}
"""

_TB = """\
module tb;
  import pssc_bridge_pkg::*;
  initial begin
    chandle b = zsp_bridge_create();
    pssc_run_action(b, ACTION_Hello, 64'd1);
    pssc_run_action(b, ACTION_World, 64'd1);
    zsp_bridge_destroy(b);
    $display("[TB] done");
    $finish;
  end
endmodule
"""


def test_bridge_drives_scenario_from_verilator(tmp_path):
    src = tmp_path / "m.pss"
    src.write_text(_MODEL)
    out = tmp_path / "out"
    res = pssc.compile(str(src), target="sv-dpi-bridge", output_dir=str(out),
                       export_actions=["Hello", "World"])
    assert res.outputs
    assert (out / "libpssc_scenario.so").exists()
    (out / "tb.sv").write_text(_TB)

    build = subprocess.run(
        ["verilator", "--binary", "--timing", "-Wno-fatal", "-Wno-WIDTH",
         "--top-module", "tb", "pssc_bridge_pkg.sv", "tb.sv",
         "-LDFLAGS", f"-L{out} -lpssc_scenario -Wl,-rpath,{out}",
         "-o", "sim_tb"],
        cwd=str(out), capture_output=True, text=True)
    assert build.returncode == 0, f"verilator build failed:\n{build.stderr}"

    run = subprocess.run([str(out / "obj_dir" / "sim_tb")],
                         capture_output=True, text=True)
    assert "hello from C" in run.stdout, run.stdout
    assert "world from C" in run.stdout, run.stdout
    assert "[TB] done" in run.stdout, run.stdout


_RAND_MODEL = """
component pss_top {
    action Entry {
        rand bit[8] x;
        constraint { x > 3; x < 8; }
        exec body { print("x=%d\\n", x); }
    }
}
"""

_TB_RAND = """\
module tb;
  import pssc_bridge_pkg::*;
  initial begin
    chandle b = zsp_bridge_create();
    pssc_run_action(b, ACTION_Entry, 64'd1);
    $display("[TB] done");
    $finish;
  end
endmodule
"""


def test_bridge_presolved_rand_runs_on_verilator(tmp_path):
    """A spawned action's presolved rand value crosses DPI and satisfies its
    constraint."""
    src = tmp_path / "m.pss"
    src.write_text(_RAND_MODEL)
    out = tmp_path / "out"
    pssc.compile(str(src), target="sv-dpi-bridge", output_dir=str(out),
                 export_actions=["Entry"])
    (out / "tb.sv").write_text(_TB_RAND)
    build = subprocess.run(
        ["verilator", "--binary", "--timing", "-Wno-fatal", "-Wno-WIDTH",
         "--top-module", "tb", "pssc_bridge_pkg.sv", "tb.sv",
         "-LDFLAGS", f"-L{out} -lpssc_scenario -Wl,-rpath,{out}", "-o", "sim_tb"],
        cwd=str(out), capture_output=True, text=True)
    assert build.returncode == 0, build.stderr
    run = subprocess.run([str(out / "obj_dir" / "sim_tb")],
                         capture_output=True, text=True)
    import re
    m = re.search(r"x=(\d+)", run.stdout)
    assert m, run.stdout
    assert 3 < int(m.group(1)) < 8, run.stdout


_TB_RAND_AUTOSEED = """\
module tb;
  import pssc_bridge_pkg::*;
  initial begin
    chandle b = zsp_bridge_create();
    pssc_run_action_rand(b, ACTION_Entry);   // seed from this thread's randstate
    $display("[TB] done");
    $finish;
  end
endmodule
"""


def test_bridge_runtime_solve_seeded_from_sv_thread(tmp_path):
    """--runtime-solve: the C side solves the action's constraints per-spawn,
    seeded from the SV thread's random state, on Verilator."""
    src = tmp_path / "m.pss"
    src.write_text(_RAND_MODEL)
    out = tmp_path / "out"
    pssc.compile(str(src), target="sv-dpi-bridge", output_dir=str(out),
                 export_actions=["Entry"], runtime_solve=True)
    assert (out / "libpssc_scenario.so").exists()
    (out / "tb.sv").write_text(_TB_RAND_AUTOSEED)
    build = subprocess.run(
        ["verilator", "--binary", "--timing", "-Wno-fatal", "-Wno-WIDTH",
         "--top-module", "tb", "pssc_bridge_pkg.sv", "tb.sv",
         "-LDFLAGS", f"-L{out} -lpssc_scenario -Wl,-rpath,{out}", "-o", "sim_tb"],
        cwd=str(out), capture_output=True, text=True)
    assert build.returncode == 0, build.stderr
    run = subprocess.run([str(out / "obj_dir" / "sim_tb")],
                         capture_output=True, text=True)
    import re
    m = re.search(r"x=(\d+)", run.stdout)
    assert m, run.stdout
    assert 3 < int(m.group(1)) < 8, run.stdout
