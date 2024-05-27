/*
 * TestLinkOverlay.cpp
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
#include "dmgr/impl/DebugMacros.h"
#include "zsp/parser/IFactory.h"
#include "MarkerCollector.h"
#include "TestLinkOverlay.h"


namespace zsp {
namespace parser {


TestLinkOverlay::TestLinkOverlay() {

}

TestLinkOverlay::~TestLinkOverlay() {

}

TEST_F(TestLinkOverlay, single_file_overlay_add_type) {
    std::string file1 = R"(
        struct A { }
        struct B : A { }
    )";

    std::string file1_p = file1 + R"(
        struct C : B { }
    )";

    MarkerCollector marker_c;

    enableDebug(true);

    ast::IGlobalScopeUP file;
    ast::ISymbolScopeUP root;
    parseLink(
        &marker_c,
        file1,
        "file1.pss",
        file,
        root);
    
    ASSERT_FALSE(checkErrors(marker_c));

    DEBUG("Finished linking base SymTree");

    ast::IGlobalScopeUP file_p(parse(
        &marker_c,
        file1_p,
        "file1.pss"));

    ASSERT_FALSE(checkErrors(marker_c));

    // Now, need to overlay content on the original
    // linked AST
    ILinkerUP linker(m_factory->mkAstLinker());
    
    ast::IRootSymbolScopeUP root_p(linker->linkOverlay(
        &marker_c,
        dynamic_cast<ast::IRootSymbolScope *>(root.get()),
        file_p.get()
    ));
}

}
}
