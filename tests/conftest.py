"""Root conftest for pssc tests.

Stubs pssparser if the native library is not available so that
pure-Python tests (e.g. SV lowering) can still run.
"""
import os
import sys
import types

# pssc's c-host target uses dv-solve directly (pssc.targets.sw_solve). Making
# dv-solve importable for that also makes zuspec-dataclasses prefer its native
# (dv-solve) randomization backend, which is currently incomplete for several
# constraint kinds. The Python-path integration tests have always exercised the
# pure-Python backend, so pin it here to keep their behavior unchanged.
os.environ.setdefault("ZSP_SOLVER_BACKEND", "python")

if "pssparser" not in sys.modules:
    try:
        import pssparser  # noqa: F401
    except (ImportError, ModuleNotFoundError):
        _stub = types.ModuleType("pssparser")
        _stub.Parser = None
        _stub.ParseException = Exception
        sys.modules["pssparser"] = _stub

        _ast = types.ModuleType("pssparser.ast")
        sys.modules["pssparser.ast"] = _ast

        _core = types.ModuleType("pssparser.core")

        class _FakeFactory:
            @staticmethod
            def inst():
                return _FakeFactory()
            def getDebugMgr(self):
                class _Dbg:
                    def enable(self, v): pass
                return _Dbg()

        _core.Factory = _FakeFactory
        sys.modules["pssparser.core"] = _core
