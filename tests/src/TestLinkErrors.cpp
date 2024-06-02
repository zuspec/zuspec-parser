/*
 * TestLinkErrors.cpp
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
#include "TestLinkErrors.h"


namespace zsp {
namespace parser {


TestLinkErrors::TestLinkErrors() {

}

TestLinkErrors::~TestLinkErrors() {

}

TEST_F(TestLinkErrors, inst_field_static_ref) {
    const char *text = R"(
        component pss_top {
            int         field;

            action Entry {
                exec post_solve {
                    int i = field;
                }
            }
        }
    )";

    enableDebug(true);
    MarkerCollector marker_c; 


    std::vector<ast::IGlobalScopeUP> files;
    ast::ISymbolScopeUP root;

    parseLink(
        &marker_c,
        text,
        "inst_field_static_ref.pss",
        files,
        root,
        false);
}

}
}
