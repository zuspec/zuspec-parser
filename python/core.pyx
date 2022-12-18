
cimport zuspec_parser.zsp_ast as ast
cimport ciostream

cdef class Factory(object):
    def __init__(self):
        self._hndl = NULL
        pass

    cpdef AstBuilder mkAstBuilder(self, MarkerListener marker_l):
        return AstBuilder.mk(self._hndl.mkAstBuilder(marker_l._hndl))
        pass

    @staticmethod
    cdef Factory inst():
        global _factoryInst
        if _factoryInst is None:
            print("TODO: must create factory")
            pass
        pass

    @staticmethod
    def inst():
        global _factoryInst
        if _factoryInst is None:
            print("TODO: must create factory")
            _factoryInst = Factory()
            pass
        print("static")

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