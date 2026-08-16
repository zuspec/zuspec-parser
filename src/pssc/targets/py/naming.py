"""What a generated Python symbol is called.

One module, because a name is decided in one place and reconstructed in
several: the register-model lowering DEFINES `regs_csr_read`, the body emitter
CALLS it, and the manifest reports it. Those were three hand-kept tables in the
C backend before `mem_access.py` collected them, and that history is the whole
reason this file exists at 60 lines rather than as three helpers scattered
across the backend.

Python identifiers are permissive enough that most PSS names pass through
unchanged, which is deliberate: a generated API whose members are spelled the
way the model spells them is one an author can navigate without a mapping
table. Only two things are rewritten -- a keyword collision, and a component
type name becoming a class name.
"""
from __future__ import annotations

import keyword
from typing import Sequence

__all__ = ["mangle", "class_name", "module_name", "reg_symbol", "strip_suffix"]


def mangle(name: str) -> str:
    """A PSS name as a Python identifier.

    Only keywords are rewritten, with a trailing underscore -- PEP 8's own
    convention for exactly this, so `class` becomes `class_` and a reader knows
    why. PSS's identifier syntax is otherwise a subset of Python's.
    """
    return name + "_" if keyword.iskeyword(name) else name


def strip_suffix(name: str, suffix: str = "_c") -> str:
    """`wb_dma_c` -> `wb_dma`. The component-type naming convention, undone."""
    n = name.split("::")[-1]
    return n[:-len(suffix)] if suffix and n.endswith(suffix) else n


def class_name(comp_name: str) -> str:
    """A component type's Python class name: `wb_dma_ch_c` -> `WbDmaCh`.

    The one place a generated name does NOT mirror the model's spelling. PSS
    component types are lower_snake by convention and Python classes are
    CapWords by a convention just as strong, and a generated module that reads
    as foreign Python is one people wrap rather than use.
    """
    return "".join(p.title() for p in strip_suffix(comp_name).split("_") if p)


def module_name(root_name: str) -> str:
    """The generated module's name, without `.py`: `wb_dma_c` -> `wb_dma`."""
    return mangle(strip_suffix(root_name))


def reg_symbol(path: Sequence[str], reg: str, kind: str) -> str:
    """A register accessor method: `["regs"], "csr", "read"` -> `regs_csr_read`.

    The path is joined VERBATIM. `CSR` stays `CSR`, because the register's name
    is how the device's documentation refers to it and lower-casing it makes a
    reader check a datasheet against a transformation. The C backend reaches the
    same spelling by the same rule (`style.reg_symbol`).
    """
    return "_".join(list(path) + [reg, kind])
