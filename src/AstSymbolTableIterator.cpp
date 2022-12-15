/*
 * AstSymbolTableIterator.cpp
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
#include "AstSymbolTableIterator.h"


namespace zsp {


AstSymbolTableIterator::AstSymbolTableIterator(ast::ISymbolScope *root) {
    m_scope_s.push_back(root);
}

AstSymbolTableIterator::AstSymbolTableIterator(
    const AstSymbolTableIterator &other) : 
    m_scope_s(other.m_scope_s.begin(), other.m_scope_s.end()) {

}

AstSymbolTableIterator::~AstSymbolTableIterator() {

}

bool AstSymbolTableIterator::pushNamedScope(const std::string &name) {
    std::map<std::string,int32_t>::const_iterator it =
        m_scope_s.back()->getSymtab().find(name);

    if (it != m_scope_s.back()->getSymtab().end()) {
        m_scope_s.push_back(dynamic_cast<ast::ISymbolScope *>(
            m_scope_s.back()->getChildren().at(it->second)));
        return true;
    } else {
        return false;
    }
}

void AstSymbolTableIterator::popScope() {
    if (m_scope_s.size() > 0) {
        m_scope_s.pop_back();
    } else {
        fprintf(stdout, "Error: attempt to pop an empty stack\n");
    }
}

bool AstSymbolTableIterator::hasScopes() {
    return m_scope_s.size() > 1;
}

ISymbolTableIterator *AstSymbolTableIterator::clone() {
    return new AstSymbolTableIterator(*this);
}


}
