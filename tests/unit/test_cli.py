"""Phase-2: CLI — subcommands, exit codes, -o creation, per-target args, --dump-ir."""
import yaml

from pssc.cli import main

SRC = "component pss_top { action A { rand bit[8] x; constraint x > 3; } }"


def _src(tmp_path):
    p = tmp_path / "m.pss"
    p.write_text(SRC)
    return str(p)


def test_version(capsys):
    import pytest
    # argparse's --version action prints and exits via SystemExit(0)
    with pytest.raises(SystemExit) as exc:
        main(["--version"])
    assert exc.value.code == 0
    assert "pssc" in capsys.readouterr().out


def test_targets_lists_builtins(capsys):
    code = main(["targets"])
    out = capsys.readouterr().out
    assert code == 0 and "sv" in out and "python" in out


def test_compile_python_creates_outdir(tmp_path, capsys):
    out = tmp_path / "made" / "here"
    code = main(["compile", _src(tmp_path), "-t", "python",
                 "--emit", "repr", "-o", str(out)])
    assert code == 0
    assert (out / "pss_classes.txt").is_file()


def test_compile_sv(tmp_path):
    out = tmp_path / "sv"
    code = main(["compile", _src(tmp_path), "-t", "sv", "-o", str(out)])
    assert code == 0 and (out / "zsp_gen_pkg.sv").is_file()


def test_unknown_target_exit_1(tmp_path, capsys):
    code = main(["compile", _src(tmp_path), "-t", "bogus"])
    assert code == 1
    assert "bogus" in capsys.readouterr().err


def test_parse_dump_ir_writes_valid_yaml(tmp_path, capsys):
    irf = tmp_path / "m.ir.yaml"
    code = main(["parse", _src(tmp_path), "--dump-ir", str(irf)])
    assert code == 0 and irf.is_file()
    data = yaml.safe_load(irf.read_text())
    assert data["_type"] == "Context"


def test_per_target_arg_wired(tmp_path):
    # --emit is contributed by the python target's add_args
    out = tmp_path / "o"
    code = main(["compile", _src(tmp_path), "-t", "python", "--emit", "none",
                 "-o", str(out)])
    assert code == 0 and not (out / "pss_classes.txt").exists()


def test_no_subcommand_prints_help(capsys):
    code = main([])
    assert code == 0
    assert "usage" in capsys.readouterr().out.lower()
