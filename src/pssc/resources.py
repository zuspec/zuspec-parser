"""Locating the runtime source a generated API depends on.

Generated code is not self-contained. The SV package needs `pssc_reg_pkg.sv`;
the C header needs the `pssc_mem*.h` seam; the C++ header needs
`pssc_reg.hpp`. pssc ships those under `pssc/share/<lang>/` and copies them
beside the generated file.

THE SEAM. A plugin's backend needs the same thing for *its* runtime source,
which lives in *its* distribution -- so the lookup takes a package name.
`core_dir("acme_pssc", "c")` resolves `acme_pssc/share/c/` by the same rule
pssc uses for its own, with no import of pssc internals and no assumption that
either package is an unzipped directory on disk.

Everything here goes through `importlib.resources`, which is the only lookup
that survives being installed as a zip or having the package relocated.
`__file__` arithmetic works right up until someone builds a single-file
distribution, and then fails in a way that reads as a missing file.
"""
from __future__ import annotations

from pathlib import Path
from typing import List

#: Subdirectory of a package holding its per-language runtime source.
SHARE = "share"


class ResourceError(Exception):
    """A package's runtime-source directory or file could not be located."""


def core_dir(package: str = "pssc", lang: str = "c") -> Path:
    """Directory of ``package``'s runtime source for ``lang``.

    ``lang`` is the subdirectory name -- ``sv``, ``c``, ``cpp`` for the
    built-ins, anything a plugin ships for itself.

    Raises :class:`ResourceError` naming the package and the expected location
    when it is absent. The alternative -- returning a path that does not exist
    -- defers the failure to a `shutil.copy2` several frames away, whose
    message names a file nobody wrote and does not mention the package that was
    supposed to provide it.
    """
    try:
        from importlib.resources import files
        root = files(package)
    except ModuleNotFoundError as e:
        raise ResourceError(
            f"cannot locate runtime source for '{lang}': package "
            f"'{package}' is not importable ({e})") from None
    except Exception as e:
        raise ResourceError(
            f"cannot locate runtime source for '{lang}' in '{package}': {e}"
        ) from None

    path = Path(str(root / SHARE / lang))
    if not path.is_dir():
        raise ResourceError(
            f"package '{package}' ships no runtime source for '{lang}': "
            f"expected {path}. A distribution that generates {lang} must "
            f"include {package}/{SHARE}/{lang}/ as package data")
    return path


def core_file(name: str, package: str = "pssc", lang: str = "c") -> Path:
    """One file from :func:`core_dir`, checked to exist.

    Checked here rather than at the copy, because a runtime header missing from
    a wheel is a packaging bug and its diagnostic should say so.
    """
    path = core_dir(package, lang) / name
    if not path.is_file():
        raise ResourceError(
            f"'{name}' is missing from {core_dir(package, lang)}. It is listed "
            f"as runtime source for '{lang}' but not shipped -- check "
            f"'{package}'s package-data configuration")
    return path


def core_files(names, package: str = "pssc", lang: str = "c") -> List[Path]:
    """:func:`core_file` over ``names``, order preserved."""
    return [core_file(n, package, lang) for n in names]
