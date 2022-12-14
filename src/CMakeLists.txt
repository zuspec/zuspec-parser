#****************************************************************************
#* CMakeLists.txt
#****************************************************************************
cmake_minimum_required (VERSION 2.8)

include(ExternalAntlr4Cpp)

if (CMAKE_CXX_COMPILER_ID STREQUAL "GNU")
  add_compile_options(-Wno-attributes)
  add_compile_options(-fPIC)
else()
  add_compile_options(-DANTLR4CPP_STATIC)
endif()

include_directories(
    ${CMAKE_BINARY_DIR}/antlr4/include/antlr4-runtime
    ${PACKAGES_DIR}/antlr4-cpp-runtime/runtime/src
    ${CMAKE_CURRENT_BINARY_DIR}/antlr4cpp_generated_src/PSSLexer
    ${CMAKE_CURRENT_BINARY_DIR}/antlr4cpp_generated_src/PSSParser
    ${CMAKE_BINARY_DIR}/zsp_ast/src/include
    ${CMAKE_CURRENT_SOURCE_DIR}
    ${CMAKE_CURRENT_SOURCE_DIR}/include
    ${DEBUG_MGR_DIR}/src/include
    )

link_directories(
	${CMAKE_BINARY_DIR}/antlr4/lib
	${CMAKE_BINARY_DIR}/antlr4/lib64
	)

antlr_target(PSSLexer PSSLexer.g4 LEXER)
antlr_target(PSSParser PSSParser.g4 PARSER 
             DEPENDS_ANTLR PSSLexer
             COMPILE_FLAGS -lib ${ANTLR_PSSLexer_OUTPUT_DIR}
             VISITOR LISTENER)

#********************************************************************
#* zsp
#********************************************************************
file(GLOB zsp_SRC
	"*.h"
	"*.cpp")
add_library(zuspec-parser SHARED
	${zsp_SRC}
	${ANTLR_PSSParser_OUTPUTS}
	${ANTLR_PSSLexer_OUTPUTS})

install(TARGETS zuspec-parser
    DESTINATION lib
    EXPORT zsp-targets)
    
add_dependencies(zuspec-parser AST libantlr4)

if (WIN32)
	if (BUILD_SHARED_LIBS)
		list(APPEND ZUSPEC_PARSER_LIBS antlr4-runtime)
	else()
		list(APPEND ZUSPEC_PARSER_LIBS antlr4-runtime-static)
	endif()
else()
	list(APPEND ZUSPEC_PARSER_LIBS antlr4-runtime pthread)
endif()

target_link_libraries(zuspec-parser ${ZUSPEC_PARSER_LIBS})
set_target_properties(zuspec-parser PROPERTIES SKIP_BUILD_RPATH TRUE)

add_library(zuspec-parser_static STATIC
	${zsp_SRC}
	${ANTLR_PSSParser_OUTPUTS}
	${ANTLR_PSSLexer_OUTPUTS})

add_dependencies(zuspec-parser_static AST libantlr4)
	

