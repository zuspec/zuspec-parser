/*
 * TestFunctionDecl.cpp
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
#include "zsp/parser/impl/TaskGetName.h"
#include "TestFunctionDecl.h"


namespace zsp {
namespace parser {


TestFunctionDecl::TestFunctionDecl() {

}

TestFunctionDecl::~TestFunctionDecl() {

}

TEST_F(TestFunctionDecl, simple_decl) {
    const char *text = R"(
        component pss_top {
            action Entry {
            }
        }

        function void doit1() {
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

    std::unordered_map<std::string,int32_t>::const_iterator doit1_idx;  
    doit1_idx = root->getSymtab().find("doit1");
    ASSERT_NE(doit1_idx, root->getSymtab().end());

    ast::IScopeChild *doit1 = root->getChildren().at(doit1_idx->second).get();
    ASSERT_TRUE(doit1);
    
    std::string fname = TaskGetName().get(doit1);
    ASSERT_EQ(fname, "doit1");

    std::string qname = TaskGetName().get(doit1, true);
    ASSERT_EQ(qname, "doit1");
}    

TEST_F(TestFunctionDecl, builtin) {
    const char *text = R"(
        import std_pkg::*;
        import addr_reg_pkg::*;

        component pss_top {
            action Entry {
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
        true);

    std::unordered_map<std::string,int32_t>::const_iterator addr_reg_pkg_idx;  
    addr_reg_pkg_idx = root->getSymtab().find("addr_reg_pkg");
    ASSERT_NE(addr_reg_pkg_idx, root->getSymtab().end());

    ast::ISymbolScope *addr_reg_pkg = dynamic_cast<ast::ISymbolScope *>(
        root->getChildren().at(addr_reg_pkg_idx->second).get());
    ASSERT_TRUE(addr_reg_pkg);

    std::unordered_map<std::string,int32_t>::const_iterator write64_idx;  
    write64_idx = addr_reg_pkg->getSymtab().find("write64");
    ASSERT_NE(write64_idx, root->getSymtab().end());

    ast::ISymbolScope *write64 = dynamic_cast<ast::ISymbolFunctionScope *>(
        addr_reg_pkg->getChildren().at(write64_idx->second).get());
    ASSERT_TRUE(write64);
    
    std::string fname = TaskGetName().get(write64);
    ASSERT_EQ(fname, "write64");

    std::string qname = TaskGetName().get(write64, true);
    ASSERT_EQ(qname, "addr_reg_pkg::write64");
}    

}
}
