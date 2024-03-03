/**
 * PMacroProcLexer.h
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
#pragma once
#include "antlr4-runtime.h"
#include "zsp/parser/IMarkerListener.h"
#include "PSSLexer.h"

namespace zsp {
namespace parser {



class PMacroProcLexer : public PSSLexer {
public:
    PMacroProcLexer(
        antlr4::ANTLRInputStream        *input,
        int32_t                         fileid,
        IMarkerListener                 *marker_l);

    virtual ~PMacroProcLexer();

    virtual std::unique_ptr<antlr4::Token> nextToken() override;

protected:
    class LexerData {
    public:
        LexerData(const std::string &content) :
            m_strstream(content), m_antlrstream(m_strstream) { }

        std::istringstream          m_strstream;
        antlr4::ANTLRInputStream    m_antlrstream;
    };

protected:
    IMarkerListener                             *m_marker_l;
    int32_t                                     m_fileid;
    std::vector<std::unique_ptr<PSSLexer>>      m_lexer_s;
    std::vector<std::unique_ptr<LexerData>>     m_lexdat_s;


};

}
}


