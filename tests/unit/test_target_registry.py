"""Phase-2: target registry — register/get/list, clear error on unknown,
discover() no-op when off."""
import pytest

from pssc import targets
from pssc.targets.base import Target


def test_builtin_targets_registered():
    names = targets.list_targets()
    assert "sv-native" in names and "python" in names


def test_get_returns_target_with_name():
    t = targets.get("sv-native")
    assert isinstance(t, Target) and t.name == "sv-native"


def test_sv_alias_resolves():
    # `sv` is kept as a back-compat alias for `sv-native`
    assert targets.get("sv") is targets.get("sv-native")
    assert "sv" not in targets.list_targets()  # alias hidden from the canonical list


def test_unknown_target_clear_error():
    with pytest.raises(KeyError) as exc:
        targets.get("does-not-exist")
    msg = str(exc.value)
    assert "does-not-exist" in msg
    assert "sv" in msg and "python" in msg  # lists available


def test_register_and_roundtrip():
    class _Tmp(Target):
        name = "x-test-tmp"
        def run(self, ctx, opts):
            return []
    try:
        targets.register(_Tmp())
        assert "x-test-tmp" in targets.list_targets()
        assert targets.get("x-test-tmp").name == "x-test-tmp"
    finally:
        targets._REGISTRY.pop("x-test-tmp", None)


def test_register_requires_name():
    class _NoName(Target):
        def run(self, ctx, opts):
            return []
    with pytest.raises(ValueError):
        targets.register(_NoName())


def test_discover_adds_nothing_without_plugins():
    # Discovery is live now (Phase 3), but this checkout installs no plugin, so
    # the observable result is unchanged -- and must stay so under repetition.
    # The behaviour that replaced "no-op stub" is covered in
    # test_target_discovery.py against injected entry points.
    before = set(targets.list_targets())
    targets.discover()
    targets.discover()  # idempotent
    assert set(targets.list_targets()) == before
    assert targets.plugin_errors() == ()


def test_register_rejects_a_name_already_taken():
    class _Shadow(Target):
        name = "op-model-c"
        def run(self, ctx, opts):
            return []
    with pytest.raises(targets.TargetError) as exc:
        targets.register(_Shadow())
    assert "op-model-c" in str(exc.value)
    # the incumbent is untouched
    assert targets.get("op-model-c").__class__.__name__ == "CProgSeqTarget"
