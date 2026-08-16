"""Phase 5b (P5b.T2): the `pssc.styles` entry-point group.

Entry points are injected rather than installed -- `test_plugin_integration.py`
covers the really-installed path, and what is under test here is the POLICY:
which shapes load, what a collision does, and that a broken style package costs
you the style and not the compiler.
"""
from __future__ import annotations

import pytest

from pssc.targets import style as st
from pssc.targets.c.style import CStylePolicy


class _FakeEP:
    def __init__(self, name, obj, dist=None):
        self.name = name
        self._obj = obj
        self.dist = dist

    def load(self):
        if isinstance(self._obj, BaseException):
            raise self._obj
        return self._obj


class _FakeDist:
    def __init__(self, name="acme-styles", version="2.0"):
        self.name = name
        self.version = version


def _style_cls(name="acme", target="op-model-c"):
    return type("_S", (CStylePolicy,), {"name": name, "target": target})


@pytest.fixture
def discovery(monkeypatch):
    """Inject entry points, and put the registry back afterwards."""
    saved = dict(st._REGISTRY)
    saved_errors = list(st._STYLE_ERRORS)
    saved_latch = st._discovered

    def inject(*eps):
        monkeypatch.setattr(st, "_entry_points", lambda: list(eps))
        monkeypatch.delenv(st.NO_PLUGINS_ENV, raising=False)
        st.discover(force=True)

    yield inject

    st._REGISTRY.clear()
    st._REGISTRY.update(saved)
    st._STYLE_ERRORS.clear()
    st._STYLE_ERRORS.extend(saved_errors)
    st._discovered = saved_latch


# -- the shapes that load ----------------------------------------------------

def test_a_style_class_is_instantiated(discovery):
    discovery(_FakeEP("acme", _style_cls()))
    assert isinstance(st.get("op-model-c", "acme"), CStylePolicy)


def test_a_style_instance_is_used_as_is(discovery):
    inst = _style_cls()()
    discovery(_FakeEP("acme", inst))
    assert st.get("op-model-c", "acme") is inst


def test_a_callable_returning_a_family_registers_all_of_them(discovery):
    """One entry point, several styles -- what a company shipping `acme-lean`
    and `acme-traced` alongside `acme` writes."""
    def family():
        return [_style_cls("acme"), _style_cls("acme-lean")]

    discovery(_FakeEP("acme", family))
    assert st.list_styles("op-model-c") == ["acme", "acme-lean", "default"]


def test_the_wrong_kind_of_object_is_reported_not_fatal(discovery):
    discovery(_FakeEP("junk", 42, _FakeDist()))
    assert st.list_styles("op-model-c") == ["default"]
    assert "expected a StylePolicy" in str(st.style_errors()[0])
    assert "acme-styles 2.0" in str(st.style_errors()[0])


# -- failure is contained ----------------------------------------------------

def test_a_style_that_raises_on_import_costs_only_itself(discovery):
    discovery(_FakeEP("bad", ImportError("no acme_sdk"), _FakeDist()),
              _FakeEP("good", _style_cls("good")))
    assert "good" in st.list_styles("op-model-c")
    assert "no acme_sdk" in str(st.style_errors()[0])
    # ...and the built-in is still there, which is the thing that matters
    assert st.get("op-model-c", "default") is not None


def test_a_family_registers_all_or_none(discovery):
    """A family colliding on its third style must not leave the first two
    behind: half a house style is worse than none, because the output looks
    styled."""
    def family():
        return [_style_cls("one"), _style_cls("two"), _style_cls("default")]

    discovery(_FakeEP("acme", family))
    assert st.list_styles("op-model-c") == ["default"]
    assert st.get("op-model-c", "default").name == "default"


def test_a_collision_names_what_holds_the_name(discovery):
    discovery(_FakeEP("dup", _style_cls("default")))
    err = str(st.style_errors()[0])
    assert "op-model-c:default" in err and "replaces=True" in err


def test_no_plugins_env_skips_style_discovery(discovery, monkeypatch):
    monkeypatch.setenv(st.NO_PLUGINS_ENV, "1")
    monkeypatch.setattr(st, "_entry_points",
                        lambda: [_FakeEP("acme", _style_cls())])
    st.discover(force=True)
    assert st.list_styles("op-model-c") == ["default"]
    assert st.style_errors() == ()


# -- keyed by target ---------------------------------------------------------

def test_two_targets_may_both_have_an_acme(discovery):
    discovery(_FakeEP("c", _style_cls("acme", "op-model-c")),
              _FakeEP("sv", _style_cls("acme", "op-model-sv")))
    assert st.get("op-model-c", "acme").target == "op-model-c"
    assert st.get("op-model-sv", "acme").target == "op-model-sv"


def test_the_builtin_c_style_is_registered_without_any_plugin():
    """`discover()` registers it lazily -- `c/style.py` imports this module, so
    doing it at import time is a cycle."""
    assert "default" in st.list_styles("op-model-c")
    assert st.is_builtin("op-model-c", "default")
