"""Emit the data types a C++ programming API mentions: enums and plain structs.

The C++ analogue of ``targets/c/lower_api_types.py``, and like it, it reuses
``sv.lower_api_types.collect_api_types``: WHICH types an API mentions is a
property of the model, not of the output language, and three collectors would
be three answers to one question. Only the rendering is here.

Register *value* structs are emitted by ``lower_reg_model``; this covers the
other half -- the enums and structs that appear in operation signatures, in
local declarations, and as component attributes.
"""
from __future__ import annotations

from typing import List

from ..progseq_model import _dt_name
from ..sv.lower_api_types import collect_api_types, _strip_pkg
from ..c.lower_reg_model import c_struct_name

_DT_ENUM = "DataTypeEnum"
_DT_STRUCT = "DataTypeStruct"
_DT_INT = "DataTypeInt"
_DT_BOOL = "DataTypeBool"


def cpp_enum_name(enum_dtype) -> str:
    return _strip_pkg(enum_dtype.name)


def emit_enum(enum_dtype) -> str:
    """An UNSCOPED enum with an explicit underlying type and explicit values.

    Unscoped, and this is the one place the C++ output deliberately declines
    the more modern spelling. A PSS enum IS an integer: the model compares one
    against an integer expression, casts one to a register field, and switches
    on a subject that arrives as a raw value from a register read. Under `enum
    class` every one of those becomes a `static_cast` the generator would have
    to insert, and the generator would have to decide at each use site whether
    the operand is meant as the enum or as its value -- a judgement it cannot
    make from the IR, and one it would get wrong silently in exactly the places
    that matter (a field encoding).

    EXPLICIT VALUES for the same reason as in C: the numbers are register field
    encodings and cross-language contract. Implicit numbering would reproduce
    them today and renumber them the day someone reorders the PSS declaration.

    An explicit underlying type is what unscoped enums lack by default -- the
    size would otherwise be implementation-defined, which matters as soon as
    one appears in a struct that is memcpy'd.
    """
    name = cpp_enum_name(enum_dtype)
    items = ",\n".join(f"    {k} = {v}" for k, v in enum_dtype.items.items())
    return f"enum {name} : int {{\n{items}\n}};"


def cpp_member_type(dtype) -> str:
    """C++ type for a plain-struct member.

    Bit-exact widths are NOT expressed as bitfields here: bitfield layout is
    implementation-defined, so `std::uint32_t x : 3` claims something the
    standard does not guarantee. Register value structs -- the ones that DO
    have a defined layout -- go through `lower_reg_model`. What is left has no
    layout contract, so a member takes the smallest standard type that holds it.
    """
    cn = _dt_name(dtype)
    if cn == _DT_INT:
        from .lower_progseq import cpp_type
        return cpp_type(dtype)
    if cn == _DT_BOOL:
        return "bool"
    if cn == _DT_ENUM:
        return cpp_enum_name(dtype)
    if cn == _DT_STRUCT:
        if _strip_pkg(dtype.name) == "addr_handle_t":
            return "pssc::addr_t"
        return c_struct_name(dtype)
    if cn == "DataTypeChandle":
        return "pssc::addr_t"
    raise ValueError(f"unsupported C++ struct member type {cn}")


def emit_struct(struct_dtype) -> str:
    """A plain struct, in DECLARATION order, with members value-initialised.

    `= {}` on every member rather than a constructor: a generated aggregate
    stays an aggregate, so a caller can still write `wb_dma_ch_caps_s c{true,
    false};`, and a default-constructed one is zeroed rather than holding
    whatever was on the stack. The C backend cannot say this in the type and
    has to zero at each declaration site instead.
    """
    name = c_struct_name(struct_dtype)
    lines = [f"struct {name} {{"]
    for f in struct_dtype.fields:
        lines.append(f"    {cpp_member_type(f.datatype)} {f.name} = {{}};")
    lines.append("};")
    return "\n".join(lines)


def lower_api_types(components, reg_value_structs=(),
                    ctor_names=None) -> str:
    """Header text for the enums and structs the API mentions."""
    enums, structs = collect_api_types(components, reg_value_structs,
                                       ctor_names)
    if not enums and not structs:
        return ""
    parts: List[str] = ["// ----- Data types used by the export API. -----"]
    for e in enums:
        parts.append(emit_enum(e))
        parts.append("")
    for s in structs:
        parts.append(emit_struct(s))
        parts.append("")
    return "\n".join(parts).rstrip()
