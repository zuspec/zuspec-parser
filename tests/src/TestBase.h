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
#include "zsp/IFactory.h"
#include "zsp/ast/IFactory.h"
#include "gtest/gtest.h"


class TestBase : public ::testing::Test {
public:
    TestBase();

    virtual ~TestBase();

	virtual void SetUp() override;

	virtual void TearDown() override;

protected:

	void runTest(
		const std::string &content,
		const std::string &name);

	zsp::ast::IGlobalScope *parse(
		zsp::IMarkerListener		*marker_l,
		const std::string 			&content,
		const std::string 			&name);

	zsp::ast::ISymbolScope *link(
		zsp::IMarkerListener						*marker_l,
		const std::vector<zsp::ast::IGlobalScopeUP>	&files
	);

	zsp::ast::ISymbolScope *link(
		zsp::IMarkerListener						*marker_l,
		const std::vector<zsp::ast::IGlobalScope *>	&files
	);

    using ParseLinkResultT=std::pair<
        zsp::ast::IGlobalScope *,
        zsp::ast::ISymbolScope *>;

    void parseLink(
        zsp::IMarkerListener        *marker_l,
        const std::string           &content,
        const std::string           &name,
        zsp::ast::IGlobalScopeUP    &global,
        zsp::ast::ISymbolScopeUP    &root);

    zsp::ast::IScopeChild *findItem(
        zsp::ast::ISymbolScope              *root,
        const std::vector<std::string>      &path);


protected:
	zsp::ast::IFactoryUP				m_ast_factory;
	zsp::IFactoryUP						m_factory;

};


