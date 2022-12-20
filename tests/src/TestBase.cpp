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

void TestBase::SetUp() {
    m_ast_factory = zsp::ast::IFactoryUP(new zsp::ast::Factory());
	m_factory = zsp::IFactoryUP(new zsp::Factory(m_ast_factory.get()));

}

void TestBase::TearDown() {

}

void TestBase::runTest(
		const std::string &content,
		const std::string &name) {
	std::stringstream s(content);

	zsp::ast::IGlobalScopeUP global(m_ast_factory->mkGlobalScope(0));

	zsp::MarkerCollector marker_c;
	zsp::IAstBuilderUP ast_builder(m_factory->mkAstBuilder(&marker_c));

	ast_builder->build(global.get(), &s);

	for (std::vector<zsp::IMarkerUP>::const_iterator
			it=marker_c.markers().begin();
			it!=marker_c.markers().end(); it++) {
		fprintf(stdout, "Marker: %s\n", (*it)->msg().c_str());
	}

	ASSERT_FALSE(marker_c.hasSeverity(zsp::MarkerSeverityE::Error));

	zsp::ILinkerUP linker(m_factory->mkAstLinker());

	zsp::ast::ISymbolScopeUP root(linker->link(
		&marker_c,
		{global.get()}
	));

	ASSERT_FALSE(marker_c.hasSeverity(zsp::MarkerSeverityE::Error));
}

zsp::ast::IGlobalScope *TestBase::parse(
		zsp::IMarkerListener		*marker_l,
		const std::string 			&content,
		const std::string 			&name) {
	std::stringstream s(content);

	zsp::ast::IGlobalScopeUP global(m_ast_factory->mkGlobalScope(0));

	zsp::IAstBuilderUP ast_builder(m_factory->mkAstBuilder(marker_l));

	ast_builder->build(global.get(), &s);

	return global.release();
}

zsp::ast::ISymbolScope *TestBase::link(
		zsp::IMarkerListener						*marker_l,
		const std::vector<zsp::ast::IGlobalScopeUP>	&files) {
	std::vector<zsp::ast::IGlobalScope *> files_p;

	for (std::vector<zsp::ast::IGlobalScopeUP>::const_iterator
		it=files.begin();
		it!=files.end(); it++) {
		files_p.push_back(it->get());
	}

	zsp::ILinkerUP linker(m_factory->mkAstLinker());
	zsp::ast::ISymbolScopeUP root(linker->link(
		marker_l,
		files_p
	));

	return root.release();
}

