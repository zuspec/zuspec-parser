"""A house style for `op-model-c`, shipped by a third-party package.

The point of this file is that it is SHORT. Tier A's claim is that an
organisation can mandate its own register macros without forking the backend;
if that takes more than a few methods, the claim is false. What is here is the
whole of it -- rename the symbols, render the accesses, decline pssc's seam.
"""
from pssc.targets.c.style import CStylePolicy


class AcmeStyle(CStylePolicy):
    name = "acme"
    description = "ACME house style: ACME_ prefixes and ACME_RD/WR macros"

    def symbol(self, comp_prefix, name):
        return f"acme_{comp_prefix}_{name}"

    def reg_accessor_form(self):
        return "macro"

    def render_reg_read(self, acc, handle, idx_args, raw):
        return f"ACME_RD{acc.prim}({acc.base}_addr({handle}{idx_args}))"

    def render_reg_write(self, acc, handle, idx_args, value, raw):
        return (f"ACME_WR{acc.prim}({acc.base}_addr({handle}{idx_args}), "
                f"{value})")

    def render_reg_masked_write(self, acc, handle, idx_args, mask, val):
        addr = f"{acc.base}_addr({handle}{idx_args})"
        cur = f"ACME_RD{acc.prim}({addr})"
        return f"ACME_WR{acc.prim}({addr}, ({cur} & ~{mask}) | ({val} & {mask}))"

    def render_mem_read(self, width, bus, addr):
        return f"ACME_RD{width}({addr})"

    def render_mem_write(self, width, bus, addr, value):
        return f"ACME_WR{width}({addr}, {value})"

    def seam_headers(self, link_style):
        return ()               # ACME supplies its own; copy none of pssc's

    def include_order(self, model, s):
        return ["#include <stdint.h>", '#include "acme_regs.h"']
