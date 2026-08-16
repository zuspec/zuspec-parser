"""``op-model-py``: a PSS operation model as a plain Python module.

The third language in the operation-model family, and the first one written
after the shared layer existed. That is its second job: the walk
(`body_walker.py`), the call dispatch (`call_legality.py`), the elaborated model
(`op_model.py`), the folded register layout (`reg_layout.py`) and the API-type
collection (`sv/lower_api_types.py`) are all consumed here rather than
reimplemented, so what is left -- `targets/py/` -- is the part that is actually
about Python.

Its first job is to be useful: a generated module drives a duck-typed bus, which
is what a cocotb bring-up, a socket-attached debugger or a pure-Python device
model already has.

Plan: P8.T1.
"""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Dict, List

from .call_legality import BOTH, TARGET_ONLY, Disposition, Entry
from .op_model import OpModelTarget


def _e(name, disp, contexts, lrm="", unsupported=""):
    return Entry(name, disp, contexts, lrm, unsupported)


#: Why the two string built-ins are not renderable here. Python HAS strings,
#: which is exactly why this needs stating: the obstacle is not the type, it is
#: that PSS format specifiers (19) are not Python's and this backend implements
#: no translation between them. Emitting the string with the specifiers intact
#: would produce output that looks formatted and is not.
_NO_PY_FORMAT = (
    "it takes a PSS format string (LRM 19), whose specifiers are not Python's, "
    "and this backend implements no translation of them")

#: Likewise the PRNG. `random` is in the standard library, so this is a choice:
#: a generated module that imports nothing is one that runs wherever it is
#: copied, and seeding/determinism is a policy this backend has no way to state.
_NO_PY_PRNG = (
    "it needs a seeded PRNG, and how a generated driver is seeded is a policy "
    "decision this backend cannot make for its caller. Pass the values in")

_NO_PY_BLOCKING_CHANNEL = (
    "get()/put() suspend, and this backend generates no scheduler to suspend to "
    "(HAVE_EVENT_WAIT=false). A blocking channel call reaching the Python means "
    "the model asked for an event this target cannot deliver -- a modelling "
    "error, not something to lower to a spin. try_get/try_put are supported: "
    "see share/py/pssc_rt.py")


class PyProgSeqTarget(OpModelTarget):
    name = "op-model-py"
    description = "Python operation-model API generated from a component tree"
    language = "Python"

    #: Same position as the C target, and for the same reason: this backend
    #: emits plain methods, generates no scheduler and links no solver, so a
    #: caller here cannot suspend until another party posts an event. A POLLING
    #: wait needs no runtime support and is available -- `yield` lowers to
    #: nothing and the surrounding loop becomes a poll.
    target_cfg = {
        "HAVE_EVENT_WAIT": False,
        "HAVE_RUNTIME_SOLVER": False,
    }

    #: Declared here rather than registered at import, so registration happens
    #: once, at construction, in step with the target's own lifecycle.
    legality_entries = (
        _e("print", Disposition.UTILITY, BOTH, "21.1.2"),
        _e("format",        Disposition.UTILITY, BOTH, "21.1.2", _NO_PY_FORMAT),
        _e("format_string", Disposition.UTILITY, BOTH, "19", _NO_PY_FORMAT),
        _e("urandom",       Disposition.UTILITY, BOTH, "21.4", _NO_PY_PRNG),
        _e("urandom_range", Disposition.UTILITY, BOTH, "21.4", _NO_PY_PRNG),
        _e("get", Disposition.CHANNEL, TARGET_ONLY, "21.9.1",
           _NO_PY_BLOCKING_CHANNEL),
        _e("put", Disposition.CHANNEL, TARGET_ONLY, "21.9.1",
           _NO_PY_BLOCKING_CHANNEL),
        # Renderable: Chan1.try_get / try_put (DEPTH > 1 is rejected).
        _e("try_get", Disposition.CHANNEL, TARGET_ONLY, "21.9.1"),
        _e("try_put", Disposition.CHANNEL, TARGET_ONLY, "21.9.1"),
    )

    def __init__(self) -> None:
        super().__init__()
        # No `derives_from`, so `OpModelTarget.__init__` registers nothing and
        # this target's Tier-2 set has to be registered here. Stated rather than
        # inherited because this backend is NOT a restyled C target: it reaches
        # different conclusions about strings and randomness, and a `dict()`
        # copy of the C entry would silently hand it whatever that entry gains
        # next.
        from .call_legality import register_extension
        register_extension(self.name, self.legality_entries, replace=True)

    def add_args(self, parser: argparse.ArgumentParser) -> None:
        # `--root`, `--ctor-name` and `--no-core-copy` come from
        # `OpModelTarget`. This backend adds one option, and only one: the
        # generated module's name. Everything the C target spells as a flag --
        # the memory seam, the lifecycle, the register layout -- is either not a
        # choice in Python or is the bus object's business.
        super().add_args(parser)
        parser.add_argument(
            "--py-module", dest="py_module", metavar="NAME",
            help="op-model-py: generated module name (default: the root "
                 "component's name with a trailing _c stripped)",
        )

    # -- runtime source ------------------------------------------------------

    core_lang = "py"

    def core_file_names(self, model, opts) -> List[str]:
        """`pssc_rt.py`, whenever anything in the generation refers to it.

        Content-dependent, as the C++ backend's channel header is: the runtime
        is REQUIRED only by a model with channels, and copying it beside a model
        that imports nothing would leave a reader wondering what is missing. It
        is copied anyway for its `MemoryBus`, which is what a bring-up drives --
        so the honest rule is "always, and the import is what varies".
        """
        return ["pssc_rt.py"]

    # -- entry point ---------------------------------------------------------

    #: The backend class that assembles the module. Resolved late so importing
    #: this module does not drag the whole lowering in.
    backend_cls = None

    @classmethod
    def backend_class(cls):
        from .py.backend import PyOpModelBackend
        return cls.backend_cls or PyOpModelBackend

    def backend_for(self, opts: argparse.Namespace):
        """The backend instance this run generates through."""
        return self.backend_class()(getattr(opts, "py_module", None) or "")

    def sections(self, model, opts: argparse.Namespace) -> Dict[str, str]:
        return self.backend_for(opts).sections(model)

    def emit(self, model, opts: argparse.Namespace) -> List[Path]:
        # The generated module FIRST, then the runtime. Python resolves imports
        # at run time, so unlike the SV package this is not a compilation order
        # -- it is a reading order, and the generated file is what a reader
        # opens.
        be = self.backend_for(opts)
        return be.generate(model) + self.install_core(model, opts)
