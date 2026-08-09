"""pssc front end: the single-pass ``Parser`` wrapper over ``pssparser``.

The source is parsed verbatim — no rewriting, no annotation side-channel. The
only front-end logic is a guard that rejects the non-LRM ``fill`` statement with
a clear diagnostic (:func:`_reject_fill`).

Split out of the package ``__init__`` so the driver/CLI can reach the parser
without importing the IR/runtime/SV layers.
"""
from typing import List
from pssparser import Parser as _PssParser, ParseException


# ---------------------------------------------------------------------------
# PSS source text-transformation helpers
# ---------------------------------------------------------------------------

def _is_word_char(c: str) -> bool:
    return c.isalnum() or c == '_'


def _scan_comment_or_string(text: str, i: int) -> int:
    """Return end index after a comment or string at i, or -1 if not at one."""
    n = len(text)
    if text[i:i+2] == '//':
        end = text.find('\n', i)
        return n if end == -1 else end + 1
    if text[i:i+2] == '/*':
        end = text.find('*/', i + 2)
        return n if end == -1 else end + 2
    if text[i] == '"':
        j = i + 1
        while j < n and text[j] != '"':
            if text[j] == '\\':
                j += 1
            j += 1
        return min(j + 1, n)
    return -1


def _reject_fill(text: str, filename: str) -> None:
    """Raise a clear diagnostic when the non-LRM ``fill { ... }`` activity
    statement appears in *text*.

    ``fill`` (and its companion ``FILL`` placeholder) is a Perspec-specific
    extension, not part of the PSS LRM. It is no longer rewritten/inferred;
    surface it explicitly instead of letting it become a cryptic parse error or
    silently dropping the enclosed constraints. ``fill`` remains valid as an
    ordinary identifier (e.g. an action named ``fill``); only the
    statement-position block form ``fill { ... }`` is rejected.
    """
    n = len(text)
    i = 0
    while i < n:
        end = _scan_comment_or_string(text, i)
        if end != -1:
            i = end
            continue
        if (text[i:i+4] == "fill"
                and (i == 0 or not _is_word_char(text[i - 1]))
                and (i + 4 < n and not _is_word_char(text[i + 4]))):
            # Followed by '{' (skipping whitespace)?
            j = i + 4
            while j < n and text[j] in " \t\r\n":
                j += 1
            # Preceded (skipping whitespace) by a statement boundary? This
            # distinguishes the `fill { ... }` statement from a declaration that
            # merely names a type/action `fill` (e.g. `action fill { ... }`).
            k = i - 1
            while k >= 0 and text[k] in " \t\r\n":
                k -= 1
            if j < n and text[j] == "{" and (k < 0 or text[k] in "{;}"):
                line = text.count("\n", 0, i) + 1
                raise ParseException(
                    "%s:%d: 'fill' is not supported (non-LRM Perspec extension). "
                    "Rewrite the activity using 'repeat'/'replicate' or a "
                    "coverage-driven loop." % (filename, line))
        i += 1



class Parser(_PssParser):
    """pssparser.Parser wrapper.

    The PSS source is parsed verbatim — there is no source rewriting and no
    annotation side-channel. ``forall``, ``covergroup``, component ``bind``, and
    the state ``initial`` / resource ``instance_id`` built-ins are handled
    natively by pssparser. The non-LRM ``fill`` statement is rejected with an
    explicit diagnostic (see :func:`_reject_fill`). ``exec file`` parses natively
    (it is grammar-valid) but is not lowered — its builder is a stub, so it is
    accepted and ignored.
    """

    def parse(self, files: List[str], prelude=()) -> bool:
        """Read and parse PSS ``files``, with ``prelude`` processed first.

        ``prelude`` is a sequence of ``(name, text)`` in-memory source units --
        typically a target's ``target_cfg_pkg`` (see
        :mod:`pssc.targets.target_cfg`). They are prepended rather than
        appended because ``compile if`` reads constants only from
        previously-processed source units (PSS 3.1 §19.1.2), and arriving late
        is silent: the model simply takes its default branch.
        """
        text_files = [(name, text) for name, text in prelude]
        for path in files:
            with open(path, 'r') as fh:
                src = fh.read()
            text_files.append((path, src))
        return self._guard_and_parse(text_files)

    def parses(self, text_files) -> bool:
        """Parse in-memory PSS texts."""
        return self._guard_and_parse(list(text_files))

    def _guard_and_parse(self, text_files: List[tuple]) -> bool:
        for fname, src in text_files:
            _reject_fill(src, fname)
        return super().parses(text_files)

