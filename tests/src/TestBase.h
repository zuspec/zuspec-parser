/**
 * TestBase.h
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
#pragma once
#include <vector>
#include "dmgr/IDebugMgr.h"
#include "zsp/parser/IFactory.h"
#include "zsp/ast/IFactory.h"
#include "gtest/gtest.h"
#include "MarkerCollector.h"

namespace zsp {
namespace parser {


class TestBase : public ::testing::Test {
public:
    TestBase();

    virtual ~TestBase();

	virtual void SetUp() override;

	virtual void TearDown() override;

protected:

	void runTest(
		const std::string   &content,
		const std::string   &name,
        bool                load_stdlib=true);

	ast::IGlobalScope *parse(
		parser::IMarkerListener		        *marker_l,
		const std::string 			        &content,
		const std::string 			        &name,
        int32_t                             fileid=0,
        bool                                process_doc_comments=false);

	ast::ISymbolScope *link(
		parser::IMarkerListener				    *marker_l,
		const std::vector<ast::IGlobalScopeUP>	&files
	);

	ast::ISymbolScope *link(
		parser::IMarkerListener				        *marker_l,
		const std::vector<ast::IGlobalScope *>	    &files
	);

    using ParseLinkResultT=std::pair<
        ast::IGlobalScope *,
        ast::ISymbolScope *>;

    void parseLink(
        MarkerCollector                     &marker_c,
        const std::string                   &content,
        const std::string                   &name,
        std::vector<ast::IGlobalScopeUP>    &files,
        ast::ISymbolScopeUP                 &root,
        bool                                load_stdlib=true);

    void parseLink(
        parser::IMarkerListener        *marker_l,
        const std::string              &content,
        const std::string              &name,
        ast::IGlobalScopeUP            &global,
        ast::ISymbolScopeUP            &root,
        int32_t                        fileid=0);

    std::pair<ast::IGlobalScope *, ast::ISymbolScope *> parseLink(
        parser::IMarkerListener        *marker_l,
        const std::string              &content,
        const std::string              &name,
        bool                           process_doc_comments=false);

    ast::IScopeChild *findItem(
        ast::ISymbolScope                   *root,
        const std::vector<std::string>      &path);

    bool checkErrors(MarkerCollector &marker_c);

    void enableDebug(bool en);


protected:
    dmgr::IDebug                        *m_dbg;
	ast::IFactory				        *m_ast_factory;
	parser::IFactory				    *m_factory;

};


}
}
