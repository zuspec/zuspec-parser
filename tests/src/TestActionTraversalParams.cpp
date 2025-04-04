/*
 * TestActionTraversalParams.cpp
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
#include "TestActionTraversalParams.h"


namespace zsp {
namespace parser {


TestActionTraversalParams::TestActionTraversalParams() {

}

TestActionTraversalParams::~TestActionTraversalParams() {

}

// TEST_F(TestActionTraversalParams, smoke) {
//     const char *text = R"(
//         component pss_top {
//             action A {
//                 int v1, v2;
//             }

//             action Entry {
//                 A a1;
//                 activity {
//                     do A(v1=10, v2=10);
//                     a1(v1=20, v2=30) with {

//                     };
//                 }
//             }
//         }
//     )";
//     runTest(text, "smoke.pss");
// }

// TEST_F(TestActionTraversalParams, binding) {
//     const char *text = R"(
//         buffer Buf { }
//         component pss_top {
//             action P {
//                 output Buf  d_out;
//             }

//             action C {
//                input Buf    d_in;
//             }

//             action Entry {
//                 P p1;
//                 C c1;
//                 activity {
//                     p1;
//                     c1(
//                         d_in=p1.d_out // Bind d_in to p1.d_out
//                         ); 
//                 }
//             }
//         }
//     )";
//     runTest(text, "smoke.pss");
// }

}
}
