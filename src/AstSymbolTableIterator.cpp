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


AstSymbolTableIterator::AstSymbolTableIterator(
    ast::IFactory           *factory,
    ast::ISymbolScope       *root) : m_factory(factory) {
    m_scope_s.push_back(root);
}

AstSymbolTableIterator::AstSymbolTableIterator(
    const AstSymbolTableIterator &other) : 
    m_factory(other.m_factory),
    m_path(other.m_path.begin(), other.m_path.end()),
    m_scope_s(other.m_scope_s.begin(), other.m_scope_s.end()) {

}

AstSymbolTableIterator::~AstSymbolTableIterator() {

}

int32_t AstSymbolTableIterator::findLocalSymbol(const std::string &name) {
    std::map<std::string,int32_t>::const_iterator it =
        m_scope_s.back()->getSymtab().find(name);

    if (it != m_scope_s.back()->getSymtab().end()) {
        return it->second;
    } else {
        return -1;
    }
}

ast::ISymbolRefPath *AstSymbolTableIterator::findLocalSymbolPath(const std::string &name) {
    int32_t idx = findLocalSymbol(name);

    if (idx != -1) {
        ast::ISymbolRefPath *ret = m_factory->mkSymbolRefPath();
        ret->getPath().insert(
            ret->getPath().begin(), 
            m_path.begin(), 
            m_path.end());
        return ret;
    } else {
        return 0;
    }
}

ast::ISymbolScope *AstSymbolTableIterator::getScope() const {
    return m_scope_s.back();
}

ast::IScopeChild *AstSymbolTableIterator::getScopeChild(int32_t idx) const {
    return m_scope_s.back()->getChildren().at(idx);
}

ast::IScopeChild *AstSymbolTableIterator::resolveAbsPath(const ast::ISymbolRefPath *path) {
    ast::IScopeChild *ret = 0;

    ast::ISymbolScope *scope = m_scope_s.at(0);
    for (uint32_t i=0; i<path->getPath().size(); i++) {
        ast::IScopeChild *next = scope->getChildren().at(path->getPath().at(i));

        if (i+1 < path->getPath().size()) {
            if (!(scope=dynamic_cast<ast::ISymbolScope *>(next))) {
                break;
            }
        } else {
            ret = next;
        }
    }

    return ret;
}

int32_t AstSymbolTableIterator::pushNamedScope(const std::string &name) {
    std::map<std::string,int32_t>::const_iterator it =
        m_scope_s.back()->getSymtab().find(name);

    if (it != m_scope_s.back()->getSymtab().end()) {
        ast::ISymbolScope *scope = dynamic_cast<ast::ISymbolScope *>(
            m_scope_s.back()->getChildren().at(it->second));
        if (scope) {
            m_scope_s.push_back(scope);
            return it->second;
        } else {
            return -1;
        }
    } else {
        return -1;
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
    return m_scope_s.size() > 0;
}

ISymbolTableIterator *AstSymbolTableIterator::clone() const {
    return new AstSymbolTableIterator(*this);
}


}
