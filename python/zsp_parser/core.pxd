#****************************************************************************
#* zsp_parser core.pxd
#****************************************************************************
cimport decl
cimport debug_mgr.core as dm_core
cimport zsp_parser.ast as ast
cimport ciostream
from libcpp cimport bool

cdef class Factory(object):
    cdef decl.IFactory      *_hndl

    cpdef ast.Factory getAstFactory(self)

    cpdef dm_core.DebugMgr getDebugMgr(self)

    cpdef void loadStandardLibrary(self,
        AstBuilder          ast_builder,
        ast.GlobalScope     glbl_scope)

    cpdef AstBuilder mkAstBuilder(self, MarkerListener marker_l)

    cpdef Linker mkAstLinker(self)

    cpdef SymbolTableIterator mkAstSymbolTableIterator(self,
        ast.SymbolScope     root)

    cpdef MarkerCollector mkMarkerCollector(self)

    cdef init(self, dm_core.Factory f, ast.Factory ast_f)

cdef Factory _factoryInst = None


cdef class AstBuilder(object):
    cdef decl.IAstBuilder      *_hndl

    cpdef build(self,
        ast.GlobalScope         root,
                                in_s)

    @staticmethod
    cdef AstBuilder mk(decl.IAstBuilder *hndl)

cdef class Linker(object):
    cdef decl.ILinker           *_hndl
    cdef bool                   _owned

    cpdef ast.SymbolScope link(self,
        MarkerListener         marker_l,
        scopes)

    @staticmethod
    cdef Linker mk(decl.ILinker *hndl, bool owned=*)


cdef class MarkerListener(object):
    cdef decl.IMarkerListener       *_hndl
    cdef bool                       _owned

    cpdef bool hasSeverity(self, s)

cdef class MarkerCollector(MarkerListener):

    @staticmethod
    cdef MarkerCollector mk(decl.IMarkerCollector *hndl, bool owned=*)

cdef class SymbolTableIterator(object):
    cdef decl.ISymbolTableIterator  *_hndl
    cdef bool                       _owned

    @staticmethod
    cdef SymbolTableIterator mk(decl.ISymbolTableIterator *hndl, bool owned=*)
