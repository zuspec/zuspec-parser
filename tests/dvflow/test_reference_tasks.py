"""Reference tasks emit filesets over the bundled core source."""
import os

from .conftest import requires_dfm, run_task, filesets_by_type


@requires_dfm
def test_regpkg_emits_reg_and_runtime(tmp_path):
    status, output, errors = run_task(tmp_path, "pssc.RegPkg")
    assert status == 0, errors
    by_ft = filesets_by_type(output)
    assert "systemVerilogSource" in by_ft
    fs = by_ft["systemVerilogSource"][0]
    assert "pssc_reg_pkg.sv" in fs.files
    assert "zsp_rt_pkg.sv" in fs.files
    # incdir points at the bundled dir and files exist on disk
    assert fs.incdirs == [fs.basedir]
    for f in fs.files:
        assert os.path.isfile(os.path.join(fs.basedir, f))


@requires_dfm
def test_regpkg_runtime_false_omits_runtime(tmp_path):
    status, output, errors = run_task(tmp_path, "pssc.RegPkg", runtime=False)
    assert status == 0, errors
    fs = filesets_by_type(output)["systemVerilogSource"][0]
    assert fs.files == ["pssc_reg_pkg.sv"]


@requires_dfm
def test_corec_default_mmio(tmp_path):
    status, output, errors = run_task(tmp_path, "pssc.CoreC")
    assert status == 0, errors
    fs = filesets_by_type(output)["cSource"][0]
    assert "pssc_mem.h" in fs.files
    assert "pssc_mem_mmio.h" in fs.files
    assert "zsp_bridge.c" not in fs.files
    for f in fs.files:
        assert os.path.isfile(os.path.join(fs.basedir, f))


@requires_dfm
def test_corec_bridge_includes_zsp_bridge(tmp_path):
    status, output, errors = run_task(tmp_path, "pssc.CoreC", bridge=True)
    assert status == 0, errors
    fs = filesets_by_type(output)["cSource"][0]
    assert "zsp_bridge.c" in fs.files
    assert "zsp_bridge.h" in fs.files


@requires_dfm
def test_corec_bad_flavor_errors(tmp_path):
    status, output, errors = run_task(tmp_path, "pssc.CoreC", flavor="bogus")
    assert status != 0
    assert any("flavor" in e for e in errors)


@requires_dfm
def test_corecpp_emits_header(tmp_path):
    status, output, errors = run_task(tmp_path, "pssc.CoreCpp")
    assert status == 0, errors
    fs = filesets_by_type(output)["cppSource"][0]
    assert fs.files == ["pssc_reg.hpp"]
    assert os.path.isfile(os.path.join(fs.basedir, "pssc_reg.hpp"))
