/*
 * PMacroProcLexer.cpp
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
#include "PMacroProcLexer.h"


namespace zsp {
namespace parser {


PMacroProcLexer::PMacroProcLexer(
    antlr4::ANTLRInputStream            *input,
    int32_t                             fileid,
    IMarkerListener                     *marker_l) : 
        PSSLexer(input), m_fileid(fileid), m_marker_l(marker_l) {

}

PMacroProcLexer::~PMacroProcLexer() {

}

std::unique_ptr<antlr4::Token> PMacroProcLexer::nextToken() {
    std::unique_ptr<antlr4::Token> ret = PSSLexer::nextToken();

    return ret;
}

}
}
