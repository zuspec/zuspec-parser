/*
 * TestBase.cpp
 *
 * Copyright 2022 Matthew Ballance and Contributors
 *
 * Licensed under the Apache License, Version 2.0 (the "License"); you may 
 * not use this file except in compliance with the License.  
 * You may obtain a copy of the License at:
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software 
 * distributed under the License is distributed on an "AS IS" BASIS, 
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  
 * See the License for the specific language governing permissions and 
 * limitations under the License.
 *
 * Created on:
 *     Author:
 */
#include "TestBase.h"
#include <sstream>
#include "AstBuilder.h"
#include "AstSymbolTable.h"
#include "MarkerCollector.h"
#include "AstMerger.h"
#include "zsp_ast/src/GlobalScope.h"
#include "zsp_ast/src/Factory.h"
#include "zsp/IMarker.h"
#include "Factory.h"
#include "TaskBuildSymbolTree.h"


TestBase::TestBase() {

}

TestBase::~TestBase() {

}

void TestBase::runTest(
		const std::string &content,
		const std::string &name) {
	std::stringstream s(content);
    zsp::ast::Factory ast_factory;
	zsp::Factory zsp_factory(&ast_factory);

	zsp::ast::IGlobalScopeUP global(ast_factory.mkGlobalScope(0));

	zsp::MarkerCollector marker_c;
	zsp::IAstBuilderUP ast_builder(zsp_factory.mkAstBuilder(&marker_c));

	ast_builder->build(global.get(), &s);

	for (std::vector<zsp::IMarkerUP>::const_iterator
			it=marker_c.markers().begin();
			it!=marker_c.markers().end(); it++) {
		fprintf(stdout, "Marker: %s\n", (*it)->msg().c_str());
	}

	ASSERT_FALSE(marker_c.hasSeverity(zsp::MarkerSeverityE::Error));

	zsp::AstMerger merger(&ast_factory);
	zsp::ast::ISymbolScopeUP symtree(zsp::TaskBuildSymbolTree(
		&ast_factory,
		&marker_c).build({global.get()}));
//	zsp::ast::IGlobalScopeUP merged(merger.merge({global.get()}));

	zsp::ISymbolTableUP symtab(zsp_factory.mkSymbolTable());
	zsp::INameResolverUP name_resolver(zsp_factory.mkNameResolver(
		symtab.get(),
		&marker_c
	));

	name_resolver->resolve(
		symtree.get()
//		global.get()
	);
}

