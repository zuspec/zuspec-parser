/*
 * TestProceduralStmts.cpp
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
#include "TestProceduralStmts.h"


namespace zsp {
namespace parser {


TestProceduralStmts::TestProceduralStmts() {

}

TestProceduralStmts::~TestProceduralStmts() {

}

TEST_F(TestProceduralStmts, nested_if_else_vars) {
    const char *text = R"(
        function void doit(int pval) {
            int lval = 1;
            if (lval == 2) {
                int l1_val /*= lval+1*/;
                int l1_val2 = l1_val;
                if (l1_val == 1) {

                }
            } else if (pval == 3) {
                int l2_val = pval+2;
                if (l2_val == 1) {

                }
            } else if (lval == 2) {

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
        "nested_if_else_vars.pss",
        files,
        root,
        false);

}

TEST_F(TestProceduralStmts, iteration_var) {
    const char *text = R"(
        function void doit(int pval) {
            repeat (i : 20) {
                i = i + 1;
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
        "nested_if_else_vars.pss",
        files,
        root,
        false);

}

}
}
