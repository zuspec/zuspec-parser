"""Phase 6a (P6a.T2): the named-section list.

The whole value of the module is in the failure case. A list of callables would
already let a backend assemble a file; what it would NOT do is tell an
extension author that the section they inserted after no longer exists -- their
customisation would just stop appearing, in generated code they do not read
every day.
"""
from __future__ import annotations

import pytest

from pssc.targets.sections import (
    Section, UnknownSection, index_of, insert_after, insert_before, names,
    remove, replace,
)


def _s(name, text=None):
    return Section(name, lambda *a, **kw: [text or name])


@pytest.fixture
def three():
    return [_s("a"), _s("b"), _s("c")]


# -- an unknown name is an error, in every operation -------------------------

@pytest.mark.parametrize("op", [
    lambda s: insert_after(s, "nope", _s("x")),
    lambda s: insert_before(s, "nope", _s("x")),
    lambda s: replace(s, "nope", _s("x")),
    lambda s: remove(s, "nope"),
    lambda s: index_of(s, "nope"),
])
def test_an_unknown_section_name_raises(three, op):
    with pytest.raises(UnknownSection):
        op(three)


def test_the_message_lists_what_is_available(three):
    """An extension author is reading a backend they did not write."""
    with pytest.raises(UnknownSection) as e:
        remove(three, "includes")
    msg = str(e.value)
    assert "'includes'" in msg and "'a'" in msg and "'c'" in msg


# -- order is preserved ------------------------------------------------------

def test_insert_after_lands_after(three):
    assert names(insert_after(three, "a", _s("x"))) == ["a", "x", "b", "c"]


def test_insert_before_lands_before(three):
    assert names(insert_before(three, "c", _s("x"))) == ["a", "b", "x", "c"]


def test_insert_at_the_end(three):
    assert names(insert_after(three, "c", _s("x"))) == ["a", "b", "c", "x"]


def test_several_sections_keep_their_own_order(three):
    assert names(insert_after(three, "a", _s("x"), _s("y"))) == \
        ["a", "x", "y", "b", "c"]


def test_replace_keeps_the_position(three):
    """Not remove-then-append: order is what a backend's correctness depends
    on, and a replacement that also moved would be a second change."""
    out = replace(three, "b", _s("b2"))
    assert names(out) == ["a", "b2", "c"]
    assert out[1].emit() == ["b2"]


def test_remove_takes_exactly_one(three):
    assert names(remove(three, "b")) == ["a", "c"]


def test_the_input_list_is_not_mutated(three):
    for op in (insert_after, insert_before):
        op(three, "a", _s("x"))
    replace(three, "a", _s("x"))
    remove(three, "a")
    assert names(three) == ["a", "b", "c"]


def test_a_section_unpacks_as_a_pair():
    name, emit = _s("a", "text")
    assert name == "a" and emit() == ["text"]


# -- against the real backend ------------------------------------------------

def test_the_c_backend_sections_are_addressable_by_name():
    """The names are the published surface: an extension inserting after
    'accessors' must not need to know the list's length or shape."""
    from pssc.targets.c.backend import COpModelBackend

    be = COpModelBackend()
    listed = names(be.header_sections(None, None))
    assert listed[0] == "banner" and listed[-1] == "guard_close"
    for expected in ("includes", "api_types", "handles", "accessors",
                     "imports", "decls"):
        assert expected in listed
