"""DFM extension hook: maps the ``pssc`` package name to its ``flow.yaml``.

Discovered by ``dv-flow-mgr`` through the ``dv_flow.mgr`` entry point declared
in ``pyproject.toml``. Intentionally dependency-free (no ``dv_flow.mgr`` import)
so package discovery is cheap and never fails on a core-only install.
"""
import os


def dvfm_packages():
    here = os.path.dirname(os.path.abspath(__file__))
    return {"pssc": os.path.join(here, "flow.yaml")}
