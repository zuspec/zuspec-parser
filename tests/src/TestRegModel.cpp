/*
 * TestRegModel.cpp
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
#include "MarkerCollector.h"
#include "TestRegModel.h"


namespace zsp {
namespace parser {


TestRegModel::TestRegModel() {

}

TestRegModel::~TestRegModel() {

}

TEST_F(TestRegModel, reg_c_field) {
    const char *text = R"(
        import addr_reg_pkg::*;

        component my_regs : reg_group_c {
            reg_c<bit[32]>      r1;
        }
    )";

    enableDebug(true);
    MarkerCollector marker_c; 


    std::vector<ast::IGlobalScopeUP> files;
    ast::ISymbolScopeUP root;

    parseLink(
        marker_c,
        text,
        "reg_c_field.pss",
        files,
        root,
        true);
}

TEST_F(TestRegModel, reg_group_c_field) {
    const char *text = R"(
        import addr_reg_pkg::*;

        component my_regs : reg_group_c {
            reg_c<bit[32]>      r1;
        }

        component pss_top {
            my_regs regs;
        }
    )";

    enableDebug(true);
    MarkerCollector marker_c; 


    std::vector<ast::IGlobalScopeUP> files;
    ast::ISymbolScopeUP root;

    parseLink(
        marker_c,
        text,
        "reg_c_field.pss",
        files,
        root,
        true);
}

}
}
