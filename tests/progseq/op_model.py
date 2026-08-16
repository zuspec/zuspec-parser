"""The checked-in copy of the real operation model, and how to read it.

`examples/op_model/pss/` is a digest-checked copy of fw-wb-dma's `src/pss/`
(scripts/sync_op_model.py). Its `files.f` is the statement of which files make
up the model AND of the order they must be presented in -- see
`op_model_rel_paths` for why the order is not negotiable.

A module rather than fixtures in conftest.py: several test modules need these
as plain functions at import time, and a bare `conftest` import resolves to
the wrong file when tests are packages.
"""
import os

#: The checked-in copy of the real operation model (see scripts/sync_op_model.py).
OP_MODEL = os.path.normpath(os.path.join(
    os.path.dirname(__file__), "..", "..", "examples", "op_model", "pss"))

#: How `files.f` spells an entry that came from upstream `src/pss`. Entries
#: WITHOUT this prefix are files the sync generates into the copy and that have
#: no upstream path -- today, the snapshot of the generated register package.
_UPSTREAM_PREFIX = "src/pss/"


def op_model_files_f():
    """`files.f`'s entries, verbatim, comments and blanks dropped."""
    with open(os.path.join(OP_MODEL, "files.f")) as fp:
        return [ln.strip() for ln in fp
                if ln.strip() and not ln.startswith("#")]


def op_model_rel_paths():
    """`files.f` as paths relative to the copy root, in order.

    The order is the whole point: a file presented before something it
    references is left unresolved while the front end still reports 0 errors
    (pssparser D3). Sorting these, or building the list by walking the tree,
    silently produces a different and wrong model.
    """
    return [p[len(_UPSTREAM_PREFIX):] if p.startswith(_UPSTREAM_PREFIX) else p
            for p in op_model_files_f()]


def op_model_sources():
    """`files.f` as absolute paths, in dependency order."""
    return [os.path.join(OP_MODEL, p) for p in op_model_rel_paths()]
