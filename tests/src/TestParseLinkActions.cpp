/*
 * TestParseLinkActions.cpp
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
#include "TestParseLinkActions.h"


namespace zsp {
namespace parser {


TestParseLinkActions::TestParseLinkActions() {

}

TestParseLinkActions::~TestParseLinkActions() {

}

TEST_F(TestParseLinkActions, action_qref) {
    const char *text = R"(
/**
 * Comment about D.
 * - **come on**
 * - **do better**
 */
component D {

}

component A {
    D       d1;

    action Entry {
        activity {
        }
    }
})";

    enableDebug(true);

    ast::IGlobalScopeUP global;
    ast::ISymbolScopeUP root;

    MarkerCollector marker_c;
    parseLink(
        &marker_c,
        text,
        "test.pss",
        global,
        root,
        0
    );

    global.release();
}

}
}
