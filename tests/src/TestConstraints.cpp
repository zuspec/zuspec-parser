/*
 * TestConstraints.cpp
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
#include "TestConstraints.h"


namespace zsp {
namespace parser {


TestConstraints::TestConstraints() {

}

TestConstraints::~TestConstraints() {

}

TEST_F(TestConstraints, foreach_index) {
    const char *text = R"(
        struct S {
            rand int arr[10];

            constraint {
                foreach(arr[i]) {
                    arr[i] == i+1;
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
        "smoke.pss",
        files,
        root,
        false);
}

}
}
