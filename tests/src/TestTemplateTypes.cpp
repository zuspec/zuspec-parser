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

TEST_F(TestTemplateTypes, two_equiv_simple_specializations) {
    const char *text = R"(
        package p {
            struct S {
                int i;
            }
            struct Q<type T> {
                rand T   v1;

//                constraint v1.i == 0;
            }
            struct Top {
                Q<int>        v1;
                Q<int>        v2;
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

TEST_F(TestTemplateTypes, type_param_with_specialized_default) {
    const char *text = R"(
        package p {
            struct sz_t<type T> {
                static const int xz;
            }

            struct Q<type R, int SZ=sz_t<R>::xz> {
                rand R   v1;
            }

            struct Top {
//                Q<int,sz_t<int>::xz>        v1;
                Q<int>        v1;
//                Q<int>        v2;
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

TEST_F(TestTemplateTypes, sizeof_s) {
    const char *text = R"(
        import addr_reg_pkg::*;

        component pss_top {
            int sz = sizeof_s<int>::nbits;
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
        true);
}

TEST_F(TestTemplateTypes, sizeof_s_2) {
    const char *text = R"(
        import addr_reg_pkg::*;
        struct R : packed_s<> {
            bit[8]  a;
            bit[8]  b;
            bit[8]  c;
        }

        component pss_top {
//            int sz1 = sizeof_s<int>::nbits;
            int sz2 = sizeof_s<R>::nbits;
//            int sz3 = sizeof_s<bit[64]>::nbits;
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
        true);
}

TEST_F(TestTemplateTypes, reg_c_1) {
    const char *text = R"(
        import addr_reg_pkg::*;

        pure component my_regs : reg_group_c {
            reg_c<int>      r1;
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
        &marker_c,
        text,
        "smoke.pss",
        files,
        root,
        true);
}

TEST_F(TestTemplateTypes, dflt_param_vals) {
    const char *text = R"(
        struct addr_trait_s { }
        struct empty_addr_trait_s : addr_trait_s { int f1; }

        component contiguous_addr_space_c<struct TRAIT : addr_trait_s = empty_addr_trait_s> { 
            TRAIT trait;
        }

        component transparent_addr_space_c<struct TRAIT: addr_trait_s = empty_addr_trait_s> : contiguous_addr_space_c<TRAIT> { }

        component pss_top {
            transparent_addr_space_c<>   c1;

            exec init_down {
                c1.trait.f1 = 0;
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

TEST_F(TestTemplateTypes, nested_template_specializations) {
    const char *text = R"(
        component addr_space_base_c {};

        struct addr_trait_s { int f1; };

        struct addr_region_s <struct TRAIT : addr_trait_s = empty_addr_trait_s> { 
            TRAIT trait;
        };

        struct empty_addr_trait_s : addr_trait_s {};

//    typedef chandle addr_handle_t;
        struct addr_handle_t { }

        component contiguous_addr_space_c<struct TRAIT : addr_trait_s = empty_addr_trait_s> : addr_space_base_c {
            function addr_handle_t add_region(addr_region_s <TRAIT> r);
        };

        component transparent_addr_space_c<
            struct TRAIT: addr_trait_s = empty_addr_trait_s> : contiguous_addr_space_c<TRAIT> {};

        component pss_top {
            transparent_addr_space_c<>   c1;
//            addr_region_s<>              r1;

            exec init_down {
//                r1.trait.f1 = 0;
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

TEST_F(TestTemplateTypes, reg_c_templated) {
    const char *text = R"(
        import addr_reg_pkg::*;

        component my_regs : reg_group_c {
            reg_c<bit[32]>      r1;
        }

/*
        component pss_top {
            transparent_addr_space_c<>   c1;
//            addr_region_s<>              r1;

            exec init_down {
//                r1.trait.f1 = 0;
            }
        }
 */
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
        true);
}

}
}
