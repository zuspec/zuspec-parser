/*
 * TestArrays.cpp
 *
 * Copyright 2023 Matthew Ballance and Contributors
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
#include "TestArrays.h"


namespace zsp {
namespace parser {


TestArrays::TestArrays() {

}

TestArrays::~TestArrays() {

}

TEST_F(TestArrays, explicit) {
    const char *text = R"(
        component pss_top {
            array<int, 10>          arr_10;
            array<int, 20>          arr_20;
        }
    )";

    enableDebug(true);
    MarkerCollector marker_c; 


    std::vector<ast::IGlobalScopeUP> files;
    ast::ISymbolScopeUP root;

    parseLink(
        marker_c,
        text,
        "explicit.pss",
        files,
        root,
        false);
}

TEST_F(TestArrays, implied) {
    const char *text = R"(
        component pss_top {
            int          arr_10[10];
            int          arr_20[10];
        }
    )";

    enableDebug(true);
    MarkerCollector marker_c; 


    std::vector<ast::IGlobalScopeUP> files;
    ast::ISymbolScopeUP root;

    parseLink(
        marker_c,
        text,
        "explicit.pss",
        files,
        root,
        false);
}

}
}
