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
        "test.pss");
    ASSERT_TRUE(ret.first);
    ASSERT_TRUE(ret.second);
    ast::IGlobalScopeUP global(ret.first);
    ast::ISymbolScopeUP root(ret.second);

    ITaskFindElementByLocationUP finder(m_factory->mkTaskFindElementByLocation());
    std::vector<ast::IScopeChild *> path;

    enableDebug(true);

    ASSERT_TRUE(finder->find(
        path,
        root.get(),
        2,
        15));

}

}
}
