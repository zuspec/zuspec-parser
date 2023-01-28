/*
 * TestTypeExtension.cpp
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
#include "TestTypeExtension.h"


namespace zsp {
namespace parser {


TestTypeExtension::TestTypeExtension() {

}

TestTypeExtension::~TestTypeExtension() {

}

TEST_F(TestTypeExtension, comp_ext_action) {
    const char *content = R"(
        component pss_top {
            action A { }
        }

        extend component pss_top {
            action B { }
        }
    )";

    ast::IGlobalScopeUP global;
    ast::ISymbolScopeUP root;
    IMarkerCollectorUP marker_c(m_factory->mkMarkerCollector());

    parseLink(
        marker_c.get(),
        content,
        "comp_ext_action.pss",
        global,
        root
    );

	for (std::vector<IMarkerUP>::const_iterator
			it=marker_c->markers().begin();
			it!=marker_c->markers().end(); it++) {
		fprintf(stdout, "Link Error: %s\n", (*it)->msg().c_str());
	}

    ASSERT_FALSE(marker_c->hasSeverity(MarkerSeverityE::Error));
    ast::IScopeChild *A = findItem(root.get(), {"pss_top", "A"});
    ASSERT_TRUE(A);
    ast::IScopeChild *B = findItem(root.get(), {"pss_top", "A"});
    ASSERT_TRUE(B);

}

TEST_F(TestTypeExtension, comp_ext_action_dup) {
    const char *content = R"(
        component pss_top {
            action A { }
        }

        extend component pss_top {
            action A { }

            action B { }
        }
    )";

    ast::IGlobalScopeUP global;
    ast::ISymbolScopeUP root;
    IMarkerCollectorUP marker_c(m_factory->mkMarkerCollector());

    parseLink(
        marker_c.get(),
        content,
        "comp_ext_action.pss",
        global,
        root
    );

    // Expecting an error about duplicate symbol
    ASSERT_TRUE(marker_c->hasSeverity(MarkerSeverityE::Error));
}

TEST_F(TestTypeExtension, ext_enum_empty) {
    const char *content = R"(
        enum MyEnum { }

        extend enum MyEnum {
            A,
            B,
            C
        }
    )";

    ast::IGlobalScopeUP global;
    ast::ISymbolScopeUP root;
    IMarkerCollectorUP marker_c(m_factory->mkMarkerCollector());

    parseLink(
        marker_c.get(),
        content,
        "comp_ext_action.pss",
        global,
        root
    );

    // Expecting an error about duplicate symbol
    ASSERT_FALSE(marker_c->hasSeverity(MarkerSeverityE::Error));
    ast::IScopeChild *MyEnum_c = findItem(root.get(), {"MyEnum"});
    ASSERT_TRUE(MyEnum_c);
    ast::ISymbolEnumScope *MyEnum = dynamic_cast<ast::ISymbolEnumScope *>(MyEnum_c);
    ASSERT_TRUE(MyEnum);
    ASSERT_EQ(MyEnum->getChildren().size(), 3);
}

TEST_F(TestTypeExtension, ext_enum_unknown) {
    const char *content = R"(
        enum MyEnum { }

        extend enum MyEnum2 {
            A,
            B,
            C
        }
    )";

    ast::IGlobalScopeUP global;
    ast::ISymbolScopeUP root;
    IMarkerCollectorUP marker_c(m_factory->mkMarkerCollector());

    parseLink(
        marker_c.get(),
        content,
        "comp_ext_action.pss",
        global,
        root
    );

    // Expecting an error about not being able to resolve MyEnum2
    ASSERT_TRUE(marker_c->hasSeverity(MarkerSeverityE::Error));
}

TEST_F(TestTypeExtension, ext_struct_unknown) {
    const char *content = R"(
        struct S { }

        extend struct S2 {
            int i;
        }
    )";

    ast::IGlobalScopeUP global;
    ast::ISymbolScopeUP root;
    IMarkerCollectorUP marker_c(m_factory->mkMarkerCollector());

    parseLink(
        marker_c.get(),
        content,
        "comp_ext_action.pss",
        global,
        root
    );

    // Expecting an error about not being able to resolve S2
    ASSERT_TRUE(marker_c->hasSeverity(MarkerSeverityE::Error));
}

}
}
