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
#include "dmgr/FactoryExt.h"
#include "zsp_ast/src/GlobalScope.h"
#include "zsp_ast/src/Factory.h"
#include "zsp/parser/IMarker.h"
#include "zsp/parser/FactoryExt.h"
#include "Factory.h"
#include "TaskBuildSymbolTree.h"

namespace zsp {
namespace parser {



TestBase::TestBase() {

}

TestBase::~TestBase() {

}

extern "C" ast::IFactory *ast_getFactory();

void TestBase::SetUp() {
    dmgr::IDebugMgr *dmgr = dmgr_getFactory()->getDebugMgr();
    m_ast_factory = ast_getFactory();
	m_factory = zsp_parser_getFactory();
    m_factory->init(dmgr, m_ast_factory);
    m_factory->getDebugMgr()->enable(false);
}

void TestBase::TearDown() {

}

void TestBase::runTest(
		const std::string   &content,
		const std::string   &name,
        bool                load_stdlib) {
	std::stringstream s(content);

	ast::IGlobalScopeUP global(m_ast_factory->mkGlobalScope(0));

	MarkerCollector marker_c;
	IAstBuilderUP ast_builder(m_factory->mkAstBuilder(&marker_c));

    if (load_stdlib) {
        m_factory->loadStandardLibrary(ast_builder.get(), global.get());
    }

	ast_builder->build(global.get(), &s);

	for (std::vector<IMarkerUP>::const_iterator
			it=marker_c.markers().begin();
			it!=marker_c.markers().end(); it++) {
		fprintf(stdout, "Parse Error: %s\n", (*it)->msg().c_str());
	}

	ASSERT_FALSE(marker_c.hasSeverity(parser::MarkerSeverityE::Error));

	ILinkerUP linker(m_factory->mkAstLinker());

	ast::ISymbolScopeUP root(linker->link(
		&marker_c,
		{global.get()}
	));

	for (std::vector<IMarkerUP>::const_iterator
			it=marker_c.markers().begin();
			it!=marker_c.markers().end(); it++) {
		fprintf(stdout, "Link Error: %s\n", (*it)->msg().c_str());
	}

	ASSERT_FALSE(marker_c.hasSeverity(MarkerSeverityE::Error));
}

ast::IGlobalScope *TestBase::parse(
		IMarkerListener		        *marker_l,
		const std::string 			&content,
		const std::string 			&name,
        bool                        process_doc_comments) {
	std::stringstream s(content);

	ast::IGlobalScopeUP global(m_ast_factory->mkGlobalScope(0));

	IAstBuilderUP ast_builder(m_factory->mkAstBuilder(marker_l));
    ast_builder->setCollectDocStrings(process_doc_comments);

	ast_builder->build(global.get(), &s);

	return global.release();
}

ast::ISymbolScope *TestBase::link(
		IMarkerListener					        *marker_l,
		const std::vector<ast::IGlobalScopeUP>	&files) {
	std::vector<ast::IGlobalScope *> files_p;

	for (std::vector<ast::IGlobalScopeUP>::const_iterator
		it=files.begin();
		it!=files.end(); it++) {
		files_p.push_back(it->get());
	}

	ILinkerUP linker(m_factory->mkAstLinker());
	ast::ISymbolScopeUP root(linker->link(
		marker_l,
		files_p
	));

	return root.release();
}

ast::ISymbolScope *TestBase::link(
		IMarkerListener						        *marker_l,
		const std::vector<ast::IGlobalScope *>	&files) {
	ILinkerUP linker(m_factory->mkAstLinker());
	ast::ISymbolScopeUP root(linker->link(
		marker_l,
		files
	));

	return root.release();
}

void TestBase::parseLink(
        IMarkerListener             *marker_l,
        const std::string           &content,
        const std::string           &name,
        ast::IGlobalScopeUP         &global,
        ast::ISymbolScopeUP         &root) {
    global = ast::IGlobalScopeUP(parse(marker_l, content, name));
    root = ast::ISymbolScopeUP(link(marker_l, {global.get()}));
}

std::pair<ast::IGlobalScope *, ast::ISymbolScope *> TestBase::parseLink(
        parser::IMarkerListener        *marker_l,
        const std::string              &content,
        const std::string              &name,
        bool                           process_doc_comments) {
    ast::IGlobalScope *global = parse(marker_l, content, name, process_doc_comments); 
    ast::ISymbolScope *root = 0;
    if (!marker_l->hasSeverity(MarkerSeverityE::Error)) {
        root = link(marker_l, {global});
    }

    return {global, root};
}

ast::IScopeChild *TestBase::findItem(
        ast::ISymbolScope                   *root,
        const std::vector<std::string>      &path) {
    ast::IScopeChild *ret = 0;
    ast::ISymbolScope *scope = root;

    for (std::vector<std::string>::const_iterator
        it=path.begin();
        it!=path.end(); it++) {
        std::map<std::string,int32_t>::const_iterator s_it =
            scope->getSymtab().find(*it);
        if (s_it != scope->getSymtab().end()) {
            if (it+1 != path.end()) {
                scope = dynamic_cast<ast::ISymbolScope *>(
                    scope->getChildren().at(s_it->second));
            } else {
                ret = dynamic_cast<ast::ISymbolScope *>(
                    scope->getChildren().at(s_it->second));
            }
        } else {
            break;
        }
    }

    return ret;
}

void TestBase::enableDebug(bool en) {
    m_factory->getDebugMgr()->enable(en);
}

}
}
