"""Phase 3 (P3.T1/P3.T2): entry-point discovery and registration policy.

Entry points are INJECTED rather than installed. Installing a package to test
discovery makes the unit suite depend on a writable environment and on pip
being on the path, which is the sort of dependency that gets a suite skipped in
CI and then quietly stays skipped. `_entry_points()` is the seam, and the real
end-to-end path against installed metadata is P3.T6's job, marked `plugin` so
it can be selected separately.
"""
from __future__ import annotations

import pytest

from pssc import targets
from pssc.targets.base import Target


# -- fakes ------------------------------------------------------------------

class _FakeDist:
    def __init__(self, name="fixture-plugin", version="0.1"):
        self.name = name
        self.version = version


class _FakeEP:
    """Enough of importlib.metadata.EntryPoint for discovery: name, dist, load."""

    def __init__(self, name, loader, dist=None):
        self.name = name
        self._loader = loader
        self.dist = dist if dist is not None else _FakeDist()

    def load(self):
        return self._loader() if callable(self._loader) else self._loader


def _target_cls(target_name, api=None):
    ns = {"name": target_name,
          "description": f"fixture target {target_name}",
          "run": lambda self, ctx, opts: []}
    if api is not None:
        ns["PSSC_TARGET_API"] = api
    return type(f"_T_{target_name.replace('-', '_')}", (Target,), ns)


@pytest.fixture
def discovery(monkeypatch):
    """Run discovery over an injected entry-point list, then restore the registry.

    The registry is process-global and the built-ins are registered at import,
    so every test here has to put it back exactly as it found it -- including
    the `_discovered` latch, which otherwise makes the NEXT test's discover()
    silently do nothing.
    """
    saved = dict(targets._REGISTRY)
    saved_errors = list(targets._PLUGIN_ERRORS)
    saved_latch = targets._discovered

    def run(eps, no_plugins=False):
        monkeypatch.setattr(targets, "_entry_points", lambda: list(eps))
        if no_plugins:
            monkeypatch.setenv(targets.NO_PLUGINS_ENV, "1")
        else:
            monkeypatch.delenv(targets.NO_PLUGINS_ENV, raising=False)
        targets.discover(force=True)

    yield run

    targets._REGISTRY.clear()
    targets._REGISTRY.update(saved)
    targets._PLUGIN_ERRORS.clear()
    targets._PLUGIN_ERRORS.extend(saved_errors)
    targets._discovered = saved_latch


# -- accepted shapes --------------------------------------------------------

def test_a_target_subclass_is_instantiated(discovery):
    discovery([_FakeEP("cls", _target_cls("x-cls"))])
    assert targets.plugin_errors() == ()
    assert isinstance(targets.get("x-cls"), Target)


def test_a_target_instance_is_used_as_is(discovery):
    inst = _target_cls("x-inst")()
    discovery([_FakeEP("inst", inst)])
    assert targets.get("x-inst") is inst


def test_a_zero_arg_callable_is_called(discovery):
    discovery([_FakeEP("fn", lambda: _target_cls("x-fn")())])
    assert targets.get("x-fn").name == "x-fn"


def test_a_callable_returning_an_iterable_registers_the_family(discovery):
    def family():
        return [_target_cls("x-fam-a")(), _target_cls("x-fam-b")]
    discovery([_FakeEP("fam", family)])
    assert targets.get("x-fam-a").name == "x-fam-a"
    assert targets.get("x-fam-b").name == "x-fam-b"


def test_declared_aliases_are_registered(discovery):
    cls = _target_cls("x-aliased")
    cls.aliases = ("x-alias-1", "x-alias-2")
    discovery([_FakeEP("aliased", cls)])
    assert targets.get("x-alias-1") is targets.get("x-aliased")
    assert "x-alias-1" not in targets.list_targets()   # aliases stay hidden


def test_a_bad_shape_is_reported_not_raised(discovery):
    discovery([_FakeEP("junk", lambda: 42)])
    assert [e.entry_point for e in targets.plugin_errors()] == ["junk"]
    assert "int" in str(targets.plugin_errors()[0])


# -- all-or-none ------------------------------------------------------------

def test_a_family_registers_all_or_none(discovery):
    # The third target collides with a built-in, so the first two must not
    # survive: half a family with no indication of which half is worse than
    # none of it.
    def family():
        return [_target_cls("x-part-a")(), _target_cls("x-part-b")(),
                _target_cls("op-model-c")()]
    discovery([_FakeEP("partial", family)])
    assert targets.plugin_errors(), "the collision must be reported"
    assert "x-part-a" not in targets.list_targets()
    assert "x-part-b" not in targets.list_targets()
    assert targets.get("op-model-c").__class__.__name__ == "CProgSeqTarget"


def test_one_raising_entry_point_does_not_block_the_others(discovery):
    def boom():
        raise ImportError("no module named 'nope'")
    discovery([_FakeEP("bad", boom),
               _FakeEP("good", _target_cls("x-good"))])
    assert targets.get("x-good").name == "x-good"
    errs = targets.plugin_errors()
    assert len(errs) == 1 and errs[0].entry_point == "bad"
    assert "ImportError" in str(errs[0]) and "nope" in str(errs[0])
    assert "fixture-plugin 0.1" in str(errs[0])


def test_an_entry_point_contributing_nothing_is_an_error(discovery):
    discovery([_FakeEP("empty", lambda: [])])
    assert len(targets.plugin_errors()) == 1


# -- policy -----------------------------------------------------------------

def test_collision_is_error(discovery):
    discovery([_FakeEP("shadow", _target_cls("op-model-sv"))])
    errs = targets.plugin_errors()
    assert len(errs) == 1
    msg = str(errs[0])
    assert "op-model-sv" in msg and "built-in" in msg and "replaces=" in msg
    assert targets.get("op-model-sv").__class__.__name__ == "ProgSeqTarget"


def test_alias_collision_is_also_an_error(discovery):
    cls = _target_cls("x-fresh-name")
    cls.aliases = ("c-progseq",)      # an alias of a built-in
    discovery([_FakeEP("aliashadow", cls)])
    assert len(targets.plugin_errors()) == 1
    assert "c-progseq" in str(targets.plugin_errors()[0])
    assert "x-fresh-name" not in targets.list_targets()
    assert targets.get("c-progseq").__class__.__name__ == "CProgSeqTarget"


def test_replaces_allows_override(discovery):
    cls = _target_cls("op-model-c")
    cls.replaces = ("op-model-c",)
    discovery([_FakeEP("deliberate", cls)])
    assert targets.plugin_errors() == ()
    assert targets.get("op-model-c").__class__.__name__ == "_T_op_model_c"


def test_replaces_does_not_license_an_unnamed_collision(discovery):
    cls = _target_cls("op-model-c")
    cls.replaces = ("op-model-sv",)   # names the WRONG target
    discovery([_FakeEP("sloppy", cls)])
    assert len(targets.plugin_errors()) == 1
    assert targets.get("op-model-c").__class__.__name__ == "CProgSeqTarget"


def test_api_version_mismatch_refused(discovery):
    discovery([_FakeEP("future", _target_cls("x-future", api=2))])
    errs = targets.plugin_errors()
    assert len(errs) == 1
    msg = str(errs[0])
    assert "x-future" not in targets.list_targets()
    assert "API 2" in msg and f"API {Target.PSSC_TARGET_API}" in msg
    assert "fixture-plugin 0.1" in msg          # names the plugin
    assert "_T_x_future" in msg                 # ...and the class


def test_api_version_must_be_an_integer(discovery):
    discovery([_FakeEP("stringy", _target_cls("x-stringy", api="1"))])
    assert len(targets.plugin_errors()) == 1
    assert "x-stringy" not in targets.list_targets()


def test_matching_api_version_loads(discovery):
    discovery([_FakeEP("ok", _target_cls("x-ok", api=Target.PSSC_TARGET_API))])
    assert targets.plugin_errors() == ()
    assert "x-ok" in targets.list_targets()


# -- switches ---------------------------------------------------------------

def test_no_plugins_env_loads_none(discovery):
    discovery([_FakeEP("cls", _target_cls("x-off"))], no_plugins=True)
    assert "x-off" not in targets.list_targets()
    assert targets.plugin_errors() == ()


def test_discovery_is_idempotent(discovery, monkeypatch):
    calls = []

    def eps():
        calls.append(1)
        return [_FakeEP("once", _target_cls("x-once"))]

    monkeypatch.delenv(targets.NO_PLUGINS_ENV, raising=False)
    monkeypatch.setattr(targets, "_entry_points", eps)
    targets.discover(force=True)
    targets.discover()
    targets.discover()
    assert calls == [1], "the second call must not re-scan"
    assert "x-once" in targets.list_targets()


def test_a_broken_scan_is_reported_not_raised(discovery, monkeypatch):
    monkeypatch.delenv(targets.NO_PLUGINS_ENV, raising=False)

    def boom():
        raise RuntimeError("unreadable metadata on sys.path")
    monkeypatch.setattr(targets, "_entry_points", boom)
    targets.discover(force=True)          # must not raise
    assert len(targets.plugin_errors()) == 1
    assert "python" in targets.list_targets()


# -- built-ins --------------------------------------------------------------

def test_builtins_are_identified_as_such():
    assert targets.is_builtin("op-model-c")
    assert targets.is_builtin("c-progseq")     # through an alias
    assert not targets.is_builtin("does-not-exist")
