/*
 * TestParseExamples.cpp
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
#include "MarkerCollector.h"
#include "TestParseExamples.h"


namespace zsp {
namespace parser {


TestParseExamples::TestParseExamples() {

}

TestParseExamples::~TestParseExamples() {

}

TEST_F(TestParseExamples, pss_lib_mem_util_c) {
    const char *mem_util_c_pss = R"(
package pssutil {
    import addr_reg_pkg::*;

    component MemUtilC {

        /**
         * GenRefData
         */
        action GenRefData {
            output mem::MemRefData              dout;
            rand addr_claim_s<mem::MemTrait>    claim;

            constraint dout.size == claim.size;
            constraint claim.alignment == dout.alignment;

            exec post_solve {
                dout.addr_h = make_handle_from_claim(claim);
            }

            exec body {
                random::RandState rs;
                bit[64] val;
                bit[64] max;

                if (dout.alignment == 8) {
                    max = 0xFFFF_FFFF_FFFF_FFFF;
                } else {
                    max = (1 << 8*dout.alignment)-1;
                }

                if (dout.kind == Rand) {
                    random::RandState_init(rs, dout.ref_val);
                    val = random::RandState_next_range(rs, 0, max);
                } else {
                    val = dout.ref_val;
                }

                repeat (i : (dout.size / dout.alignment)) {
                    match (dout.alignment) {
                        [1]: write8(
                            make_handle_from_handle(dout.addr_h, i*dout.alignment),
                            val);
                        [2]: write16(
                            make_handle_from_handle(dout.addr_h, i*dout.alignment),
                            val);
                        [4]: write32(
                            make_handle_from_handle(dout.addr_h, i*dout.alignment),
                            val);
                        [8]: write64(
                            make_handle_from_handle(dout.addr_h, i*dout.alignment),
                            val);
                    }

                    if (dout.kind == Rand) {
                        val = random::RandState_next_range(rs, 0, max);
                    } else if (dout.kind == Incr) {
                        val += 1;
                        if (val > max) {
                            val = 0;
                        }
                    }
                }
            }
        }
    }
}
    )";
    MarkerCollector marker_c;
    ast::IGlobalScopeUP global(parse(&marker_c, mem_util_c_pss, "mem_util_c.pss"));
    ASSERT_TRUE(global.get());
}

}
}
