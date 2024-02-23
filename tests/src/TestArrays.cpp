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
        component my_c {

        }
        component pss_top {
            int          arr_10[10];
            int          arr_20[10];
            my_c         arr_30[30];
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

TEST_F(TestArrays, parameterized) {
    const char *text = R"(
        component T_c<int i=1> { }

        component my_c {
            T_c<>       a;
        }
        component pss_top {
            my_c         arr_30[30];
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

TEST_F(TestArrays, parameterized_subelem_ref) {
    const char *text = R"(
        component T_c<int i=1> { 
            int         f1;
        }

        component my_c {
            T_c<>       a;
        }
        component pss_top {
            my_c         arr_30[30];

            exec init_down {
                arr_30[0].a.f1 = 2;
            }
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

TEST_F(TestArrays, parameterized_nested_subelem_ref) {
    const char *text = R"(
        component T_c<int i=1> { 
            int         f1;
        }

        component my_c {
            T_c<>       a;
        }
        component pss_top {
            my_c         arr_30[30];

            action Entry {
                exec post_solve {
                    int i = comp.arr_30[0].a.f1;
                }
            }
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
