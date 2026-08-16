"""A tier-B extension: `op-model-c` with ACME's house conventions.

TIER A (a style policy) can change what things are CALLED. This is the next
tier up -- the changes an organisation actually asks for that a naming policy
cannot express:

  * a compliance banner in every generated header      (an inserted SECTION)
  * a trace call at the top of every operation         (a wrapped emit_operation)
  * a register-map header beside the API               (an EXTRA FILE)
  * ACME's naming, without publishing an entry point   (a swapped style_cls)

It is the validation for P6b's override surface, and its LENGTH is the
criterion: if a change of this size cannot be written short, against methods
pssc marks as overridable, then the marked set is wrong (design §6). Nothing
here reaches past a marked method, and nothing here is a copy of pssc's code.
"""
from __future__ import annotations

from pssc.targets.c.backend import COpModelBackend
from pssc.targets.c.style import CStylePolicy
from pssc.targets.c_progseq_tgt import CProgSeqTarget
from pssc.targets.sections import Section, insert_after


class AcmeHouseStyle(CStylePolicy):
    """Tier A, reused from inside tier B: `acme_` on every exported symbol.

    Not registered as a `pssc.styles` entry point -- the backend names it as
    its `style_cls`, which is what a house backend wants: the policy is not one
    of several the user picks between, it is what this target IS.
    """
    name = "acme-house"
    description = "ACME house naming"

    def symbol(self, comp_prefix, name):
        return f"acme_{comp_prefix}_{name}"


class AcmeBackend(COpModelBackend):
    """The four override kinds, one each."""

    style_cls = AcmeHouseStyle

    #: 1. An inserted section. `insert_after` raises if `banner` is ever
    #: renamed upstream, so this cannot silently stop taking effect.
    def header_sections(self, model, s):
        return insert_after(
            super().header_sections(model, s), "banner",
            Section("acme_compliance", self.emit_compliance))

    def emit_compliance(self, model, s):
        return ["/* ACME-INTERNAL. Generated; see PLM-4417 before editing. */",
                ""]

    #: 2. A wrapped operation: a trace call inside every generated function,
    #: which a style policy cannot add and a body emitter never sees (it is
    #: not a statement of the model's).
    def emit_operation(self, fn, ctx):
        lines = super().emit_operation(fn, ctx)
        opened = next(i for i, ln in enumerate(lines) if ln.endswith(" {"))
        trace = f'    ACME_TRACE("{ctx.prefix}", "{fn.name}");'
        return lines[:opened + 1] + [trace] + lines[opened + 1:]

    #: 3. An extra file, written by the same call that writes the API and
    #: reported to the build system in the same list.
    def emit_extra_files(self, model, s):
        lines = [f"/* ACME register map for {s.prefix}. Generated. */",
                 "#pragma once"]
        for comp in self.comps:
            for group in getattr(comp, "fields", None) or []:
                name = getattr(group, "name", None)
                if name:
                    lines.append(f"/*   {self.prefixes[comp]}.{name} */")
        return {f"{s.prefix}_acme_map.h": "\n".join(lines) + "\n"}


class AcmeCTarget(CProgSeqTarget):
    """The target. Everything not stated here -- every option, every legality
    entry, every capability flag, every style -- comes from `op-model-c`."""

    name = "op-model-acme-c"
    description = "ACME house C API (tier-B extension of op-model-c)"
    derives_from = "op-model-c"
    backend_cls = AcmeBackend
