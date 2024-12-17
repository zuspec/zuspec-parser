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
#include "dmgr/impl/DebugMacros.h"
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

    m_dbg = 0;
    char tmp[1024];
    snprintf(tmp, sizeof(tmp), "zsp::parser::Test::%s",
        ::testing::UnitTest::GetInstance()->current_test_info()->name());
    DEBUG_INIT(tmp, m_factory->getDebugMgr());
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
//    ast_builder->setEnableProfile(true);

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
		MarkerCollector		        *marker_l,
		const std::string 			&content,
		const std::string 			&name,
        int32_t                     fileid,
        bool                        process_doc_comments) {
	std::stringstream s(content);
    return parse(marker_l, &s, name, fileid, process_doc_comments);
}

ast::IGlobalScope *TestBase::parse(
		MarkerCollector		        *marker_l,
        std::istream                *content,
		const std::string 			&name,
        int32_t                     fileid,
        bool                        process_doc_comments) {
	ast::IGlobalScopeUP global(m_ast_factory->mkGlobalScope(fileid));

	IAstBuilderUP ast_builder(m_factory->mkAstBuilder(marker_l));
    ast_builder->setCollectDocStrings(process_doc_comments);

	ast_builder->build(global.get(), content);

	return global.release();
}

ast::ISymbolScope *TestBase::link(
		IMarkerListener					        *marker_l,
		std::vector<ast::IGlobalScopeUP>	&files) {
	std::vector<ast::IGlobalScope *> files_p;

	for (std::vector<ast::IGlobalScopeUP>::iterator
		it=files.begin();
		it!=files.end(); it++) {
		files_p.push_back(it->release());
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
        IMarkerCollector            *marker_l,
        const std::string           &content,
        const std::string           &name,
        ast::IGlobalScopeUP         &global,
        ast::ISymbolScopeUP         &root,
        int32_t                     fileid) {
	std::stringstream s(content);
    std::vector<ast::IGlobalScopeUP> files;
    parseLink(marker_l, &s, name, files, root, fileid, false);
    global = std::move(files.back());
}

void TestBase::parseLink(
        IMarkerCollector                    *marker_c,
        std::istream                        *content,
        const std::string                   &name,
        std::vector<ast::IGlobalScopeUP>    &global,
        ast::ISymbolScopeUP                 &root,
        int32_t                             fileid,
        bool                                load_stdlib,
        bool                                process_doc_comments) {
    std::vector<ast::IGlobalScope *> files_p;
	IAstBuilderUP ast_builder(m_factory->mkAstBuilder(marker_c));

    if (load_stdlib) {
	    ast::IGlobalScope *stdlib = m_ast_factory->mkGlobalScope(global.size());
        m_factory->loadStandardLibrary(ast_builder.get(), stdlib);
        global.push_back(ast::IGlobalScopeUP(stdlib));
        files_p.push_back(stdlib);
    }

    ast_builder->setCollectDocStrings(process_doc_comments);

    ast::IGlobalScope *file = m_ast_factory->mkGlobalScope(global.size());
	ast_builder->build(file, content);

    global.push_back(ast::IGlobalScopeUP(file));
    files_p.push_back(file);

	for (std::vector<IMarkerUP>::const_iterator
			it=marker_c->markers().begin();
			it!=marker_c->markers().end(); it++) {
		fprintf(stdout, "Parse Error: %s\n", (*it)->msg().c_str());
	}

	ASSERT_FALSE(marker_c->hasSeverity(parser::MarkerSeverityE::Error));
	if (marker_c->hasSeverity(parser::MarkerSeverityE::Error)) {
        return;
    }

	ILinkerUP linker(m_factory->mkAstLinker());

	root = ast::ISymbolScopeUP(linker->link(
		marker_c,
        files_p
	));

	for (std::vector<IMarkerUP>::const_iterator
			it=marker_c->markers().begin();
			it!=marker_c->markers().end(); it++) {
		fprintf(stdout, "Link Error: %s\n", (*it)->msg().c_str());
	}

	ASSERT_FALSE(marker_c->hasSeverity(MarkerSeverityE::Error));
	if (marker_c->hasSeverity(parser::MarkerSeverityE::Error)) {
        return;
    }
}

std::pair<ast::IGlobalScope *, ast::ISymbolScope *> TestBase::parseLink(
        IMarkerCollector               *marker_l,
        const std::string              &content,
        const std::string              &name,
        bool                           process_doc_comments) {
	std::stringstream s(content);

    std::vector<ast::IGlobalScopeUP> global;
    ast::ISymbolScopeUP root;

    parseLink(marker_l, &s, name, global, root, 0, false, process_doc_comments);

    return {global.back().release(), root.release()};
}

void TestBase::parseLink(
        IMarkerCollector                    *marker_c,
        const std::string                   &content,
        const std::string                   &name,
        std::vector<ast::IGlobalScopeUP>    &files,
        ast::ISymbolScopeUP                 &root,
        bool                                load_stdlib) {
    std::vector<ast::IGlobalScope *> files_p;
	std::stringstream s(content);
	IAstBuilderUP ast_builder(m_factory->mkAstBuilder(marker_c));

    if (load_stdlib) {
	    ast::IGlobalScope *stdlib = m_ast_factory->mkGlobalScope(files.size());
        m_factory->loadStandardLibrary(ast_builder.get(), stdlib);
        files.push_back(ast::IGlobalScopeUP(stdlib));
        files_p.push_back(stdlib);
    }

    ast::IGlobalScope *file = m_ast_factory->mkGlobalScope(files.size());
	ast_builder->build(file, &s);

    files.push_back(ast::IGlobalScopeUP(file));
    files_p.push_back(file);

	for (std::vector<IMarkerUP>::const_iterator
			it=marker_c->markers().begin();
			it!=marker_c->markers().end(); it++) {
		fprintf(stdout, "Parse Error: %s\n", (*it)->msg().c_str());
	}

	ASSERT_FALSE(marker_c->hasSeverity(parser::MarkerSeverityE::Error));
	if (marker_c->hasSeverity(parser::MarkerSeverityE::Error)) {
        return;
    }

	ILinkerUP linker(m_factory->mkAstLinker());

	root = ast::ISymbolScopeUP(linker->link(
		marker_c,
        files_p
	));

	for (std::vector<IMarkerUP>::const_iterator
			it=marker_c->markers().begin();
			it!=marker_c->markers().end(); it++) {
		fprintf(stdout, "Link Error: %s\n", (*it)->msg().c_str());
	}

	ASSERT_FALSE(marker_c->hasSeverity(MarkerSeverityE::Error));
	if (marker_c->hasSeverity(parser::MarkerSeverityE::Error)) {
        return;
    }
}

ast::IScopeChild *TestBase::findItem(
        ast::ISymbolScope                   *root,
        const std::vector<std::string>      &path) {
    ast::IScopeChild *ret = 0;
    ast::ISymbolScope *scope = root;

    for (std::vector<std::string>::const_iterator
        it=path.begin();
        it!=path.end(); it++) {
        std::unordered_map<std::string,int32_t>::const_iterator s_it =
            scope->getSymtab().find(*it);
        if (s_it != scope->getSymtab().end()) {
            if (it+1 != path.end()) {
                scope = dynamic_cast<ast::ISymbolScope *>(
                    scope->getChildren().at(s_it->second).get());
            } else {
                ret = dynamic_cast<ast::ISymbolScope *>(
                    scope->getChildren().at(s_it->second).get());
            }
        } else {
            break;
        }
    }

    return ret;
}

bool TestBase::checkErrors(MarkerCollector &marker_c) {
    for (std::vector<IMarkerUP>::const_iterator
        it=marker_c.markers().begin();
        it!=marker_c.markers().end(); it++) {
        fprintf(stdout, "Parse Error: %s\n", (*it)->msg().c_str());
    }
    return marker_c.hasSeverity(MarkerSeverityE::Error);
}

void TestBase::enableDebug(bool en) {
    m_factory->getDebugMgr()->enable(en);
}

}
}
