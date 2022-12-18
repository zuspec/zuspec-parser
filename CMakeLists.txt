cmake_minimum_required (VERSION 3.11)

project(zuspec-parser)

include(ExternalProject)

if (NOT PACKAGES_DIR)
  set(PACKAGES_DIR ${CMAKE_SOURCE_DIR}/packages)

  enable_testing()
  add_subdirectory(tests)
endif()

message("PSSParser: PACKAGES_DIR=${PACKAGES_DIR}")


list(APPEND CMAKE_MODULE_PATH ${PACKAGES_DIR}/antlr4-cpp-runtime/cmake)

# Some include	
include_directories(${CMAKE_BINARY_DIR}/zsp_ast/src/include)

link_directories(
	${CMAKE_BINARY_DIR}/antlr4/lib
	${CMAKE_BINARY_DIR}/zsp_ast/lib
	)

set(ANTLR_EXECUTABLE ${PACKAGES_DIR}/antlr4-tools.jar)
set(ANTLR4_JAR_LOCATION ${PACKAGES_DIR}/antlr4-tools.jar)

if (WIN32)
  set(PYTHON ${PACKAGES_DIR}/python/Scripts/python.exe)
else()
  set(PYTHON ${PACKAGES_DIR}/python/bin/python)
endif()

find_package(ANTLR REQUIRED)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

if (CMAKE_CXX_COMPILER_ID STREQUAL "GNU")
  set(ANTLR_CXXFLAGS "-Wno-attributes -fPIC")
else()
  set(ANTLR_CXXFLAGS -DANTLR4CPP_STATIC)
endif()

set(CompilerFlags
        CMAKE_CXX_FLAGS
        CMAKE_CXX_FLAGS_DEBUG
        CMAKE_CXX_FLAGS_RELEASE
        CMAKE_C_FLAGS
        CMAKE_C_FLAGS_DEBUG
        CMAKE_C_FLAGS_RELEASE
        "-fPIC"
        )
foreach(CompilerFlag ${CompilerFlags})
  string(REPLACE "/MD" "/MT" ${CompilerFlag} "${${CompilerFlag}}")
  string(REPLACE "/MDd" "/MTd" ${CompilerFlag} "${${CompilerFlag}}")
endforeach()

ExternalProject_Add(libantlr4
    PREFIX antlr4
    SOURCE_DIR "${PACKAGES_DIR}/antlr4-cpp-runtime"
    CMAKE_CACHE_ARGS
      -DCMAKE_INSTALL_PREFIX:PATH=${CMAKE_BINARY_DIR}/antlr4
      -DCMAKE_CXX_FLAGS:STRING=${ANTLR_CXXFLAGS}
      -DCMAKE_BUILD_TYPE:STRING=${CMAKE_BUILD_TYPE}
      -DBUILD_SHARED_LIBS:BOOL=${BUILD_SHARED_LIBS}
    )
    
ExternalProject_Add(AST
	PREFIX zsp_ast
	SOURCE_DIR "${CMAKE_CURRENT_BINARY_DIR}/zsp_ast/src"
	DOWNLOAD_COMMAND 
		${PYTHON} -m astbuilder gen-cpp -name zsp_ast -namespace zsp::ast -astdir ${CMAKE_CURRENT_SOURCE_DIR}/ast -license ${CMAKE_CURRENT_SOURCE_DIR}/etc/copyright.cpp &&
		${PYTHON} -m astbuilder gen-pyext -name zsp_ast -namespace zsp::ast -package zuspec_parser.zsp_ast -astdir ${CMAKE_CURRENT_SOURCE_DIR}/ast -o ../ext
        CMAKE_CACHE_ARGS
          -DCMAKE_INSTALL_PREFIX:PATH=${CMAKE_CURRENT_BINARY_DIR}/zsp_ast
          -DCMAKE_BUILD_TYPE:STRING=${CMAKE_BUILD_TYPE}
          -DBUILD_SHARED_LIBS:BOOL=${BUILD_SHARED_LIBS}
	)


add_subdirectory(src)

#if (NOT DEFINED ENV{EXT_PYTHON})
#   set(ENV{EXT_PYTHON} ${PYTHON})
#endif()

#add_custom_target(build_ext ALL
#	COMMAND ${CMAKE_COMMAND} -E copy ${CMAKE_BINARY_DIR}/pssast/ext/pssast_decl.pxd ${CMAKE_CURRENT_SOURCE_DIR}/python/pssparser/pssast_decl.pxd
#	COMMAND ${CMAKE_COMMAND} -E copy ${CMAKE_BINARY_DIR}/pssast/ext/pssast.pxd ${CMAKE_CURRENT_SOURCE_DIR}/python/pssparser/pssast.pxd
#	COMMAND ${CMAKE_COMMAND} -E copy ${CMAKE_BINARY_DIR}/pssast/ext/pssast.pyx ${CMAKE_CURRENT_SOURCE_DIR}/python/pssast.pyx
#	COMMAND ${CMAKE_COMMAND} -E copy ${CMAKE_BINARY_DIR}/pssast/ext/PyBaseVisitor.cpp ${CMAKE_CURRENT_SOURCE_DIR}/python/PyBaseVisitor.cpp
#	COMMAND ${CMAKE_COMMAND} -E copy ${CMAKE_BINARY_DIR}/pssast/ext/PyBaseVisitor.h ${CMAKE_CURRENT_SOURCE_DIR}/python/PyBaseVisitor.h
#	COMMAND ${CMAKE_COMMAND} -E env CMAKE_BINARY_DIR=${CMAKE_BINARY_DIR} $ENV{EXT_PYTHON} ${CMAKE_CURRENT_SOURCE_DIR}/setup.py build_ext --inplace
#	COMMAND $ENV{EXT_PYTHON} ${CMAKE_CURRENT_SOURCE_DIR}/setup.py bdist_wheel
#	)


