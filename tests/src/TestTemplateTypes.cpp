/*
 * TestTemplateTypes.cpp
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
#include "MarkerCollector.h"
#include "TestTemplateTypes.h"


namespace zsp {
namespace parser {


TestTemplateTypes::TestTemplateTypes() {

}

TestTemplateTypes::~TestTemplateTypes() {

}

TEST_F(TestTemplateTypes, smoke) {
    const char *text = R"(
        package p {
            struct S {
                int i;
            }
            struct Q<type T> {
                rand T   v1;

                constraint v1.i == 0;
            }
            struct Top {
                Q<S>        v;
            }
        }
    )";
    enableDebug(true);
    MarkerCollector marker_c; 
    std::vector<ast::IGlobalScopeUP> files;

    files.push_back(ast::IGlobalScopeUP(parse(
        &marker_c,
        text,
        "template_smoke.pss"
    )));

    for (std::vector<IMarkerUP>::const_iterator
        it=marker_c.markers().begin();
        it!=marker_c.markers().end(); it++) {
        fprintf(stdout, "Parse Error: %s\n", (*it)->msg().c_str());
    }
    ASSERT_FALSE(marker_c.hasSeverity(MarkerSeverityE::Error));

    ast::ISymbolScopeUP root(link(
        &marker_c,
        files
    ));

    for (std::vector<IMarkerUP>::const_iterator
        it=marker_c.markers().begin();
        it!=marker_c.markers().end(); it++) {
        fprintf(stdout, "Marker: %s\n", (*it)->msg().c_str());
    }
    ASSERT_FALSE(marker_c.hasSeverity(MarkerSeverityE::Error));
}

}
}
