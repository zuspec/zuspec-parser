/*
 * TestTaskFindElementByLocation.cpp
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
#include "TestTaskFindElementByLocation.h"


namespace zsp {
namespace parser {


TestTaskFindElementByLocation::TestTaskFindElementByLocation() {

}

TestTaskFindElementByLocation::~TestTaskFindElementByLocation() {

}

TEST_F(TestTaskFindElementByLocation, smoke) {
    const char *content = R"(
    component pss_top { // line 2, position 15-21
        action A {

        }
    }
    )";

    IMarkerCollectorUP marker_c(m_factory->mkMarkerCollector());
    std::pair<ast::IGlobalScope *, ast::ISymbolScope *> ret = parseLink(
        marker_c.get(),
        content,
        "test.pss",
        true);
    ASSERT_TRUE(ret.first);
    ASSERT_TRUE(ret.second);
    ast::IGlobalScopeUP global(ret.first);
    ast::ISymbolScopeUP root(ret.second);

    ITaskFindElementByLocationUP finder(m_factory->mkTaskFindElementByLocation());
    std::vector<ast::IScopeChild *> path;

    enableDebug(true);

    ITaskFindElementByLocation::Result result = finder->find(
        root.get(),
        global.get(),
        2,
        15);
    ASSERT_TRUE(result.isValid);
    ASSERT_TRUE(result.isType);
    ASSERT_TRUE(result.target);
    ASSERT_EQ(result.docComment, "");
}

TEST_F(TestTaskFindElementByLocation, docCommentType) {
    const char *content = R"(
    // This is a doc comment
    component pss_top { // line 3, position 15-21
        action A {

        }
    }
    )";

    IMarkerCollectorUP marker_c(m_factory->mkMarkerCollector());
    std::pair<ast::IGlobalScope *, ast::ISymbolScope *> ret = parseLink(
        marker_c.get(),
        content,
        "test.pss",
        true);
    ASSERT_TRUE(ret.first);
    ASSERT_TRUE(ret.second);
    ast::IGlobalScopeUP global(ret.first);
    ast::ISymbolScopeUP root(ret.second);

    ITaskFindElementByLocationUP finder(m_factory->mkTaskFindElementByLocation());
    std::vector<ast::IScopeChild *> path;

    enableDebug(true);

    ITaskFindElementByLocation::Result result = finder->find(
        root.get(),
        global.get(),
        3,
        15);
    ASSERT_TRUE(result.isValid);
    ASSERT_TRUE(result.isType);
    ASSERT_TRUE(result.target);
    ASSERT_NE(result.docComment, "");
//    ASSERT_TRUE(strstr(result.docComment.c_str(), ""This is ");
}

TEST_F(TestTaskFindElementByLocation, field) {
    const char *content = R"(
    component C { }
    component pss_top { 
        C      c1; // line 4, position 16-17
        action A {

        }
    }
    )";

    IMarkerCollectorUP marker_c(m_factory->mkMarkerCollector());
    std::pair<ast::IGlobalScope *, ast::ISymbolScope *> ret = parseLink(
        marker_c.get(),
        content,
        "test.pss",
        true);
    ASSERT_TRUE(ret.first);
    ASSERT_TRUE(ret.second);
    ast::IGlobalScopeUP global(ret.first);
    ast::ISymbolScopeUP root(ret.second);

    ITaskFindElementByLocationUP finder(m_factory->mkTaskFindElementByLocation());
    std::vector<ast::IScopeChild *> path;

    enableDebug(true);

    ITaskFindElementByLocation::Result result = finder->find(
        root.get(),
        global.get(),
        4,
        16);
    ASSERT_TRUE(result.isValid);
    ASSERT_FALSE(result.isType);
    ASSERT_TRUE(result.target);
    ASSERT_EQ(result.docComment, "");
}

TEST_F(TestTaskFindElementByLocation, fieldType) {
    const char *content = R"(
    component C { }
    component pss_top { 
        C      c1; // line 4, position 9
        action A {

        }
    }
    )";

    IMarkerCollectorUP marker_c(m_factory->mkMarkerCollector());
    std::pair<ast::IGlobalScope *, ast::ISymbolScope *> ret = parseLink(
        marker_c.get(),
        content,
        "test.pss",
        true);
    ASSERT_TRUE(ret.first);
    ASSERT_TRUE(ret.second);
    ast::IGlobalScopeUP global(ret.first);
    ast::ISymbolScopeUP root(ret.second);

    ITaskFindElementByLocationUP finder(m_factory->mkTaskFindElementByLocation());
    std::vector<ast::IScopeChild *> path;

    enableDebug(true);

    ITaskFindElementByLocation::Result result = finder->find(
        root.get(),
        global.get(),
        4,
        9);
    ASSERT_TRUE(result.isValid);
    ASSERT_TRUE(result.isType);
    ASSERT_TRUE(result.target);
    ASSERT_TRUE(dynamic_cast<ast::ITypeScope *>(result.target));
    ASSERT_EQ(dynamic_cast<ast::ITypeScope *>(result.target)->getName()->getId(), "C");
    ASSERT_EQ(result.docComment, "");
}

TEST_F(TestTaskFindElementByLocation, fieldTypeDocComment) {
    const char *content = R"(
    /**
     * Component-type C
     */
    component C { }
    component pss_top { 
        C      c1; // line 7, position 9
        action A {

        }
    }
    )";

    IMarkerCollectorUP marker_c(m_factory->mkMarkerCollector());
    std::pair<ast::IGlobalScope *, ast::ISymbolScope *> ret = parseLink(
        marker_c.get(),
        content,
        "test.pss",
        true);
    ASSERT_TRUE(ret.first);
    ASSERT_TRUE(ret.second);
    ast::IGlobalScopeUP global(ret.first);
    ast::ISymbolScopeUP root(ret.second);

    ITaskFindElementByLocationUP finder(m_factory->mkTaskFindElementByLocation());
    std::vector<ast::IScopeChild *> path;

    enableDebug(true);

    ITaskFindElementByLocation::Result result = finder->find(
        root.get(),
        global.get(),
        7,
        9);
    ASSERT_TRUE(result.isValid);
    ASSERT_TRUE(result.isType);
    ASSERT_TRUE(result.target);
    ASSERT_TRUE(dynamic_cast<ast::ITypeScope *>(result.target));
    ASSERT_EQ(dynamic_cast<ast::ITypeScope *>(result.target)->getName()->getId(), "C");
    ASSERT_NE(result.docComment, "");
}

}
}
