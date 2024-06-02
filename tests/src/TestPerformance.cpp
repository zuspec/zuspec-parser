/*
 * TestPerformance.cpp
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
#include <fstream>
#include <iostream>
#include "MarkerCollector.h"
#include "TestPerformance.h"


namespace zsp {
namespace parser {


TestPerformance::TestPerformance() {

}

TestPerformance::~TestPerformance() {

}

TEST_F(TestPerformance, file) {
    std::string fname = "regs.pss";
    std::fstream fs(fname.c_str(), std::ios_base::in);

    MarkerCollector marker_c;

    std::vector<ast::IGlobalScopeUP> global;
    ast::ISymbolScopeUP root;
    bool parse_link = true;
    if (parse_link) {
    parseLink(
        &marker_c,
        &fs,
        fname,
        global,
        root,
        0,
        true);
    } else {
    parse(
        &marker_c,
        &fs,
        fname,
        0,
        false
    );
    }

    fs.close();

    ASSERT_FALSE(marker_c.hasSeverity(MarkerSeverityE::Error));
}

}
}
