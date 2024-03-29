/*
 * TestImportLink.cpp
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
#include "TestImportLink.h"


namespace zsp {
namespace parser {



TestImportLink::TestImportLink() {

}

TestImportLink::~TestImportLink() {

}

TEST_F(TestImportLink, struct_typeref) {
    const char *text = R"(
    struct A { }
    struct B : A { }
    )";

    enableDebug(true);
    MarkerCollector marker_c; 
    std::vector<ast::IGlobalScopeUP> files;

    files.push_back(ast::IGlobalScopeUP(parse(
        &marker_c,
        text,
        "struct_typeref.pss"
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

TEST_F(TestImportLink, struct_valp_typeref) {
    const char *text = R"(
    struct A<int T> { }
    struct B : A<2> { }
    )";

    enableDebug(true);
    MarkerCollector marker_c; 
    std::vector<ast::IGlobalScopeUP> files;

    files.push_back(ast::IGlobalScopeUP(parse(
        &marker_c,
        text,
        "struct_typeref.pss"
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

TEST_F(TestImportLink, ambiguous_wildcard_imp) {
    const char *text = R"(
    package p1 {
        struct A { }
    }
    package p2 {
        struct A { }
    }
    package p3 {
        import p1::*;
        import p2::*;
        struct B : A { }
    }
    )";

    enableDebug(true);
    MarkerCollector marker_c; 
    std::vector<ast::IGlobalScopeUP> files;

    files.push_back(ast::IGlobalScopeUP(parse(
        &marker_c,
        text,
        "ambiguous_wildcard_imp.pss"
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
    ASSERT_EQ(marker_c.markers().size(), 1);
    ASSERT_TRUE(marker_c.markers().at(0)->msg().find("Ambiguous symbol resolution") != -1);
    ASSERT_TRUE(marker_c.hasSeverity(MarkerSeverityE::Error));
}

}
}

