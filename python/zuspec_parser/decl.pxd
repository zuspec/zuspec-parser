

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
cimport zsp_ast_decl as ast
cimport ciostream


cdef extern from "zsp/IFactory.h" namespace "zsp":
    cdef cppclass IFactory:
        IAstBuilder *mkAstBuilder()

cdef extern from "zsp/IAstBuilder.h" namespace "zsp":
    cdef cppclass IAstBuilder:

        void build(
            ast.IGlobalScope        *scope,
            ciostream.istream       *in_s,
            IMarkerListener         *marker_l)


cdef extern from "zsp/IMarker.h" namespace "zsp":
    cdef enum MarkerSeverityE:
        Error "zsp::MarkerSeverityE::Error"
        Warn "zsp::MarkerSeverityE::Warn"
        Info "zsp::MarkerSeverityE::Info"
        Hint "zsp::MarkerSeverityE::Hint"
        NumLevels "zsp::MarkerSeverityE::NumLevels"

    cdef cppclass Location:
        int32_t            file;
        int32_t            line;
        int32_t            pos;

    cdef cppclass IMarker:
        const cpp_string &msg() const
        MarkerSeverityE severity() const
        const Location &loc() const;
        IMarker *clone() const

cdef extern from "zsp/IMarkerListener.h" namespace "zsp":
    cdef cppclass IMarkerListener:
        void marker(const IMarker *m)
        bool hasSeverity(MarkerSeverityE s)
