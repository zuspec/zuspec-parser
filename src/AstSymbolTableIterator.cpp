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
#include "dmgr/impl/DebugMacros.h"
#include "AstSymbolTableIterator.h"

namespace zsp {
namespace parser {



AstSymbolTableIterator::AstSymbolTableIterator(
    dmgr::IDebugMgr         *dmgr,
    ast::IFactory           *factory,
    ast::ISymbolScope       *root) : m_factory(factory) {
    m_scope_s.push_back(root);
    DEBUG_INIT("AstSymbolTableIterator", dmgr);
}

AstSymbolTableIterator::AstSymbolTableIterator(
    const AstSymbolTableIterator &other) : 
    m_factory(other.m_factory),
    m_path(other.m_path.begin(), other.m_path.end()),
    m_scope_s(other.m_scope_s.begin(), other.m_scope_s.end()) {

    if (m_scope_s.size() == 0) {
        fprintf(stdout, "Error: initial scope-stack size is 0\n");
    }

}

AstSymbolTableIterator::~AstSymbolTableIterator() {

}

int32_t AstSymbolTableIterator::findLocalSymbol(const std::string &name) {
    DEBUG_ENTER("findLocalSymbol %s", name.c_str());
    std::map<std::string,int32_t>::const_iterator it =
        m_scope_s.back()->getSymtab().find(name);

    if (it != m_scope_s.back()->getSymtab().end()) {
        DEBUG_LEAVE("findLocalSymbol %s - success", name.c_str());
        return it->second;
    } else {
        DEBUG_LEAVE("findLocalSymbol %s - fail", name.c_str());
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
        ret->getPath().push_back({ast::SymbolRefPathElemKind::ElemKind_ChildIdx, idx});
        return ret;
    } else {
        return 0;
    }
}

ast::ISymbolRefPath *AstSymbolTableIterator::getScopeSymbolPath(int32_t off) const {
    ast::ISymbolRefPath *ret = m_factory->mkSymbolRefPath();

    for (int32_t i=0; i<(m_path.size()-off); i++) {
        ret->getPath().push_back(m_path.at(i));
    }

    return ret;
}

ast::ISymbolScope *AstSymbolTableIterator::getScope(int32_t off) const {
    return m_scope_s.at(m_scope_s.size()-off-1);
}

ast::IScopeChild *AstSymbolTableIterator::getScopeChild(int32_t idx) const {
    return m_scope_s.back()->getChildren().at(idx);
}

ast::IScopeChild *AstSymbolTableIterator::resolveAbsPath(const ast::ISymbolRefPath *path) {
    ast::IScopeChild *ret = 0;

    ast::ISymbolScope *scope = m_scope_s.at(0);
    for (uint32_t i=0; i<path->getPath().size(); i++) {
        DEBUG("Scope: %s @ %d", scope->getName().c_str(), path->getPath().at(i));
        const ast::SymbolRefPathElem &elem = path->getPath().at(i);
        ast::IScopeChild *next = scope->getChildren().at(elem.idx);

        if (i+1 < path->getPath().size()) {
            if (!(scope=dynamic_cast<ast::ISymbolScope *>(next))) {
                fprintf(stdout, "i=%d size=%d and target isn't a symbol scope (next=%p)\n",
                    i, path->getPath().size(), next);
                break;
            }
        } else {
            ret = next;
        }
    }

    return ret;
}

int32_t AstSymbolTableIterator::pushNamedScope(const std::string &name) {
    DEBUG_ENTER("pushNamedScope %s", name.c_str());
    std::map<std::string,int32_t>::const_iterator it =
        m_scope_s.back()->getSymtab().find(name);

    if (it != m_scope_s.back()->getSymtab().end()) {
        ast::ISymbolScope *scope = dynamic_cast<ast::ISymbolScope *>(
            m_scope_s.back()->getChildren().at(it->second));
        if (scope) {
            m_scope_s.push_back(scope);
            m_path.push_back({ast::SymbolRefPathElemKind::ElemKind_ChildIdx, it->second});
            DEBUG_LEAVE("pushNamedScope %s - success sz=%d", 
                name.c_str(), m_scope_s.size());
            return it->second;
        } else {
            DEBUG_LEAVE("pushNamedScope %s - fail", name.c_str());
            return -1;
        }
    } else {
        DEBUG_LEAVE("pushNamedScope %s - fail", name.c_str());
        return -1;
    }
}

void AstSymbolTableIterator::pushScope(
        ast::ISymbolScope           *s,
        ast::SymbolRefPathElemKind  kind) {
    m_scope_s.push_back(s);
    m_path.push_back({kind, s->getId()});
}

void AstSymbolTableIterator::popScope() {
    DEBUG_ENTER("popScope %d", m_scope_s.size());
    if (m_scope_s.size() > 0) {
        m_scope_s.pop_back();
        m_path.pop_back();
        /*
        if (m_scope_s.size() == 0) {
            FATAL("emptied scope stack");
        }
         */
    } else {
        FATAL("attempt to pop an empty stack");
    }
    DEBUG_LEAVE("popScope - sz=%d", m_scope_s.size());
}

bool AstSymbolTableIterator::hasScopes() {
    return m_scope_s.size() > 0;
}

ISymbolTableIterator *AstSymbolTableIterator::clone() const {
    return new AstSymbolTableIterator(*this);
}

dmgr::IDebug *AstSymbolTableIterator::m_dbg = 0;

}
}
