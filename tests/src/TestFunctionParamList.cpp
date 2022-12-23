/*
 * TestFunctionParamList.cpp
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
#include "TestFunctionParamList.h"


namespace zsp {


TestFunctionParamList::TestFunctionParamList() {

}

TestFunctionParamList::~TestFunctionParamList() {

}

TEST_F(TestFunctionParamList, specified) {
    const char *content = R"(
        function void doit(int a, int b, int c);
    )";

    runTest(content, "specified.pss");
}

// TEST_F(TestFunctionParamList, chained) {
//     const char *content = R"(
//         function void doit(int a, b, c, bit d, e, f);
//     )";

//     runTest(content, "specified.pss");
// }

// TEST_F(TestFunctionParamList, ud_type_chained) {
//     const char *content = R"(
//         struct S { }
//         struct P { }
//         function void doit(S a, b, c, P d, e, f);
//     )";

//     runTest(content, "specified.pss");
// }

}
