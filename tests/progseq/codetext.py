"""Reading generated code without reading its comments.

The op-model targets now carry the PSS source's prose into their output, and
this model's prose *discusses the code it sits next to*: `transfer_list_start`
explains in a comment why it does not call `write_fields`, and the C target's
`wait_hint` explains what `notify_irq()` would have done on a profile that has
it. A structural assertion that greps the raw text for a call therefore finds
the sentence saying the call is absent, and an ``in``/``not in`` pair over
generated text stops meaning what it says.

Assertions about what the code *does* have to look at the code. Assertions
about the prose -- see test_comment_propagation.py -- look at the raw text.

A module rather than a conftest fixture: several test modules need it as a
plain function at import time, and these tests are packages, so a bare
``conftest`` import resolves to the wrong file.
"""
import re

#: A `/* ... */` block, including one spanning lines.
_BLOCK = re.compile(r"/\*.*?\*/", re.DOTALL)

#: A `//` comment running to end of line.
_LINE = re.compile(r"//[^\n]*")


def code_only(text: str) -> str:
    """*text* with its comments removed and its line structure preserved.

    Comments become blank rather than disappearing, so a line number in a
    failure message still points at the right line of the original.
    """
    text = _BLOCK.sub(lambda m: "\n" * m.group(0).count("\n"), text)
    return _LINE.sub("", text)
