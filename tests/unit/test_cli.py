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


def test_shared_sv_option_registered_once():
    # Target variants that inherit options (e.g. sv-pure extends sv-native, both
    # declaring --no-rt-pkg) must not collide in the single compile parser.
    from pssc.cli import build_parser

    parser = build_parser()  # must not raise argparse.ArgumentError
    compile_parser = parser._subparsers._group_actions[0].choices["compile"]
    no_rt = [a for a in compile_parser._actions if "--no-rt-pkg" in a.option_strings]
    assert len(no_rt) == 1


def test_targets_lists_builtins(capsys):
    code = main(["targets"])
    out = capsys.readouterr().out
    assert code == 0 and "sv" in out and "python" in out


def test_targets_prints_the_override_surface(capsys):
    """P6b.T1. An extension author's first question is "what may I override,
    and what happens to it next release"; without this the answer is to read
    pssc's source and guess, which is how an unmarked method becomes somebody's
    API."""
    code = main(["targets", "--overrides", "op-model-c"])
    out = capsys.readouterr().out
    assert code == 0
    assert "header_sections" in out and "stable" in out
    assert "body_emitter_cls" in out and "provisional" in out
    assert "pairs with emit_guard_close" in out


def test_targets_overrides_of_a_target_without_one_is_an_error(capsys):
    code = main(["targets", "--overrides", "python"])
    assert code == 1
    assert "no override surface" in capsys.readouterr().err


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


# --- Phase 3: plugin errors and option policy -------------------------------

import argparse
import pytest

from pssc import targets as _targets
from pssc.cli import _DedupArgGroup, OptionPolicyError, build_parser
from pssc.targets.base import Target


class _Broken:
    """Stands in for an entry point whose package fails to import."""
    name = "brokenplug"
    dist = None

    def load(self):
        raise ImportError("libfoo.so: cannot open shared object file")


@pytest.fixture
def failed_plugin(monkeypatch):
    saved = list(_targets._PLUGIN_ERRORS)
    saved_latch = _targets._discovered
    monkeypatch.delenv(_targets.NO_PLUGINS_ENV, raising=False)
    monkeypatch.setattr(_targets, "_entry_points", lambda: [_Broken()])
    _targets.discover(force=True)
    assert _targets.plugin_errors()
    yield
    _targets._PLUGIN_ERRORS.clear()
    _targets._PLUGIN_ERRORS.extend(saved)
    _targets._discovered = saved_latch


def test_targets_reports_failed_plugin(failed_plugin, capsys):
    code = main(["targets"])
    cap = capsys.readouterr()
    assert code == 0, "the listing is still correct; a bad plugin is not fatal"
    assert "python" in cap.out           # ...and still pipeable, on stdout
    assert "brokenplug" in cap.err
    assert "ImportError" in cap.err and "libfoo.so" in cap.err
    assert "PSSC_NO_PLUGINS" in cap.err  # names the bisect switch
    assert "Traceback" not in cap.err


def test_unknown_target_mentions_failed_plugin(failed_plugin, tmp_path, capsys):
    code = main(["compile", _src(tmp_path), "-t", "brokenplug"])
    err = capsys.readouterr().err
    assert code == 1
    assert "brokenplug" in err and "ImportError" in err
    # `e.args[0]`, not `str(KeyError)`: the whole sentence used to arrive
    # wrapped in repr() quotes.
    assert "\\n" not in err and not err.lstrip().startswith("pssc: error: \"")


# -- option policy -----------------------------------------------------------

def _group():
    return _DedupArgGroup(argparse.ArgumentParser())


def test_builtin_dedup_still_first_wins():
    g = _group()
    a = g.for_target("built-a", is_plugin=False).add_argument("--shared")
    b = g.for_target("built-b", is_plugin=False).add_argument("--shared")
    assert a is not None and b is None


def test_plugin_option_collision_raises():
    # The namespace rule below makes plugin-vs-plugin collision unreachable
    # (two plugins cannot share a target name -- registration refuses it), so
    # the case this guards is a plugin whose namespaced option a built-in
    # already claimed. Contrived, but it is the difference between an error and
    # the plugin's option silently resolving to somebody else's dest.
    g = _group()
    g.for_target("built-a", is_plugin=False).add_argument("--myplug-style")
    with pytest.raises(OptionPolicyError) as exc:
        g.for_target("myplug", is_plugin=True).add_argument("--myplug-style")
    msg = str(exc.value)
    assert "myplug" in msg and "built-a" in msg and "--myplug-style" in msg


def test_an_unnamespaced_plugin_option_is_refused_before_it_can_collide():
    g = _group()
    g.for_target("built-a", is_plugin=False).add_argument("--prefix")
    with pytest.raises(OptionPolicyError) as exc:
        g.for_target("myplug", is_plugin=True).add_argument("--prefix")
    # The namespace violation is the more actionable of the two diagnoses:
    # renaming the option fixes both.
    assert "not namespaced" in str(exc.value)


def test_plugin_option_must_be_namespaced():
    g = _group()
    with pytest.raises(OptionPolicyError) as exc:
        g.for_target("myplug", is_plugin=True).add_argument("--style")
    msg = str(exc.value)
    assert "--myplug-" in msg and "-X style=VALUE" in msg


def test_a_namespaced_plugin_option_registers():
    g = _group()
    assert g.for_target("myplug", is_plugin=True).add_argument(
        "--myplug-style", default="a") is not None


def test_target_opt_roundtrip(tmp_path):
    parser = build_parser()
    args = parser.parse_args(["compile", _src(tmp_path),
                              "-X", "style=terse", "-X", "verbose"])
    tgt = _targets.get("python")
    assert tgt.opt(args, "style") == "terse"
    assert tgt.opt(args, "verbose") == "true"    # bare NAME means true
    assert tgt.opt_bool(args, "verbose") is True
    assert tgt.opt(args, "absent", default="d") == "d"
    assert tgt.opt_bool(args, "absent") is False


def test_target_opt_last_wins(tmp_path):
    parser = build_parser()
    args = parser.parse_args(["compile", _src(tmp_path),
                              "-X", "style=a", "-X", "style=b"])
    assert _targets.get("python").opt(args, "style") == "b"


def test_target_opt_choices_validated(tmp_path):
    parser = build_parser()
    args = parser.parse_args(["compile", _src(tmp_path), "-X", "style=nope"])
    tgt = _targets.get("python")
    with pytest.raises(ValueError) as exc:
        tgt.opt(args, "style", choices=("terse", "full"))
    assert "nope" in str(exc.value) and "terse, full" in str(exc.value)
    assert tgt.opt(args, "style", choices=("nope",)) == "nope"


def test_target_opt_bool_rejects_a_non_boolean(tmp_path):
    parser = build_parser()
    args = parser.parse_args(["compile", _src(tmp_path), "-X", "fast=maybe"])
    with pytest.raises(ValueError) as exc:
        _targets.get("python").opt_bool(args, "fast")
    assert "maybe" in str(exc.value)


def test_target_opt_absent_is_empty(tmp_path):
    parser = build_parser()
    args = parser.parse_args(["compile", _src(tmp_path)])
    assert Target.parse_target_opts(args) == {}


def test_malformed_target_opt_is_reported(tmp_path):
    parser = build_parser()
    args = parser.parse_args(["compile", _src(tmp_path), "-X", "=value"])
    with pytest.raises(ValueError, match="NAME=VALUE"):
        Target.parse_target_opts(args)
