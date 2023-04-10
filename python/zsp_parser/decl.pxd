

cimport debug_mgr.decl as dm
from libcpp.pair cimport pair as cpp_pair
from libcpp.set cimport set as cpp_set
from libcpp.string cimport string as cpp_string
from libcpp.vector cimport vector as cpp_vector
from libcpp.memory cimport unique_ptr
from libc.stdint cimport intptr_t
from libc.stdint cimport int32_t
from libc.stdint cimport uint32_t
from libc.stdint cimport uint64_t
from libc.stdint cimport int64_t
from libcpp cimport bool
cimport cpython.ref as cpy_ref
from zsp_parser cimport ast_decl as ast
cimport ciostream

ctypedef IFactory *IFactoryP


cdef extern from "zsp/parser/IFactory.h" namespace "zsp::parser":
    cdef cppclass IFactory:

        void init(dm.IDebugMgr *dmgr, ast.IFactory *ast_factory)

        ast.IFactory *getAstFactory()

        dm.IDebugMgr *getDebugMgr()

        void loadStandardLibrary(
            IAstBuilder             *ast_builder,
            ast.IGlobalScope        *glbl_scope)

        IAstBuilder *mkAstBuilder(IMarkerListener *)

        ILinker *mkAstLinker()

        ISymbolTableIterator *mkAstSymbolTableIterator(
            ast.ISymbolScope        *root)

        IMarkerCollector *mkMarkerCollector()


cdef extern from "zsp/parser/IAstBuilder.h" namespace "zsp::parser":
    cdef cppclass IAstBuilder:

        void build(
            ast.IGlobalScope        *scope,
            ciostream.istream       *in_s)

cdef extern from "zsp/parser/ILinker.h" namespace "zsp::parser":
    cdef cppclass ILinker:

        ast.ISymbolScope *link(
            IMarkerListener         *marker_l,
            const cpp_vector[ast.IGlobalScopeP] &scopes)

        pass

cdef extern from "zsp/parser/IMarker.h" namespace "zsp::parser":
    cdef enum MarkerSeverityE:
        Severity_Error "zsp::parser::MarkerSeverityE::Error"
        Severity_Warn "zsp::parser::MarkerSeverityE::Warn"
        Severity_Info "zsp::parser::MarkerSeverityE::Info"
        Severity_Hint "zsp::parser::MarkerSeverityE::Hint"
        Severity_NumLevels "zsp::parser::MarkerSeverityE::NumLevels"

    cdef cppclass Location:
        int32_t            file;
        int32_t            line;
        int32_t            pos;

    cdef cppclass IMarker:
        const cpp_string &msg() const
        MarkerSeverityE severity() const
        const Location &loc() const;
        IMarker *clone() const

cdef extern from "zsp/parser/IMarkerListener.h" namespace "zsp::parser":
    cdef cppclass IMarkerListener:
        void marker(const IMarker *m)
        bool hasSeverity(MarkerSeverityE s)

cdef extern from "zsp/parser/IMarkerCollector.h" namespace "zsp::parser":
    cdef cppclass IMarkerCollector(IMarkerListener):
        pass

cdef extern from "zsp/parser/ISymbolTableIterator.h" namespace "zsp::parser":
    cdef cppclass ISymbolTableIterator:
        int32_t findLocalSymbol(const cpp_string &name)


