
import ctypes
from enum import IntEnum
import os
cimport debug_mgr.core as dm_core
cimport zsp_parser.ast as ast
cimport zsp_parser.ast_decl as ast_decl
cimport zsp_parser.decl as decl
from ciostream.core cimport cistream
from libc.stdint cimport intptr_t
from libcpp.vector cimport vector as std_vector
from libcpp.cast cimport dynamic_cast

cdef Factory _inst = None
cdef class Factory(object):
    def __init__(self):
        self._hndl = NULL
        pass

    cpdef ast.Factory getAstFactory(self):
        return ast.Factory.mk(self._hndl.getAstFactory())

    cpdef dm_core.DebugMgr getDebugMgr(self):
        return dm_core.DebugMgr.mk(self._hndl.getDebugMgr(), False)

    cpdef void loadStandardLibrary(self,
        AstBuilder          ast_builder,
        ast.GlobalScope     glbl_scope):
        self._hndl.loadStandardLibrary(
            ast_builder._hndl,
            glbl_scope.asGlobalScope())

    cpdef AstBuilder mkAstBuilder(self, MarkerListener marker_l):
        return AstBuilder.mk(self._hndl.mkAstBuilder(marker_l._hndl))

    cpdef Linker mkAstLinker(self):
        return Linker.mk(self._hndl.mkAstLinker(), True)

    cpdef SymbolTableIterator mkAstSymbolTableIterator(self,
        ast.SymbolScope     root):
        return SymbolTableIterator.mk(self._hndl.mkAstSymbolTableIterator(root.asSymbolScope()))

    cpdef MarkerCollector mkMarkerCollector(self):
        return MarkerCollector.mk(self._hndl.mkMarkerCollector(), True)

    cdef init(self, dm_core.Factory f, ast.Factory ast_f):
        self._hndl.init(f._hndl.getDebugMgr(), ast_f._hndl)

    @staticmethod
    def inst():
        cdef Factory factory
        global _inst
        if _inst is None:
            ext_dir = os.path.dirname(os.path.abspath(__file__))
            build_dir = os.path.abspath(os.path.join(ext_dir, "../../build"))

            libname = "libzsp-parser.so"
            core_lib = None

            for libdir in ("lib", "lib64"):
                if os.path.isfile(os.path.join(build_dir, libdir, libname)):
                    core_lib = os.path.join(build_dir, libdir, libname)
                    break

            if core_lib is None:
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
                                in_s):
        cdef cistream c_in_s
        
        c_in_s = cistream(in_s)

        self._hndl.build(
            root.asGlobalScope(),
            c_in_s.stream())

    @staticmethod
    cdef AstBuilder mk(decl.IAstBuilder *hndl):
        ret = AstBuilder()
        ret._hndl = hndl
        return ret

cdef class Linker(object):
    def __dealloc__(self):
        if self._owned:
            del self._hndl

    cpdef ast.SymbolScope link(self,
        MarkerListener          marker_l,
        scopes):
        cdef std_vector[ast_decl.IGlobalScopeP] scopes_n
        cdef ast_decl.ISymbolScope *ret_h

        for s in scopes:
            scope = <ast.GlobalScope>(s)
            scopes_n.push_back(scope.asGlobalScope())

        ret_h = self._hndl.link(marker_l._hndl, scopes_n)

        if ret_h == NULL:
            return None
        else:
            return ast.SymbolScope.mk(ret_h, True)

    @staticmethod
    cdef Linker mk(decl.ILinker *hndl, bool owned=True):
        ret = Linker()
        ret._hndl = hndl
        ret._owned = owned
        return ret

class MarkerSeverityE(IntEnum):
    Error = decl.MarkerSeverityE.Severity_Error
    Warn = decl.MarkerSeverityE.Severity_Warn
    Info = decl.MarkerSeverityE.Severity_Info
    Hint = decl.MarkerSeverityE.Severity_Hint
    NumLevels = decl.MarkerSeverityE.Severity_NumLevels

cdef class Location(object):

    def __init__(self, file, line, pos):
        self._file = file
        self._line = line
        self._pos = pos

    @property
    def file(self):
        return self._file

cdef class Marker(object):

    def __dealloc__(self):
        if self._owned:
            del self._hndl
    
    cpdef str msg(self):
        return self._hndl.msg().decode()

    cpdef Location loc(self):
        cdef const ast_decl.Location *lp = &self._hndl.loc()
        return Location(lp.fileid, lp.lineno, lp.linepos)

    @staticmethod
    cdef Marker mk(decl.IMarker *hndl, bool owned=True):
        ret = Marker()
        ret._hndl = hndl
        ret._owned = owned
        return ret

cdef class MarkerListener(object):
    def __dealloc__(self):
        if self._owned:
            del self._hndl

    cpdef bool hasSeverity(self, s):
        cdef int s_i = int(s)
        return self._hndl.hasSeverity(<decl.MarkerSeverityE>(s_i))
    pass

cdef class MarkerCollector(MarkerListener):

    cpdef markers(self):
        ret = []
        for i in range(self.asCollector().markers().size()):
            ret.append(Marker.mk(
                self.asCollector().markers().at(i).get(),
                False
            ))
        return ret

    cdef decl.IMarkerCollector *asCollector(self):
        return dynamic_cast[decl.IMarkerCollectorP](self._hndl)

    @staticmethod
    cdef MarkerCollector mk(decl.IMarkerCollector *hndl, bool owned=True):
        ret = MarkerCollector()
        ret._hndl = hndl
        ret._owned = owned
        return ret

cdef class SymbolTableIterator(object):

    def __dealloc__(self):
        if self._owned:
            del self._hndl

    @staticmethod
    cdef SymbolTableIterator mk(decl.ISymbolTableIterator *hndl, bool owned=True):
        ret = SymbolTableIterator()
        ret._hndl = hndl
        ret._owned = owned
        return ret
