"""Phase-2: target registry — register/get/list, clear error on unknown,
discover() no-op when off."""
import pytest

from pssc import targets
from pssc.targets.base import Target


def test_builtin_targets_registered():
    names = targets.list_targets()
    assert "sv" in names and "python" in names


def test_get_returns_target_with_name():
    t = targets.get("sv")
    assert isinstance(t, Target) and t.name == "sv"


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


def test_discover_is_noop_when_off():
    before = set(targets.list_targets())
    targets.discover()
    targets.discover()  # idempotent
    assert set(targets.list_targets()) == before
