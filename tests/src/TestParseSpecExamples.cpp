/*
 * TestParseSpecExamples.cpp
 *
 *  Created on: Oct 17, 2020
 *      Author: ballance
 */

#include "TestParseSpecExamples.h"
#include <sstream>
#include "AstBuilder.h"
#include "MarkerCollector.h"
#include "zsp_ast/src/GlobalScope.h"
#include "zsp_ast/src/Factory.h"
#include "zsp/parser/IMarker.h"

namespace zsp {
namespace parser {

TestParseSpecExamples::TestParseSpecExamples() {
	// TODO Auto-generated constructor stub

}

TestParseSpecExamples::~TestParseSpecExamples() {
	// TODO Auto-generated destructor stub
}


TEST_F(TestParseSpecExamples, test_003_enum_data_type) {
    const char *text = R"(
        enum config_modes_e {UNKNOWN, MODE_A=10, MODE_B=20, MODE_C=35,
            MODE_D=40};
        component uart_c {
            action configure {
                rand config_modes_e mode;
                constraint {mode != UNKNOWN; }
            }
        };
    )";
    runTest(text, "003_enum_data_type.pss");
}

TEST_F(TestParseSpecExamples, test_005_string_data_type) {
    const char *text = R"(
        struct string_s {
            rand bit a;
            rand string s;

            constraint {
                if (a == 1) {
                    s == "FOO";
                } else {
                    s == "BAR";
                }
            }
        }
    )";

    enableDebug(false);
    runTest(text, "005_string_data_type.pss");
}

TEST_F(TestParseSpecExamples, test_007_chandle_data_type) {
    const char *text = R"(

function chandle do_init();
struct info_s {
 chandle ptr;

 exec pre_solve {
 ptr = do_init();
 }
}
)";
    runTest(text, "007_chandle_data_type.pss");
}

TEST_F(TestParseSpecExamples, test_008_struct_with_rand_modifier) {
    const char *text = R"(

struct axi4_trans_req {
rand bit[32] axi_addr;
rand bit[32] axi_write_data;
rand bit is_write;
rand bit[4] prot;
rand bit[2] sema4;
}
    )";
    runTest(text, "008_struct_with_rand_modifier.pss");
}

TEST_F(TestParseSpecExamples, test_010_typedef) {
    const char *text = R"(

typedef bit[32] uint32_t;
    )";
    runTest(text, "010_typedef.pss");
}

TEST_F(TestParseSpecExamples, test_012_fixed_size_arrays) {
    const char *text = R"(

//<example>
struct route { }
struct S {
//</example>

int fixed_sized_arr [16]; // array of 16 signed integers
bit [8] byte_arr [256]; // array of 256 bytes
route east_routes [8]; // array of 8 route structs


//<example>
}
//</example>
    )";
    runTest(text, "012_fixed_size_arrays.pss");
}

TEST_F(TestParseSpecExamples, test_014_sum_property_of_an_array) {
    const char *text = R"(

//<example>
struct S {
//</example>
	
bit [8] data [4];
 constraint data_c {
 data.sum > 0 && data.sum < 1000;
 }
 
//<example>
}
//</example>    )";
    runTest(text, "014_sum_property_of_an_array.pss");
}

TEST_F(TestParseSpecExamples, test_017_size_property_of_an_array) {
    const char *text = R"(

//<example>
struct S {
//</example>

bit [8] data [4];
 constraint data_c {
 data.size < 10;
 }
 
//<example>
}
//</example>    )";
    runTest(text, "017_size_property_of_an_array.pss");
}

TEST_F(TestParseSpecExamples, test_018_per_attribute_access_modifier) {
    const char *text = R"(

struct S1 {
 rand int a; // public accessibility (default)
 private rand int b; // private accessibility
 rand int c; // public accessibility (default)
}
    )";
    runTest(text, "018_per_attribute_access_modifier.pss");
}

TEST_F(TestParseSpecExamples, test_019_block_access_modifier) {
    const char *text = R"(

struct S2 {
 private:
 rand int w; // private accessibility
 rand int x; // private accessibility
 public rand int y; // public accessibility
 rand int z; // private accessibility
 public:
 rand int s; // public accessibility
}
    )";
    runTest(text, "019_block_access_modifier.pss");
}

TEST_F(TestParseSpecExamples, test_020_overlap_of_possible_enum_values) {
    const char *text = R"(

//<example>
component top {
//</example>
	
    enum config_modes_e {UNKNOWN, MODE_A=10, MODE_B=20};
    enum foo_e {A=10, B, C};

    action my_a {
        rand config_modes_e cfg;
        rand foo_e foo;
        constraint cfg == (config_modes_e)11; // illegal
        constraint cfg == (config_modes_e)foo; // cfg==MODE_A,
        // the only value in the numeric domain of both cfg and foo
        // ...
    }

//<example>
}
//</example>    )";
    runTest(text, "020_overlap_of_possible_enum_values.pss");
}

TEST_F(TestParseSpecExamples, test_021_casting_of_variable_to_a_vector) {
    const char *text = R"(

package external_fn_pkg {
    enum align_e {byte_aligned = 1, short_aligned = 2, word_aligned = 4};

    function bit[32] alloc_addr(bit[32] size, bit[4] align);

    buffer mem_seg_s {
        rand bit[32] size;
        bit[32] addr;
        align_e al;
        exec post_solve {
            addr = alloc_addr(size, (bit[4])al);
        }
    }
}
    )";
    runTest(text, "021_casting_of_variable_to_a_vector.pss");
}

TEST_F(TestParseSpecExamples, test_022_component) {
    const char *text = R"(

component uart_c { /* ... */ };

    )";
    runTest(text, "022_component.pss");
}

TEST_F(TestParseSpecExamples, test_024_namespace) {
    const char *text = R"(

component usb_c {
 action write {/* ... */}
}
component uart_c {
 action write {/* ... */}
}
component pss_top {
 uart_c s1;
 usb_c s2;
 action entry {
 uart_c::write wr; //refers to the write action in uart_c
 // ...
 }
}
    )";
    runTest(text, "024_namespace.pss");
}

TEST_F(TestParseSpecExamples, test_026_component_instantiation) {
    const char *text = R"(

component vid_pipe_c { /* ... */ };
component codec_c {
 vid_pipe_c pipeA, pipeB;
 action decode { /* ... */};
};
component multimedia_ss_c {
 codec_c codecs[4];
};
component pss_top {
 multimedia_ss_c multimedia_ss;
};
    )";
    enableDebug(true);
    runTest(text, "026_component_instantiation.pss");
}

TEST_F(TestParseSpecExamples, test_028_constraining_a_comp_attribute) {
    const char *text = R"(
component vid_pipe_c { 
//<example>
     action program { /* ... */ }
//</example>
    /* ... */ 
};

component codec_c {
    vid_pipe_c pipeA, pipeB;
    bit mode1_enable;

 
    action decode {
        rand bit mode;
 
        constraint set_mode {
            comp.mode1_enable==0 -> mode == 0;
        }
	
        activity {
            do vid_pipe_c::program with { comp == this.comp.pipeA; };
        }
    };
};

component multimedia_ss_c {
    codec_c codecs[2];

    exec init {
        codecs[0].mode1_enable = 0;
        codecs[1].mode1_enable = 1;
    };
};
    )";
    enableDebug(false);
    runTest(text, "028_constraining_a_comp_attribute.pss");
}

TEST_F(TestParseSpecExamples, test_030_atomic_action) {
    const char *text = R"(

//<example>
component top {
buffer data_buf { /* ... */ }
//</example>
action write {
 output data_buf data;
 rand int size;
 // implementation details
 // ...
};


//<example>
}
//</example>
    )";
    runTest(text, "030_atomic_action.pss");
}

TEST_F(TestParseSpecExamples, test_032_compound_action) {
    const char *text = R"(

//<example>
component top {
//</example>

action sub_a {/* ... */};
action compound_a {
 sub_a a1, a2;
 activity {
 a1;
 a2;
 }
}

//<example>
}
//</example>    )";
    runTest(text, "032_compound_action.pss");
}

TEST_F(TestParseSpecExamples, test_034_extended_action_traversal) {
    const char *text = R"(

component pss_top {
 action A { };
 action B { };
 action C { };
 action entry {
 activity {
 do A;
 }
 }
 extend action entry {
 activity {
 do B;
 }
 }
 extend action entry {
 activity {
 do C;
 }
 }
}

    )";
    runTest(text, "034_extended_action_traversal.pss");
}

TEST_F(TestParseSpecExamples, test_035_hand_coded_action_traversal) {
    const char *text = R"(

component pss_top {
 action A { };
 action B { };
 action C { };
 action entry {
 activity {
 schedule {
 do A;
 do B;
 do C;
 }
 }
 }
}

    )";
    runTest(text, "035_hand_coded_action_traversal.pss");
}

TEST_F(TestParseSpecExamples, test_036_inheritance_and_traversal) {
    const char *text = R"(

component pss_top {
 action A { }
 action B { }
 action C { }
 action base {
 activity {
 do A;
 }
 }
 action ext1 : base {
 activity {
 do B;
 }
 }
 action ext2 : base {
 activity {
 super;
 do C;
 }
 }
}


    )";
    runTest(text, "036_inheritance_and_traversal.pss");
}

TEST_F(TestParseSpecExamples, test_037_action_traversal) {
    const char *text = R"(

//<example>
component top {
//</example>

    action A {
        rand bit[4] f1;
        // ...
    }

    action B {
        A a1, a2;

        activity {
//            a1;
            a2 with {
                f1 < 10;
            };
        }
    }

//<example>
}
//</example>    )";

    enableDebug(false);
    runTest(text, "037_action_traversal.pss");
}

TEST_F(TestParseSpecExamples, test_039_anonymous_action_traversal) {
    const char *text = R"(

//<example>
component top {
//</example>

action A {
 rand bit[4] f1;
 // ...
}
action B {
 activity {
 do A;
 do A with {f1 < 10;};
 }
}


//<example>
}
//</example>    )";
    runTest(text, "039_anonymous_action_traversal.pss");
}

TEST_F(TestParseSpecExamples, test_041_compound_action_traversal) {
    const char *text = R"(
    // <example>
    component top {
    // </example>

        action A {
            rand bit[4] f1;
            // ...
        }

        action B {
            A a1, a2;

            activity {
                a1;
                a2 with {
                    f1 < 10;
                };
            }
        }

        action C {
            action bit[4] max;
            B b1;

            activity {
                max;
                b1 with {
                    a1.f1 <= max;
                };
            }
        }

    // <example>
    }
    // </example>
    )";
    enableDebug(false);
    runTest(text, "041_compound_action_traversal.pss");
}

TEST_F(TestParseSpecExamples, test_043_sequential_block) {
    const char *text = R"(

// example
component top {
action A { /* ... */ }
action B { /* ... */ }
// example

action my_test {
 A a;
 B b;
 activity {
 a;
 b;
 }
};

// example
}
// example
    )";
    runTest(text, "043_sequential_block.pss");
}

TEST_F(TestParseSpecExamples, test_045_variants_of_specifying_sequential_execution_in_activity) {
    const char *text = R"(

// example
component top {
    action A { }
    action B { }
// example

action my_test {
 A a;
 B b;
 activity {
 a;
 b;
 {a; b;};
 sequence{a; b;};
 }
};

// example
}
// example
    )";
    runTest(text, "045_variants_of_specifying_sequential_execution_in_activity.pss");
}

TEST_F(TestParseSpecExamples, test_047_parallel_statement) {
    const char *text = R"(

// example
component top {
 action A { /* ... */ }
 action B { /* ... */ }
 action C { /* ... */ }
// example

action my_test {
 A a;
 B b;
 C c;
 activity {
 a;
 parallel {
 b;
 c;
 }
 }
};

// example
}
// example
    )";
    runTest(text, "047_parallel_statement.pss");
}

TEST_F(TestParseSpecExamples, test_049_another_parallel_statement) {
    const char *text = R"(

// example
component top {
// example

resource R{ /* ... */}

pool [4] R R_pool;

bind R_pool *;

action A { lock R r; }
action B {}
action C {}
action D { lock R r;}
action my_test {
activity {
parallel {
{do A; do B;}
{do C; do D;}
}
}
}

// example
}
// example    )";
    runTest(text, "049_another_parallel_statement.pss");
}

TEST_F(TestParseSpecExamples, test_051_schedule_statement) {
    const char *text = R"(

// example
component top {
action A { /* ... */ }
action B { /* ... */ }
action C { /* ... */ }
// example

action my_test {
 A a;
 B b;
 C c;
 activity {
 a;
 schedule {
 b;
 c;
 }
 }
};

// example
}
// example
    )";
    runTest(text, "051_schedule_statement.pss");
}

TEST_F(TestParseSpecExamples, test_053_scheduling_block_with_sequential_sub_blocks) {
    const char *text = R"(

// example
component top {
// example

action A {}
action B {}
action C {}
action D {}
action my_test {
activity {
schedule {
{do A; do B;}
{do C; do D;}
}
}
}


// example
}
// example    )";
    runTest(text, "053_scheduling_block_with_sequential_sub_blocks.pss");
}

TEST_F(TestParseSpecExamples, test_055_repeat_statement) {
    const char *text = R"(

// example
component top {
 action A { /* ... */ }
 action B { /* ... */ }
// example

action my_test {
 A a;
 B b;
 activity {
 repeat (3) {
 a;
 b;
 }
 }
};

// example
}
// example
    )";
    runTest(text, "055_repeat_statement.pss");
}

TEST_F(TestParseSpecExamples, test_057_another_repeat_statement) {
    const char *text = R"(

// example
component top {
 action my_action1 { /* ... */ }
 action my_action2 { /* ... */ }
// example

action my_test {
 my_action1 action1;
 my_action2 action2;
 activity {
 repeat (i : 10) {
 if ((i % 4) == 0) {
 action1;
 } else {
 action2;
 }
 }
 }
};

// example
}
// example
    )";
    runTest(text, "057_another_repeat_statement.pss");
}

TEST_F(TestParseSpecExamples, test_059_repeat_while_statement) {
    const char *text = R"(

component top {
function bit is_last_one();
action do_something {
bit last_one;
exec post_solve {
last_one = comp.is_last_one();
}
exec body C = """
printf("Do Something\n");
""";
}
action entry {
do_something s1;
activity {
repeat {
s1;
} while (!s1.last_one);
}
}
}
    )";
    runTest(text, "059_repeat_while_statement.pss");
}

TEST_F(TestParseSpecExamples, test_061_foreach_statement) {
    const char *text = R"(

// example
component top {
// example

action my_action1 {
 rand bit in [0..3] val;
 // ...
}
action my_test {
 rand bit [4] in [0..3] a[16];
 my_action1 action1;

 activity {
 foreach (a[j]) {
 action1 with { action1.val <= a[j]; };
 }
 }
};

// example
}
// example
    )";
    runTest(text, "061_foreach_statement.pss");
}

TEST_F(TestParseSpecExamples, test_063_select_statement) {
    const char *text = R"(

// example
component top {
 action my_action1 { /* ... */ }
 action my_action2 { /* ... */ }
// example

action my_test {
 my_action1 action1;
 my_action2 action2;
 activity {
 select {
 action1;
 action2;
 }
 }
}

// example
}
// example
    )";
    runTest(text, "063_select_statement.pss");
}

TEST_F(TestParseSpecExamples, test_065_select_statement_with_guard_conditions_and_weights) {
    const char *text = R"(

// example
component top {
 action my_action1 { /* ... */ }
 action my_action2 { /* ... */ }
 action my_action3 { /* ... */ }
// example

action my_test {
my_action1 action1;
my_action2 action2;
my_action3 action3;
 rand int in [0..4] a;
 activity {
 select {
 (a == 0)[20]: action1;
 (a in [0..3])[30]: action2;
 [50]: action3;
 }
 }
}

// example
}
// example
    )";
    runTest(text, "065_select_statement_with_guard_conditions_and_weights.pss");
}

TEST_F(TestParseSpecExamples, test_067_if_else_statement) {
    const char *text = R"(

// example
component top {
 action A { /* ... */ }
 action B { /* ... */ }
// example

action my_test {
 rand int in [1..10] x;
 A a;
 B b;
 activity {
 if (x > 5)
 a;
 else
 b;
 }
};

// example
}
// example
    )";
    runTest(text, "067_if_else_statement.pss");
}

TEST_F(TestParseSpecExamples, test_069_match_statement) {
    const char *text = R"(

// <example>
component top {
  buffer security_data { /* ... */ }
  action my_action1 { /* ... */ }
  action my_action2 { /* ... */ }
  action my_action3 { /* ... */ }
// </example>

action my_test {
 input security_data in_security_data;
 my_action1 action1;
 my_action2 action2;
 my_action3 action3;
 activity {
 match (in_security_data.val) {
 	[LEVEL2..LEVEL4]: 
 		action1;
	[LEVEL3..LEVEL5]:
		action2;
	default:
		action3;
 }
}
}

// <example>
}
// </example>
    )";
    runTest(text, "069_match_statement.pss");
}

TEST_F(TestParseSpecExamples, test_071_using_a_symbol) {
    const char *text = R"(

component entity {
action a { }
action b { }
action c { }
action top {
 a a1, a2, a3;
 b b1, b2, b3;
 c c1, c2, c3;
 symbol a_or_b {
 select {a1; b1; }
 select {a2; b2; }
 select {a3; b3; }
 }
 activity {
a_or_b;
 c1;
 c2;
 c3;
 }
}
}    )";
    runTest(text, "071_using_a_symbol.pss");
}

TEST_F(TestParseSpecExamples, test_073_using_a_parameterized_symbol) {
    const char *text = R"(

component entity {
 action a { }
 action b { }
 action c { }
 action top {
 a a1, a2, a3;
 b b1, b2, b3;
 c c1, c2, c3;
 symbol ab_or_ba (a aa, b bb) {
 select {
 { aa; bb; }
 { bb; aa; }
 }
 }
 activity {
 ab_or_ba(a1,b1);
 ab_or_ba(a2,b2);
 ab_or_ba(a3,b3);
 c1;
 c2;
 c3;
 }
 }
}

    )";
    runTest(text, "073_using_a_parameterized_symbol.pss");
}

TEST_F(TestParseSpecExamples, test_075_scoping_and_named_sub_activities) {
    const char *text = R"(

// example
component top {
// example

action A {};
action B {
 int x;
 activity {
 L1: parallel { // 'L1' is 1st level named sub-activity
 if (x > 10) {
 L2: { // 'L2' is 2nd level named sub-activity
 A a;
 a;
 }
 {
 A a; // OK - this is a separate naming scope for variables
 a;
 }
 }
 L2: { // Error - this 'L2' conflicts with 'L2' above
 A a;
 a;
 }
 }
 }
};

// example
}
// example

    )";
    runTest(text, "075_scoping_and_named_sub_activities.pss");
}

TEST_F(TestParseSpecExamples, test_076_hierarchical_references_and_named_subactivities) {
    const char *text = R"(

//<example>
component top {
//</example>

action A { rand int x; };
action B {
 A a;
 activity {
 a;
 my_seq: sequence {
 A a;
 a;
 parallel {
	 my_rep: repeat (3) {
	 	A a;
	 	a;
	 };
	 
	 sequence { A a; a; }; // this 'a' is declared in unnamed scope
	 A a; // can't be accessed from outside
	a;
 };
};
};
};
 
action C {
 B b1, b2;
 constraint b1.a.x == 1;
 constraint b1.my_seq.a.x == 2;
 constraint b1.my_seq.my_rep.a.x == 3; // applies to all three iterations
 // of the loop
 activity {
 b1;
 b2 with { my_seq.my_rep.a.x == 4; }; // likewise
 }
};

//<example>
}
//</example>
    )";
    runTest(text, "076_hierarchical_references_and_named_subactivities.pss");
}

TEST_F(TestParseSpecExamples, test_077_bind_statement) {
    const char *text = R"(

component top{
 buffer B {int a;};
 action P1 {
   output B out;
 };
 action P2 {
   output B out;
 };
 action C {
   input B inp;
 };

 pool B B_p;
 bind B {*};

 action T {
   P1 p1;
   P2 p2;
   C c;
   activity {
     p1; 
     p2; 
     c;
     bind p1.out c.inp;
   };
 }
};

    )";
    runTest(text, "077_bind_statement.pss");
}

TEST_F(TestParseSpecExamples, test_079_hierarchical_flow_binding) {
    const char *text = R"(

// example
component top {
 buffer data_buf { /* ... */ }
// example

action sub_a {
 input data_buf din;
 output data_buf dout;
}
action compound_a {
 input data_buf data_in;
 output data_buf data_out;
 sub_a a1, a2;
 activity {
 a1;
 a2;
 bind a1.dout a2.din;
 bind data_in a1.din;
 bind data_out a2.dout;
 }
}

// example
}
// example
    )";
    runTest(text, "079_hierarchical_flow_binding.pss");
}

TEST_F(TestParseSpecExamples, test_081_hierarchical_resource_binding) {
    const char *text = R"(

// example
component top {
  resource reslk_r { /* ... */ }
  resource resshr_r { /* ... */ }
// example

action sub_a {
 lock reslk_r rlkA, rlkB;
 share resshr_r rshA, rshB;
}

action compound_a {
 lock reslk_r crlkA, crlkB;
 share resshr_r crshA, crshB;
 sub_a a1, a2;
 activity {
 schedule {
 a1;
 a2;
 }
 bind crlkA {a1.rlkA, a2.rlkA};
 bind crshA {a1.rshA, a2.rshA};
 bind crlkB {a1.rlkB, a2.rshB};
 bind crshB {a1.rshB, a2.rlkB}; //illegal
 }
}

// example
}
// example
    )";
    runTest(text, "081_hierarchical_resource_binding.pss");
}

TEST_F(TestParseSpecExamples, test_083_buffer_object) {
    const char *text = R"(

struct mem_segment_s {/* ... */};

buffer data_buff_s {
 rand mem_segment_s seg;
};
    )";
    runTest(text, "083_buffer_object.pss");
}

TEST_F(TestParseSpecExamples, test_085_stream_object) {
    const char *text = R"(

struct mem_segment_s { /* ... */};
stream data_stream_s {
 rand mem_segment_s seg;
 };
     )";
    runTest(text, "085_stream_object.pss");
}

TEST_F(TestParseSpecExamples, test_087_state_object) {
    const char *text = R"(

enum mode_e { /* ... */ };
state config_s {
 rand mode_e mode;
 /* ... */
};
    )";
    runTest(text, "087_state_object.pss");
}

TEST_F(TestParseSpecExamples, test_089_buffer_flow_object) {
    const char *text = R"(

// example
component top {
// example

struct mem_segment_s {/*... */};
buffer data_buff_s {
 rand mem_segment_s seg;
 };
action cons_mem_a {
 input data_buff_s in_data;
};
action prod_mem_a {
 output data_buff_s out_data;
};

// example
}
// example
    )";
    runTest(text, "089_buffer_flow_object.pss");
}

TEST_F(TestParseSpecExamples, test_091_stream_flow_object) {
    const char *text = R"(

// example
component top {
// example

struct mem_segment_s {/* ... */};
stream data_stream_s {
 rand mem_segment_s seg;
 };
action cons_mem_a {
 input data_stream_s in_data;
};
action prod_mem_a {
 output data_stream_s out_data;
};

// example
}
// example
    )";
    runTest(text, "091_stream_flow_object.pss");
}

TEST_F(TestParseSpecExamples, test_093_declaring_a_resource) {
    const char *text = R"(

resource DMA_channel_s {
 rand bit[4] priority;
};
    )";
    runTest(text, "093_declaring_a_resource.pss");
}

TEST_F(TestParseSpecExamples, test_095_resource_object) {
    const char *text = R"(

//<example>
component top {
//</example>
resource DMA_channel_s {
 rand bit[4] priority;
};

resource CPU_core_s { /* ... */ };
action two_chan_transfer {
 lock DMA_channel_s chan_A;
 lock DMA_channel_s chan_B;
 share CPU_core_s ctrl_core;
 /* ... */
};

//<example>
}
//</example>    )";
    runTest(text, "095_resource_object.pss");
}

TEST_F(TestParseSpecExamples, test_097_pool_declaration) {
    const char *text = R"(

//<example>
struct mem_segment_s { /* ... */ }
//</example>

buffer data_buff_s {
 rand mem_segment_s seg;
 };
 
resource channel_s { /*...*/ };
component dmac_c {
 pool data_buff_s buff_p;
 // ...
 pool [4] channel_s chan_p;
}
    )";
    runTest(text, "097_pool_declaration.pss");
}

TEST_F(TestParseSpecExamples, test_099_static_binding) {
    const char *text = R"(

struct mem_segment_s { /* ... */ };
buffer data_buff_s {
 rand mem_segment_s seg;
 };
resource channel_s {/* ... */ };
component dma_sub_c {
 /* ... */
}
component dmac_c {
 dma_sub_c dmas1, dmas2;
 pool data_buff_s buff_p;
 bind buff_p {*};
 pool [4] channel_s chan_p;
 bind chan_p {dmas1.*, dmas2.*};
 action mem2mem_a {
 input data_buff_s in_data;
 output data_buff_s out_data;
 /* ... */
 }
}

    )";
    runTest(text, "099_static_binding.pss");
}

TEST_F(TestParseSpecExamples, test_101_pool_binding) {
    const char *text = R"(

state power_state_s { rand int in [0..4] level; }
resource channel_s {}
component graphics_c {
 pool power_state_s power_state_var;
 bind power_state_var *; // accessible to all actions under this
 // component (specifically power_transition's
 //input/output)
 action power_transition {
 input power_state_s curr; //current state
 output power_state_s next; //next state
 lock channel_s chan;
 }
}
component my_multimedia_ss_c {
 graphics_c gfx0;
 graphics_c gfx1;
 pool [4] channel_s channels;
 bind channels {gfx0.*,gfx1.*};// accessible by default to all
 // actions under these components sub-tree
 // (specifically power_transition's chan)
 action observe_same_power_state {
 input power_state_s gfx0_state;
 input power_state_s gfx1_state;
 constraint gfx0_state.level == gfx1_state.level;
 }
 // explicit binding of the two power state variables to the
 // respective inputs of action observe_same_power_state
 bind gfx0.power_state_var observe_same_power_state.gfx0_state;
 bind gfx1.power_state_var observe_same_power_state.gfx1_state;
}

    )";
    runTest(text, "101_pool_binding.pss");
}

TEST_F(TestParseSpecExamples, test_103_resource_object_assignment) {
    const char *text = R"(

resource cpu_core_s {}
component dma_c {
 resource channel_s {}
 pool[2] channel_s channels;
 bind channels {*}; // accessible to all actions
 // under this component (and its sub-tree)
 action transfer {
 lock channel_s chan;
 lock cpu_core_s core;
 }
}
component pss_top {
 dma_c dma0,dma1;
 pool[4] cpu_core_s cpu;
 bind cpu {dma0.*, dma1.*};// accessible to all actions
 // under the two sub-components
 action par_dma_xfers {
 dma_c::transfer xfer_a;
 dma_c::transfer xfer_b;
  // ...
 constraint {xfer_a.core.instance_id != xfer_b.core.instance_id;};
 constraint {xfer_a.chan.instance_id == xfer_b.chan.instance_id;};
 }
}

    )";
    runTest(text, "103_resource_object_assignment.pss");
}

TEST_F(TestParseSpecExamples, test_105_state_object_binding) {
    const char *text = R"(

enum codec_config_mode_e {UNKNOWN, A, B}
component codec_c {
 state configuration_s {
 rand codec_config_mode_e mode;
 constraint initial -> mode == UNKNOWN;
 }
 pool configuration_s config_var;
 bind config_var *;
 action configure {
 input configuration_s prev_conf;
 output configuration_s next_conf;
 constraint prev_conf.mode == UNKNOWN && next_conf.mode in [A, B];
 }
}

    )";
    runTest(text, "105_state_object_binding.pss");
}

TEST_F(TestParseSpecExamples, test_107_declaring_a_static_constraint) {
    const char *text = R"(

//<example>
component top {
//</example>

action A {
 rand bit[32] addr;

 constraint addr_c {
 addr == 0x1000;
 }
}

//<example>
}
//</example>    )";
    runTest(text, "107_declaring_a_static_constraint.pss");
}

TEST_F(TestParseSpecExamples, test_109_declaring_a_dynamic_constraint) {
    const char *text = R"(

//<example>
component top {
//</example>

action B {
 action bit[32] addr;

 dynamic constraint dyn_addr1_c {
 addr in [0x1000..0x1FFF];
 }

 dynamic constraint dyn_addr2_c {
 addr in [0x2000..0x2FFF];
 }
}

//<example>
}
//</example>
    )";
    runTest(text, "109_declaring_a_dynamic_constraint.pss");
}

TEST_F(TestParseSpecExamples, test_111_declaring_a_dynamic_constraint_inside_a_static_constraint) {
    const char *text = R"(

//<example>
component top {
//</example>

 action send_pkt {
 rand bit[16] pkt_sz;
 constraint pkt_sz_c { pkt_sz > 0; }
 constraint interesting_sz_c { small_pkt_c || jumbo_pkt_c; }
 dynamic constraint small_pkt_c { pkt_sz >= 100; }
 dynamic constraint jumbo_pkt_c {pkt_sz > 1500; }
 }
 action scenario {
 activity {
 do send_pkt; // Send a packet with size in [1..100, 1500..65535]
 do send_pkt with {pkt_sz >= 100; }; // Send a small packet with
 // a directly-specified inline constraint
 do send_pkt with {small_pkt_c; }; // Send a small packet by
 // referencing a dynamic constraint
 }
 }
 
//<example>
}
//</example>    )";
    runTest(text, "111_declaring_a_dynamic_constraint_inside_a_static_constraint.pss");
}

TEST_F(TestParseSpecExamples, test_113_inheriting_and_overriding_constraints) {
    const char *text = R"(

buffer data_buff {
rand int size;
constraint size in [1..1024];
constraint size_align { size%4 == 0; } // 4 byte aligned
}
buffer corrupt_data_buff : data_buff {
constraint size_align { size%4 == 1; }
//overrides alignment 1 byte off
constraint corrupt_data_size { size > 256; }
// additional constraint
}
    )";
    runTest(text, "113_inheriting_and_overriding_constraints.pss");
}

TEST_F(TestParseSpecExamples, test_115_action_traversal_in_line_constraint) {
    const char *text = R"(

//<example>
component top {
//</example>

action A {
 rand bit[4] f;
};
action B {
 A a1, a2, a3, a4;

 constraint c1 { a1.f in [8..15]; };
 constraint c2 { a1.f == a4.f; };
 activity {
 a1;
 a2 with {
 f in [8..15]; // same effect as constraint c1 has on a1
 };
 a3 with {
 f == a4.f; // illegal - a4.f is unresolved at this point
 };
 a4;
 }
};

//<example>
}
//</example>
    )";
    runTest(text, "115_action_traversal_in_line_constraint.pss");
}

TEST_F(TestParseSpecExamples, test_117_variable_resolution_inside_with_constraint_block) {
    const char *text = R"(
component subc {
action A {
rand int f;
rand int g;
}
}
component top {
subc sub1, sub2;
action B {
rand int f;
rand int h;
subc::A a;
activity {
a with {
f < h; // sub-action's f and containing action's h
g == this.f; // sub-action's g and containing action's f
comp == this.comp.sub1; // sub-action's component is
// sub-component 'sub1' of the
// parent action's component
};
}
}
}
    )";
    runTest(text, "117_variable_resolution_inside_with_constraint_block.pss");
}

TEST_F(TestParseSpecExamples, test_119_in_constraint) {
    const char *text = R"(

//<example>
struct S {
 rand bit[32] addr;
//</example>
constraint addr_c {
 addr in [0x0000..0xFFFF];
 }
 
//<example>
}
//</example>
    )";
    runTest(text, "119_in_constraint.pss");
}

TEST_F(TestParseSpecExamples, test_121_implication_constraint) {
    const char *text = R"(

struct impl_s {
 rand bit[8] a, b;

 constraint ab_c {
 (a > 5) -> b == 1;
 }
}
    )";
    runTest(text, "121_implication_constraint.pss");
}

TEST_F(TestParseSpecExamples, test_123_if_constraint) {
    const char *text = R"(
struct if_else_s {
 rand bit[8] a, b;

 constraint ab_c {
 if (a > 5) {
 b == 1;
 } else {
 b < a;
 }
 }
}
    )";
    runTest(text, "123_if_constraint.pss");
}

TEST_F(TestParseSpecExamples, test_125_foreach_iterative_constraint) {
    const char *text = R"(

struct foreach_s {
 rand bit[10] fixed_arr[10];

 constraint fill_arr_elem_c {
 foreach (fixed_arr[i]) {
 if (i > 0) {
 fixed_arr[i] > fixed_arr[i-1];
 }
 }
 }
}
    )";
    runTest(text, "125_foreach_iterative_constraint.pss");
}

TEST_F(TestParseSpecExamples, test_127_unique_constraint) {
    const char *text = R"(

struct my_struct {
rand bit[4] in [0..15] A, B, C;
constraint unique_abc_c {
unique {A, B, C};
}
}
    )";
    runTest(text, "127_unique_constraint.pss");
}

TEST_F(TestParseSpecExamples, test_129_scheduling_constraints) {
    const char *text = R"(

//<example>
component top {
    action A { }
    action B { }
    action C { }
    action D { }
//</example>

action my_sub_flow {
 A a; B b; C c; D d;
 activity {
 sequence {
 a;
 schedule {
 b; c; d;
 };
 };
 };
};
action my_top_flow {
 my_sub_flow sf1, sf2;
 activity {
 schedule {
 sf1;
 sf2;
 };
 };
 constraint sequence {sf1.a, sf2.b};
 constraint parallel {sf1.b, sf2.b, sf2.d};
};

//<example>
}
//</example>
    )";
    runTest(text, "129_scheduling_constraints.pss");
}

TEST_F(TestParseSpecExamples, test_130_sequencing_constraint) {
    const char *text = R"(

state power_state_s {
 rand int in [0..3] domain_A, domain_B, domain_C;
 constraint domain_B in [ prev.domain_B - 1,
 prev.domain_B,
 prev.domain_B + 1];
 constraint prev.domain_C==0 -> domain_C in[0,1] || domain_B==0;
};
//...
component power_ctrl_c {
 pool power_state_s psvar;
 bind psvar *;
 action power_trans1 {
 output power_state_s next_state;
 };
 action power_trans2 {
 output power_state_s next_state;
 constraint next_state.domain_C == 0;
 };
};

    )";
    runTest(text, "130_sequencing_constraint.pss");
}

TEST_F(TestParseSpecExamples, test_132_struct_rand_and_non_rand_fields) {
    const char *text = R"(

struct S1 {
 rand bit[4] a;
 bit[4] b;
}
struct S2 {
 rand S1 s1_1;
 S1 s1_2;
}
    )";
    runTest(text, "132_struct_rand_and_non_rand_fields.pss");
}

TEST_F(TestParseSpecExamples, test_134_action_rand_qualified_fields) {
    const char *text = R"(

//<example>
component top {
//</example>

action A {
 rand bit[4] a;
 }

 action B {
 A a_1, a_2;
 rand bit[4] b;

 activity {
 a_1;
 a_2;
 }
 }

//<example>
}
//</example>
     )";
    runTest(text, "134_action_rand_qualified_fields.pss");
}

TEST_F(TestParseSpecExamples, test_136_action_qualified_data_fields) {
    const char *text = R"(


//<example>
component top {
//</example>

action A {
 rand bit[4] a;
 }

 action B {
 action bit[4] a_bit;
 A a_1;

 activity {
 a_bit;
 a_1;
 }
 }
 
//<example>
}
//</example>    )";
    runTest(text, "136_action_qualified_data_fields.pss");
}

TEST_F(TestParseSpecExamples, test_138_randomizing_flow_object_attributes) {
    const char *text = R"(

component top {
buffer mem_obj {
int dat;
constraint dat%2 == 0; // dat must be even
}
action write1 {
output mem_obj out_obj;
constraint out_obj.dat in [1..5];
}
action write2 {
output mem_obj out_obj;
constraint out_obj.dat in [6..10];
}
action read {
input mem_obj in_obj;
constraint in_obj.dat in [8..12];
}
action test {
activity {
do write1;
do read;
}
}
}

    )";
    runTest(text, "138_randomizing_flow_object_attributes.pss");
}

TEST_F(TestParseSpecExamples, test_140_randomizing_resource_object_attributes) {
    const char *text = R"(

component top {
enum rsrc_kind_e {A, B, C, D};
resource rsrc_obj {
rand rsrc_kind_e kind;
}
pool[2] rsrc_obj rsrc_pool;
bind rsrc_pool *;
action something {
share rsrc_obj my_rsrc_inst;
constraint my_rsrc_inst.kind != A;
}
action something_else {
lock rsrc_obj my_rsrc_inst;
}
action test {
activity {
parallel {
do something with { my_rsrc_inst.kind != B; };
 do something with { my_rsrc_inst.kind != C; };
 do something_else;
}
}
}
}

    )";
    runTest(text, "140_randomizing_resource_object_attributes.pss");
}

TEST_F(TestParseSpecExamples, test_142_activity_with_random_fields) {
    const char *text = R"(


//<example>
component top {
//</example>

action A {
 rand bit[4] val;
}

action my_action {
 A a, b, c;
 constraint abc_c {
 a.val < b.val;
 b.val < c.val;
 }
 activity {
 a;
 b;
 c;
 }
}

//<example>
}
//</example>
    )";
    runTest(text, "142_activity_with_random_fields.pss");
}

TEST_F(TestParseSpecExamples, test_144_activity_with_random_fields_in_a_loop) {
    const char *text = R"(

//<example>
component top {
//</example>

action A {
 rand bit[4] val;
}

action my_action {
 A a, b, c, d;
 constraint abc_c {
 a.val < b.val;
 b.val < c.val;
 c.val < d.val;
 }
 activity {
 a;
 repeat (2) {
 b;
 c;
 d;
 }
 }
}

//<example>
}
//</example>
    )";
    runTest(text, "144_activity_with_random_fields_in_a_loop.pss");
}

TEST_F(TestParseSpecExamples, test_146_struct_with_random_fields) {
    const char *text = R"(

struct abc_s {
rand bit[4] in [0..15] a_val, b_val, c_val;
constraint {
a_val < b_val;
b_val < c_val;
}
}
    )";
    runTest(text, "146_struct_with_random_fields.pss");
}

TEST_F(TestParseSpecExamples, test_148_activity_with_random_fields) {
    const char *text = R"(


//<example>
component top {
//</example>

action A {
 rand bit[4] val;
}

action my_action {
 A a, b, c;
 constraint abc_c {
 a.val < b.val;
 b.val < c.val;
 }
 activity {
 a;
 b;
 c;
 }
}

//<example>
}
//</example>
    )";
    runTest(text, "148_activity_with_random_fields.pss");
}

TEST_F(TestParseSpecExamples, test_150_sub_activity_traversal) {
    const char *text = R"(

component top {
action A {
rand bit[4] val;
}
action sub {
A a, b, c;
constraint abc_c {
a.val < b.val;
b.val < c.val;
}
activity {
a;
b;
c;
}
}
action top_action {
A v;
sub s1;
constraint c {
s1.a.val == v.val;
}
activity {
v;
s1;
}
}
}
    )";
    runTest(text, "150_sub_activity_traversal.pss");
}

TEST_F(TestParseSpecExamples, test_152_activity_with_dynamic_constraints) {
    const char *text = R"(

//<example>
component top {
//</example>

action A {
 rand bit[4] val;
}
action dyn {
 A a, b;

 dynamic constraint d1 {
 b.val < a.val;
 b.val <= 5;
 }

 dynamic constraint d2 {
 b.val > a.val;
 b.val <= 7;
 }

 activity {
 a;
 select {
 d1;
 d2;
 }
 b;
 }
}

//<example>
}
//</example>
    )";
    runTest(text, "152_activity_with_dynamic_constraints.pss");
}

TEST_F(TestParseSpecExamples, test_154_pre_solve_post_solve) {
    const char *text = R"(
function bit[6] get_init_val();

function bit[6] get_exp_val(bit[6] stim_val);

struct S1 {
    bit[6] init_val;
    rand bit[6] rand_val;
    bit[6] exp_val;

    exec pre_solve {
        init_val = get_init_val();
    }

    constraint rand_val_c {
        rand_val <= init_val+10;
    }

    exec post_solve {
        exp_val = get_exp_val(rand_val);
    }
}

struct S2 {
    bit[6] init_val;
    rand bit[6] rand_val;
    bit[6] exp_val;
    rand S1 s1_1, s1_2;

    exec pre_solve {
        init_val = get_init_val();
    }

    constraint rand_val_c {
        rand_val > init_val;
    }

    exec post_solve {
        exp_val = get_exp_val(rand_val);
    }
}
    )";
    enableDebug(false);
    runTest(text, "154_pre_solve_post_solve.pss");
}

TEST_F(TestParseSpecExamples, test_156_post_solve_ordering_between_action_and_flow_objects) {
    const char *text = R"(


//<example>
component top {
//</example>

buffer mem_obj {
 exec post_solve { /* ... */}
};
action write {
 output mem_obj out_obj;
 exec post_solve { /* ... */ }
};
action read {
 input mem_obj in_obj;
 exec post_solve { /* ... */ }
};
action test {
 write wr;
 read rd;
 activity {
 	wr;
 	rd;
	bind wr.out_obj rd.in_obj;
 }
 exec post_solve { /* ... */ }
};

//<example>
}
//</example>    )";
    runTest(text, "156_post_solve_ordering_between_action_and_flow_objects.pss");
}

TEST_F(TestParseSpecExamples, test_158_exec_body_block_sampling_external_data) {
    const char *text = R"(

function bit[4] compute_val1(bit[4] v);
function bit[4] compute_val2(bit[4] v);
component pss_top {

 action A {
 rand bit[4] x;
 bit[4] y1, y2;

 constraint assume_y_c {
 y1 >= x && y1 <= x+2;
 y2 >= x && y2 <= x+3;

 y1 <= y2;
 }

 exec body {
 y1 = compute_val1(x);
 y2 = compute_val2(x);
 }
 }
}
    )";
    runTest(text, "158_exec_body_block_sampling_external_data.pss");
}

TEST_F(TestParseSpecExamples, test_160_generating_multiple_scenarios) {
    const char *text = R"(

component pss_top {
 buffer data_buff_s {
 rand int val;};
 pool data_buff_s data_mem;
 bind data_mem *;
 action A_a {output data_buff_s dout;};
 action B_a {output data_buff_s dout;};
 action C_a {input data_buff_s din;};
 action D_a {input data_buff_s din;};
 action root_a {
 A_a a;
 B_a b;
 C_a c;
 D_a d;
 activity {
 select {a; b;}
 select {c; d;}
 }
 }
}

    )";
    runTest(text, "160_generating_multiple_scenarios.pss");
}

TEST_F(TestParseSpecExamples, test_162_action_inferences_for_partially_specified_flows) {
    const char *text = R"(

component pss_top {
 state config_s {};
 pool config_s config_var;
 bind config_var *;
 buffer data_buff_s {};
 pool data_buff_s data_mem;
 bind data_mem *;
 stream data_stream_s {};
 pool data_stream_s data_bus;
 bind data_bus *;
 action setup_A {
 output config_s new_cfg;
 };
 action setup_B {
 output config_s new_cfg;
 };
 action load_data {
 input config_s curr_cfg;
 constraint !curr_cfg.initial;
 output data_buff_s out_data;
 };
 action send_data {
 input data_buff_s src_data;
 output data_stream_s out_data;
 };
 action receive_data {
 input data_stream_s in_data;
 };
};

    )";
    runTest(text, "162_action_inferences_for_partially_specified_flows.pss");
}

TEST_F(TestParseSpecExamples, test_164_object_pools_affect_inferencing) {
    const char *text = R"(

component pss_top {
  buffer data_buff_s {/* ... */};
  pool data_buff_s data_mem1;
  pool data_buff_s data_mem2;

  bind data_mem1 {A_a.dout, C_a.din};
  bind data_mem2 {B_a.dout, D_a.din};

  action A_a {output data_buff_s dout;};
  action B_a {output data_buff_s dout;};
  action C_a {input data_buff_s din;};
  action D_a {input data_buff_s din;};

  action root_a {
    C_a c;
    D_a d;

    activity {
      select {c; d;}
    }
  }
}

    )";
    runTest(text, "164_object_pools_affect_inferencing.pss");
}

TEST_F(TestParseSpecExamples, test_166_inline_data_constraints_affect_action_inferencing) {
    const char *text = R"(
component pss_top {
 buffer data_buff_s {
 rand int val;};
 pool data_buff_s data_mem;
 bind data_mem *;
 action A_a {output data_buff_s dout;};
 action B_a {output data_buff_s dout;};
 action C_a {input data_buff_s din;};
 action D_a {input data_buff_s din;};
 action root_a {
 A_a a;
 B_a b;
 C_a c;
 D_a d;
 activity {
 select {a with{dout.val<5;}; b with {dout.val<5;};}
 select {c; d with {din.val>5;};}
 }
 }
}

    )";
    runTest(text, "166_inline_data_constraints_affect_action_inferencing.pss");
}

TEST_F(TestParseSpecExamples, test_168_data_constraints_affect_action_inferencing) {
    const char *text = R"(
component pss_top {
 buffer data_buff_s {
 rand int val;};
 pool data_buff_s data_mem;
 bind data_mem *;
 action A_a {
 output data_buff_s dout;
 constraint {dout.val<5;}
 };
 action B_a {
 output data_buff_s dout;
 constraint {dout.val<5;}
 };
 action C_a {input data_buff_s din;};
 action D_a {
 input data_buff_s din;
 constraint {din.val > 5;}
 };
 action root_a {
 A_a a;
 B_a b;
 C_a c;
 D_a d;
 activity {
 select {a; b;}
 select {c; d;}
 }
 }
}

    )";
    runTest(text, "168_data_constraints_affect_action_inferencing.pss");
}

TEST_F(TestParseSpecExamples, test_170_single_coverage_point) {
    const char *text = R"(
enum color_e {red, green, blue};
struct s {
rand color_e color;
covergroup {
c : coverpoint color;
} cs1;
}
    )";
    runTest(text, "170_single_coverage_point.pss");
}

TEST_F(TestParseSpecExamples, test_172_two_coverage_points_and_cross_coverage_items) {
    const char *text = R"(

enum color_e {red, green, blue};
struct s {
 rand color_e color;
 rand bit[4] pixel_adr, pixel_offset, pixel_hue;
 covergroup {
 Hue : coverpoint pixel_hue;
 Offset : coverpoint pixel_offset;
 AxC: cross color, pixel_adr;
 all : cross color, Hue, Offset;
 } cs2;
}

    )";
    runTest(text, "172_two_coverage_points_and_cross_coverage_items.pss");
}

TEST_F(TestParseSpecExamples, test_174_creating_a_covergroup_instance_with_a_formal_parameter_list) {
    const char *text = R"(

enum color_e {red, green, blue};
struct s {
rand color_e color;
covergroup cs1(color_e c) {
c : coverpoint c;
}
cs1 cs1_inst(color);
}
    )";
    runTest(text, "174_creating_a_covergroup_instance_with_a_formal_parameter_list.pss");
}

TEST_F(TestParseSpecExamples, test_176_creating_a_covergroup_instance_with_instance_options) {
    const char *text = R"(

enum color_e {red, green, blue};

struct s {
	rand color_e color;
	
	covergroup cs1 (color_e color) {
		c : coverpoint color;
	}
	
	cs1 cs1_inst(color) with {
		option.at_least = 2;
	};
}
    )";
    runTest(text, "176_creating_a_covergroup_instance_with_instance_options.pss");
}

TEST_F(TestParseSpecExamples, test_178_creating_an_inline_covergroup_instance) {
    const char *text = R"(

enum color_e {red, green, blue};
struct s {
rand color_e color;
covergroup {
option.at_least = 2;
c : coverpoint color;
} cs1_inst;
}
    )";
    runTest(text, "178_creating_an_inline_covergroup_instance.pss");
}

TEST_F(TestParseSpecExamples, test_180_specifying_an_iff_condition) {
    const char *text = R"(

struct s {
rand bit[4] s0;
rand bit is_s0_enabled;
covergroup {
coverpoint s0 iff (is_s0_enabled);
} cs4;
}
    )";
    runTest(text, "180_specifying_an_iff_condition.pss");
}

TEST_F(TestParseSpecExamples, test_182_specifying_bins) {
    const char *text = R"(

struct s {
	rand bit[10] v_a;
	
	covergroup {
		coverpoint v_a {
			bins a = [0..63, 65];
			bins b[] = [127..150, 148..191];
			bins c[] = [200, 201, 202];
			bins d = [1000..];
			bins others[] = default;
		}
	} cs;
}
    )";
    runTest(text, "182_specifying_bins.pss");
}

TEST_F(TestParseSpecExamples, test_184_select_all_values_from_0_to_255) {
    const char *text = R"(

struct s {
rand bit[8] x;
covergroup {
a: coverpoint x {
bins mod3[] = [0..255] with (item % 3 == 0);
}
} cs;
}
    )";
    runTest(text, "184_select_all_values_from_0_to_255.pss");
}

TEST_F(TestParseSpecExamples, test_186_using_with_in_a_coverpoint) {
    const char *text = R"(

struct s {
	rand bit[8] x;
	
	covergroup {
		a: coverpoint x {
		bins mod3[] = a with ((a % 3) == 0);
		}
	} cs;
}
    )";
    runTest(text, "186_using_with_in_a_coverpoint.pss");
}

TEST_F(TestParseSpecExamples, test_188_excluding_coverage_point_values) {
    const char *text = R"(

struct s {
  rand bit[4] a;

  covergroup {
    a_cp: coverpoint a {
      ignore_bins ignore_vals = [7,8];
    }
  } cs;
}

    )";
    runTest(text, "188_excluding_coverage_point_values.pss");
}

TEST_F(TestParseSpecExamples, test_190_specifying_illegal_coverage_point_values) {
    const char *text = R"(

struct s {
rand bit[4] a;
covergroup {
coverpoint a {
illegal_bins illegal_vals = [7, 8];
}
} cs23;
}
    )";
    runTest(text, "190_specifying_illegal_coverage_point_values.pss");
}

TEST_F(TestParseSpecExamples, test_192_value_resolution) {
    const char *text = R"(

struct s {
	rand bit[3] p1;
	int [3] p2;
	
	covergroup {
		coverpoint p1 {
			bins b1 = [1, 2..5, 6..10];
			bins b2 = [-1, 1..10, 15];
		}
		coverpoint p2 {
			bins b3 = [1, 2..5, 6..10];
			bins b4 = [-1, 1..10, 15];
		}
	} c1;
}
    )";
    runTest(text, "192_value_resolution.pss");
}

TEST_F(TestParseSpecExamples, test_194_specifying_a_cross) {
    const char *text = R"(

struct s {
rand bit[4] a, b;
covergroup {
aXb : cross a, b;
} cov;
}
    )";
    runTest(text, "194_specifying_a_cross.pss");
}

TEST_F(TestParseSpecExamples, test_196_specifying_cross_bins) {
    const char *text = R"(

struct s {
rand bit[4] a, b;
covergroup {
coverpoint a {
bins low[] = [0..127];
bins high = [128..255];
}
coverpoint b {
bins two[] = b with (b%2 == 0);
}
X : cross a, b {
bins small_a_b = X with (a <= 10 && b<=10);
}
} cov;
}
    )";
    runTest(text, "196_specifying_cross_bins.pss");
}

TEST_F(TestParseSpecExamples, test_198_setting_options) {
    const char *text = R"(

covergroup cs1 (bit[64] a_var, bit[64] b_var) {
option.per_instance = 1;
option.comment = "This is CS1";
a : coverpoint a_var {
option.auto_bin_max = 128;
}
b : coverpoint b_var {
option.weight = 10;
}
}
    )";
    runTest(text, "198_setting_options.pss");
}

TEST_F(TestParseSpecExamples, test_200_per_instance_coverage_of_flow_objects) {
    const char *text = R"(

enum mode_e { M0, M1, M2 }
buffer b1 {
rand mode_e mode;
covergroup {
option.per_instance = true;
coverpoint mode;
} cs;
}
component pss_top {
pool b1 b1_p;
bind b1_p *;
action P_a {
output b1 b1_out;
}
action C_a {
input b1 b1_in;
}
action entry {
activity {
repeat (10) {
do C_a;
}
}
}
}

    )";
    runTest(text, "200_per_instance_coverage_of_flow_objects.pss");
}

TEST_F(TestParseSpecExamples, test_201_per_instance_coverage_in_actions) {
    const char *text = R"(

enum mode_e { M0, M1, M2 }
component pss_top {
action A {
rand mode_e mode;
covergroup {
option.per_instance = true;
coverpoint mode;
} cg;
}
action entry {
A a1;
activity {
repeat (4) {
a1;
}
repeat (10) {
do A;
}
}
}
}

    )";
    runTest(text, "201_per_instance_coverage_in_actions.pss");
}

TEST_F(TestParseSpecExamples, test_202_type_extension) {
    const char *text = R"(

enum config_modes_e {UNKNOWN, MODE_A=10, MODE_B=20};

component uart_c {
    action configure {
        rand config_modes_e mode;
         constraint {mode != UNKNOWN;}
    }
}

package additional_config_pkg {
    extend enum config_modes_e {MODE_C=30, MODE_D=50}

    extend action uart_c::configure {
        constraint {mode != MODE_D;}
    }
}
    )";

    enableDebug(false);
    runTest(text, "202_type_extension.pss");
}

TEST_F(TestParseSpecExamples, test_204_action_type_extension) {
    const char *text = R"(

component mem_ops_c {
    enum mem_block_tag_e {SYS_MEM, A_MEM, B_MEM, DDR};
    buffer mem_buff_s {
        rand mem_block_tag_e mem_block;
    }
    pool mem_buff_s mem;
    bind mem *;
    action memcpy {
        input mem_buff_s src_buff;
        output mem_buff_s dst_buff;
    }
}

package soc_config_pkg {
    extend action mem_ops_c::memcpy {
        rand int in [1, 2, 4, 8] ta_width; // introducing new attribute
        constraint { // layering additional constraint
            src_buff.mem_block in [SYS_MEM, A_MEM, DDR];
            dst_buff.mem_block in [SYS_MEM, A_MEM, DDR];
            ta_width < 4 -> dst_buff.mem_block != A_MEM;
        }
    }
}

component pss_top {
    import soc_config_pkg::*;// explicitly importing the package grants
    // access to types and type-members
    mem_ops_c mem_ops;

    action test {
        mem_ops_c::memcpy cpy1, cpy2;
        constraint cpy1.ta_width == cpy2.ta_width;// constraining an

        // attribute introduced in an extension
        activity {
            repeat (3) {
                parallel { cpy1; cpy2; };
            }
        }
    }
}

    )";
    runTest(text, "204_action_type_extension.pss");
}

TEST_F(TestParseSpecExamples, test_206_enum_type_extensions) {
    const char *text = R"(

package mem_defs_pkg { // reusable definitions
    enum mem_block_tag_e {}; // initially empty
    buffer mem_buff_s {
        rand mem_block_tag_e mem_block;
    }
}

package AB_subsystem_pkg {
    import mem_defs_pkg ::*;
    extend enum mem_block_tag_e {A_MEM, B_MEM};
}

package soc_config_pkg {
    import mem_defs_pkg ::*;
    extend enum mem_block_tag_e {SYS_MEM, DDR};
}

component dma_c {
    import mem_defs_pkg::*;
    action mem2mem_xfer {
        input mem_buff_s src_buff;
        output mem_buff_s dst_buff;
    }
}

extend component dma_c {
    import AB_subsystem_pkg::*;

    // explicitly importing the package grants
    import soc_config_pkg::*; // access to enum items

    action dma_test {
        activity {
            do dma_c::mem2mem_xfer with {
                src_buff.mem_block == A_MEM;
                dst_buff.mem_block == DDR;
            };
        }
    }
}
    )";
    runTest(text, "206_enum_type_extensions.pss");
}

TEST_F(TestParseSpecExamples, test_207_type_inheritance_and_overrides) {
    const char *text = R"(

//<example>
component top {
//</example>

action axi_write_action { /* ... */ };
action xlator_action {
 axi_write_action axi_action;
 axi_write_action other_axi_action;
 activity {
 axi_action; // overridden by instance
 other_axi_action; // overridden by type
 }
};
action axi_write_action_x : axi_write_action { /* ... */};
action axi_write_action_x2 : axi_write_action_x { /* ... */};
action axi_write_action_x3 : axi_write_action_x { /* ... */};
action reg2axi_top {
 override {
 type axi_write_action with axi_write_action_x;
 instance xlator.axi_action with axi_write_action_x2;
 }
 xlator_action xlator;
 activity {
 repeat (10) {
 xlator; // override applies equally to all 10 traversals
 }
 }
};
action reg2axi_top_x : reg2axi_top {
 override {
 instance xlator.axi_action with axi_write_action_x3;
 }
};

//<example>
}
//</example>
    )";
    runTest(text, "207_type_inheritance_and_overrides.pss");
}

TEST_F(TestParseSpecExamples, test_210_data_instantiation_in_a_component) {
    const char *text = R"(

component sub_c {
 int base_addr;

 exec init {
 base_addr = 0x1000;
 }
};
component pss_top {
 sub_c s1, s2;

 exec init {
 s1.base_addr = 0x2000;
 }
}
    )";
    runTest(text, "210_data_instantiation_in_a_component.pss");
}

TEST_F(TestParseSpecExamples, test_212_accessing_component_data_field_from_an_action) {
    const char *text = R"(

component sub_c {
bit[32] base_addr = 0x1000;
action A {
exec body {
// reference base_addr in context component
activate(comp.base_addr + 0x16);
// activate() is an imported function
}
}
}
component pss_top {
sub_c s1, s2;
exec init {
s1.base_addr = 0x1000;
s2.base_addr = 0x2000;
}
action entry {
sub_c::A a;
activity {
repeat (2) {
a; // Runs sub_c::A with 0x1000 as base_addr when
// associated with s1
// Runs sub_c::A with 0x2000 as base_addr when
// associated with s2;
}
}
}
}
    )";
    runTest(text, "212_accessing_component_data_field_from_an_action.pss");
}

TEST_F(TestParseSpecExamples, test_214_referencing_pss_variables_using_mustache_notation) {
    const char *text = R"(

component top {
struct S {
rand int b;
}
action A {
rand int a;
rand S s1;
exec body C = """
 printf("a={{a}} s1.b={{s1.b}} a+b={{a+s1.b}}\n");
""";
}
}
    )";
    runTest(text, "214_referencing_pss_variables_using_mustache_notation.pss");
}

TEST_F(TestParseSpecExamples, test_215_variable_reference_used_to_select_the_function) {
    const char *text = R"(

component top {
action A {
rand bit[2] func_id;
rand bit[4] a;
exec body C = """
 func_{{func_id}}({{a}});
""";
}
}
    )";
    runTest(text, "215_variable_reference_used_to_select_the_function.pss");
}

TEST_F(TestParseSpecExamples, test_216_declaring_a_random_func_id_variable_that_identifies_a_c_function_to_call) {
    const char *text = R"(

component top {
action A {
rand bit[2] func_id;
rand bit[4] a;
exec body C = """
 func_{{func_id}}({{a}});
""";
}
}
    )";
    runTest(text, "216_declaring_a_random_func_id_variable_that_identifies_a_c_function_to_call.pss");
}

TEST_F(TestParseSpecExamples, test_217_allowing_programmatic_declaration_of_a_target_variable_declaration) {
    const char *text = R"(

enum obj_type_e {my_int8,my_int16,my_int32,my_int64};
function string get_unique_obj_name();
import solve function get_unique_obj_name;

buffer mem_buff_s {
 rand obj_type_e obj_type;
 string obj_name;

 exec post_solve {
 obj_name = get_unique_obj_name();
 }

 // declare an object in global space
 exec declaration C = """
 static {{obj_type}} {{obj_name}};
 """;
};
    )";
    runTest(text, "217_allowing_programmatic_declaration_of_a_target_variable_declaration.pss");
}

TEST_F(TestParseSpecExamples, test_218_pi_method) {
    const char *text = R"(

package generic_methods {
 function int compute_value(
int val,
output int out_val);
}
    )";
    runTest(text, "218_pi_method.pss");
}

TEST_F(TestParseSpecExamples, test_220_function_availability) {
    const char *text = R"(

package external_functions_pkg {

 function bit[32] alloc_addr(bit[32] size);

 function void transfer_mem(
 bit[32] src, bit[32] dst, bit[32] size
 );
}
package pregen_tests_pkg {

 import solve function external_functions_pkg::alloc_addr;

 import target function external_functions_pkg::transfer_mem;

}
    )";
    runTest(text, "220_function_availability.pss");
}

TEST_F(TestParseSpecExamples, test_222_explicit_specification_of_the_implementation_language) {
    const char *text = R"(

package known_c_methods {
import C function generic_methods::compute_expected_value;
}
    )";
    runTest(text, "222_explicit_specification_of_the_implementation_language.pss");
}

TEST_F(TestParseSpecExamples, test_224_calling_pi_functions) {
    const char *text = R"(

package external_functions_pkg {

    function bit[32] alloc_addr(bit[32] size);

    function void transfer_mem(
        bit[32] src, bit[32] dst, bit[32] size
    );

    buffer mem_segment_s {
        rand bit[32] size;
        bit[32] addr;

        constraint size in [8..4096];

        exec post_solve {
            addr = alloc_addr(size);
        }
    }
}

component mem_xfer {
    import external_functions_pkg::*;

    action xfer_a {
        input mem_segment_s in_buff;
        output mem_segment_s out_buff;

        constraint in_buff.size == out_buff.size;

        exec body {
            transfer_mem(in_buff.addr, out_buff.addr, in_buff.size);
        }
    }
}
    )";

    enableDebug(false);
    runTest(text, "224_calling_pi_functions.pss");
}

TEST_F(TestParseSpecExamples, test_226_reactive_control_flow) {
    const char *text = R"(

component my_ip_c {
 function int sample_DUT_state();
 import target C function sample_DUT_state;
 // specify mapping to target C function by that same name
 action check_state {
 int curr_val;
 exec body {
 curr_val = comp.sample_DUT_state();
 // value only known during execution on target platform
 }
 };
 action A { };
 action B { };
 action my_test {
 check_state cs;
 activity {
 repeat {
 cs;
 if (cs.curr_val % 2 == 0) {
 do A;
 } else {
 do B;
 }
 } while (cs.curr_val < 10);
 }
 };
};
    )";
    runTest(text, "226_reactive_control_flow.pss");
}

TEST_F(TestParseSpecExamples, test_228_target_template_function_implementation) {
    const char *text = R"(

package thread_ops_pkg {
 function void do_stw(bit[32] val, bit[32] vaddr);
}
package thread_ops_asm_pkg {
 target ASM function void do_stw(bit[32] val, bit[32] vaddr) = """
 loadi RA {{val}}
 store RA {{vaddr}}
 """;
}
    )";
    runTest(text, "228_target_template_function_implementation.pss");
}

TEST_F(TestParseSpecExamples, test_230_import_class) {
    const char *text = R"(

import class base {
 void base_method();
}
import class ext : base {
 void ext_method();
}
    )";
    runTest(text, "230_import_class.pss");
}

TEST_F(TestParseSpecExamples, test_236_export_action) {
    const char *text = R"(

component comp {

 action A1 {
 rand bit mode;
 rand bit[32] val;

 constraint {
 if (mode!=0) {
 val in [0..10];
 } else {
 val in [10..100];
 }
 }
 }

}
package pkg {
 // Export A1, providing a mapping to field 'mode'
 export target comp::A1(bit mode);
}
    )";
    runTest(text, "236_export_action.pss");
}

TEST_F(TestParseSpecExamples, test_240_conditional_processing_static_if) {
    const char *text = R"(

package config_pkg {
 const bool PROTOCOL_VER_1_2 = false;
}

//<example>
component top {
//</example>
compile if (config_pkg::PROTOCOL_VER_1_2) {
 action new_flow {
 activity { /* ... */ }
 }
} else {
 action old_flow {
 activity { /* ... */ }
 }
}

//<example>
}
//</example>
    )";
    runTest(text, "240_conditional_processing_static_if.pss");
}

TEST_F(TestParseSpecExamples, test_241_compile_has) {
    const char *text = R"(

package config_pkg {
}

//<example>
component top {
//</example>

compile if (
	compile has(config_pkg::PROTOCOL_VER_1_2) &&
config_pkg::PROTOCOL_VER_1_2) {
 action new_flow {
 activity { /* ... */}
 }
} else {
 action old_flow {
 	activity { /* ... */}
 }
 
}

//<example>
}
//</example>

    )";
    runTest(text, "241_compile_has.pss");
}

TEST_F(TestParseSpecExamples, test_242_circular_dependency) {
    const char *text = R"(

compile if (compile has(FIELD2)) {
 static const int FIELD1 = 1;
}
compile if (compile has (FIELD1)) {
 static const int FIELD2 = 2;
}
    )";
    runTest(text, "242_circular_dependency.pss");
}

TEST_F(TestParseSpecExamples, test_243_compile_assert) {
    const char *text = R"(

compile if (compile has(FIELD2)) {
 static const int FIELD1 = 1;
}

compile if (compile has (FIELD1)) {
 static const int FIELD2 = 2;
}

compile assert(compile has(FIELD1), "FIELD1 not found");
    )";
    runTest(text, "243_compile_assert.pss");
}

TEST_F(TestParseSpecExamples, test_parse_executor_pkg) {
    const char *text = R"(
package executor_pkg {
    struct executor_trait_s {};

    struct empty_executor_trait_s : executor_trait_s {};

    component executor_base_c {};

    component executor_c<
        struct TRAIT : executor_trait_s = empty_executor_trait_s> : executor_base_c {
        TRAIT trait;
    };

    component executor_group_c<
        struct TRAIT : executor_trait_s = empty_executor_trait_s> {

        function void add_executor(ref executor_c<TRAIT> exe);
    };

    struct executor_claim_s<
        struct TRAIT : executor_trait_s = empty_executor_trait_s> {
        rand TRAIT trait;
    };

    function ref executor_base_c executor();

}
    )";

    runTest(text, "executor_pkg");
}
TEST_F(TestParseSpecExamples, test_parse_addr_reg_pkg) {
    const char *text = R"(
package executor_pkg {
    component executor_base_c {

    }
}

package addr_reg_pkg {
    import executor_pkg::* ;

    component addr_space_base_c {};

    struct addr_trait_s {};

    struct empty_addr_trait_s : addr_trait_s {};

    struct addr_handle_t { }
//    typedef chandle addr_handle_t;

    component contiguous_addr_space_c<
            struct TRAIT : addr_trait_s = empty_addr_trait_s> : addr_space_base_c {
        function addr_handle_t add_region(addr_region_s <TRAIT> r);
        function addr_handle_t add_nonallocatable_region(addr_region_s <> r);
        bool byte_addressable = true;
    };

    component transparent_addr_space_c<
            struct TRAIT: addr_trait_s = empty_addr_trait_s> : contiguous_addr_space_c<TRAIT> {};

    struct addr_region_base_s {
        bit[64] size;
    };

    struct addr_region_s <struct TRAIT : addr_trait_s = empty_addr_trait_s>
        : addr_region_base_s {
        TRAIT trait;
    };

    struct transparent_addr_region_s<
            struct TRAIT : addr_trait_s = empty_addr_trait_s> : addr_region_s<TRAIT> {
        bit[64] addr;
    };

    struct addr_claim_base_s {
        rand bit[64] size;
        rand bool permanent;

        constraint default permanent == false;
    };

    struct addr_claim_s <struct TRAIT : addr_trait_s = empty_addr_trait_s> : addr_claim_base_s {
        rand TRAIT trait;
        rand bit[64] in [64'd2**0, 64'd2**1, 64'd2**2, 64'd2**3 , 64'd2**4 ,
            64'd2**5 , 64'd2**6 , 64'd2**7 , 64'd2**8 , 64'd2**9 , 64'd2**10,
            64'd2**11, 64'd2**12, 64'd2**13, 64'd2**14, 64'd2**15, 64'd2**16,
            64'd2**17, 64'd2**18, 64'd2**19, 64'd2**20, 64'd2**21, 64'd2**22,
            64'd2**23, 64'd2**24, 64'd2**25, 64'd2**26, 64'd2**27, 64'd2**28,
            64'd2**29, 64'd2**30, 64'd2**31, 64'd2**32, 64'd2**33, 64'd2**34,
            64'd2**35, 64'd2**36, 64'd2**37, 64'd2**38, 64'd2**39, 64'd2**40,
            64'd2**41, 64'd2**42, 64'd2**43, 64'd2**44, 64'd2**45, 64'd2**46,
            64'd2**47, 64'd2**48, 64'd2**49, 64'd2**50, 64'd2**51, 64'd2**52,
            64'd2**53, 64'd2**54, 64'd2**55, 64'd2**56, 64'd2**57, 64'd2**58,
            64'd2**59, 64'd2**60, 64'd2**61, 64'd2**62, 64'd2**63] alignment;
        };

    struct transparent_addr_claim_s<
            struct TRAIT : addr_trait_s = empty_addr_trait_s> : addr_claim_s<TRAIT> {
        rand bit[64] addr;
    };

    enum endianness_e {LITTLE_ENDIAN, BIG_ENDIAN};

    struct packed_s<endianness_e e = LITTLE_ENDIAN> {};

    struct sizeof_s<type T> {
        static const int nbytes = /* implementation-specific */ -1;
        static const int nbits = /* implementation-specific */ -1;
    };

    const addr_handle_t nullhandle = /* implementation-specific */ null;

    struct sized_addr_handle_s < 
        int SZ, // in bits
        int lsb = 0,
        endianness_e e = LITTLE_ENDIAN > : packed_s<e> {
        addr_handle_t hndl;
    };

    function addr_handle_t make_handle_from_claim (
        addr_claim_base_s claim,
        bit[64] offset = 0);
function addr_handle_t make_handle_from_handle (addr_handle_t handle,
 bit[64] offset);
function bit[64] addr_value(addr_handle_t hndl);
import target function addr_value;
function bit[8] read8(addr_handle_t hndl);
function bit[16] read16(addr_handle_t hndl);
function bit[32] read32(addr_handle_t hndl);
function bit[64] read64(addr_handle_t hndl);
function void write8 (addr_handle_t hndl, bit[8] data);
function void write16(addr_handle_t hndl, bit[16] data);
function void write32(addr_handle_t hndl, bit[32] data);
function void write64(addr_handle_t hndl, bit[64] data);
function void read_bytes (addr_handle_t hndl, list<bit[8]> data,
 int size);
function void write_bytes(addr_handle_t hndl, list<bit[8]> data);
function void read_struct (addr_handle_t hndl, struct packed_struct);
function void write_struct(addr_handle_t hndl, struct packed_struct);
extend component executor_base_c {
 function bit[8] read8(addr_handle_t hndl);
 function bit[16] read16(addr_handle_t hndl);
 function bit[32] read32(addr_handle_t hndl);
 function bit[64] read64(addr_handle_t hndl);
 function void write8 (addr_handle_t hndl, bit[8] data);
 function void write16(addr_handle_t hndl, bit[16] data);
 function void write32(addr_handle_t hndl, bit[32] data);
 function void write64(addr_handle_t hndl, bit[64] data);
 function void read_bytes (addr_handle_t hndl, list<bit[8]> data,
 int size);
 function void write_bytes(addr_handle_t hndl, list<bit[8]> data);
 };
enum reg_access {READWRITE, READONLY, WRITEONLY};
pure component reg_c < type R,
        reg_access ACC = READWRITE,
        int SZ = (8*sizeof_s<R>::nbytes)> {
//        int SZ = (8*R)> {
function R read();
 import target function read;
 function void write(R r);
 import target function write;
 function bit[SZ] read_val();
 import target function read_val;
 function void write_val(bit[SZ] r);
import target function write_val;
};
struct node_s {
 string name;
 int index;
};
pure component reg_group_c {
 pure function bit[64] get_offset_of_instance(string name);
 pure function bit[64] get_offset_of_instance_array(string name,
 int index);
 pure function bit[64] get_offset_of_path(list<node_s> path);
 function void set_handle(addr_handle_t addr);
 import solve function set_handle;
};
}
    )";
    enableDebug(false);    
    runTest(text, "test_parse_addr_reg_pkg", false);
}

}
}

