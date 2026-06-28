"""`exec file` parses natively and is ignored (detox C2).

The ``exec file "name" = <triple-quoted-template>;`` form is grammar-valid in
pssparser (``target_file_exec_block``), but its AST builder is a stub, so no
node is produced and the directive is not lowered. The old
``_strip_exec_file_blocks`` source rewrite (which deleted it before parsing) is
gone; the construct now flows through ``parse -> link -> translate`` untouched
and is simply ignored.
"""
from __future__ import annotations
import os
import tempfile
import pytest

from pssc import Parser, AstToIrTranslator

pytestmark = pytest.mark.filterwarnings("ignore::UserWarning")

_TQ = '"""'

EXEC_FILE_PSS = """\
component pss_top {
    action A {
        rand bit[8] x;
        exec file "out.txt" = %sgenerated %s;
    }
}
""" % (_TQ, _TQ)


def _translate(src: str):
    with tempfile.NamedTemporaryFile(suffix='.pss', mode='w', delete=False) as f:
        f.write(src)
        fname = f.name
    try:
        p = Parser()
        p.parse([fname])
        root = p.link()
        return AstToIrTranslator().translate(root)
    finally:
        try:
            os.unlink(fname)
        except OSError:
            pass


def test_exec_file_parses_and_translates_cleanly():
    """No parse/link/translate error; the action still reaches the IR."""
    ctx = _translate(EXEC_FILE_PSS)
    assert not ctx.errors
    action = ctx.type_map.get("pss_top::A") or ctx.type_map.get("A")
    assert action is not None
    # `x` is a real field; `exec file` contributes nothing (builder stub).
    assert "x" in [f.name for f in action.fields]
