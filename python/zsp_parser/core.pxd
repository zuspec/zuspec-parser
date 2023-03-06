#****************************************************************************
#* zsp_parser core.pxd
#****************************************************************************
cimport decl
cimport debug_mgr.core as dm_core
cimport zsp_parser.ast as ast
cimport ciostream

cdef class Factory(object):
    cdef decl.IFactory      *_hndl

    cpdef AstBuilder mkAstBuilder(self, MarkerListener marker_l)

    cdef init(self, dm_core.Factory f, ast.Factory ast_f)

cdef Factory _factoryInst = None


cdef class AstBuilder(object):
    cdef decl.IAstBuilder      *_hndl

    cpdef build(self,
        ast.GlobalScope         root,
        ciostream.cistream      in_s)

    @staticmethod
    cdef AstBuilder mk(decl.IAstBuilder *hndl)


cdef class MarkerListener(object):
    cdef decl.IMarkerListener       *_hndl
