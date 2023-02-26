
import ctypes
import os
cimport debug_mgr.core as dm_core
cimport zsp_parser.ast as ast
cimport ciostream
from libc.stdint cimport intptr_t

cdef Factory _inst = None
cdef class Factory(object):
    def __init__(self):
        self._hndl = NULL
        pass

    cpdef AstBuilder mkAstBuilder(self, MarkerListener marker_l):
        return AstBuilder.mk(self._hndl.mkAstBuilder(marker_l._hndl))
        pass

    cdef init(self, dm_core.Factory f, ast.Factory ast_f):
        self._hndl.init(f._hndl.getDebugMgr(), ast_f._hndl)

    @staticmethod
    def inst():
        cdef Factory factory
        global _inst
        if _inst is None:
            ext_dir = os.path.dirname(os.path.abspath(__file__))
            core_lib = os.path.join(ext_dir, "libzsp-parser.so")
            if not os.path.isfile(core_lib):
                raise Exception("Extension library core \"%s\" doesn't exist" % core_lib)

            so = ctypes.cdll.LoadLibrary(core_lib)
            func = so.zsp_parser_getFactory
            func.restype = ctypes.c_void_p

            hndl = <decl.IFactoryP>(<intptr_t>(func()))
            factory = Factory()
            factory._hndl = hndl
            factory.init(
                dm_core.Factory.inst(),
                ast.Factory.inst())
            _inst = factory

        return _inst

cdef class AstBuilder(object):

    def __dealloc__(self):
        del self._hndl

    cpdef build(self,
        ast.GlobalScope         root,
        ciostream.cistream      in_s):
        self._hndl.build(
            root.asGlobalScope(),
            in_s.stream())

    @staticmethod
    cdef AstBuilder mk(decl.IAstBuilder *hndl):
        ret = AstBuilder()
        ret._hndl = hndl
        return ret

cdef class MarkerListener(object):
    pass