/*
 * SymbolScope.cpp
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
#include "SymbolScope.h"
#include "zsp/ast/INamedScopeChild.h"
#include "zsp/ast/IExprId.h"


namespace zsp {
namespace parser {

SymbolScope::SymbolScope(
    const std::string           &name,
    SymbolScopeKind             kind) : m_name(name), m_kind(kind) {
    m_parent = 0;
}

SymbolScope::~SymbolScope() {

}

std::string SymbolScope::getFullName() {
    std::string ret = m_name;

    ISymbolScope *p = getParent();
    while (p) {
        ret.insert(0, "::");
        ret.insert(0, p->getName());
        p = p->getParent();
    }

    return ret;
}

void SymbolScope::addDeclScope(zsp::ast::IScopeChild *scope) {
    m_decl_scopes.push_back(scope);
}

bool SymbolScope::addSubscope(ISymbolScope *scope) {
    if (m_symtab.find(scope->getName()) != m_symtab.end()) {
        ResolveResult res;
        res.is_terminal=false;
        res.scope = scope;
        m_subscopes.push_back(ISymbolScopeUP(scope));
        m_symtab.insert({scope->getName(), res});
        return true;
    } else {
        return false;
    }
}

bool SymbolScope::addTerminal(ast::INamedScopeChild *terminal) {
    if (m_symtab.find(terminal->getName()->getId()) != m_symtab.end()) {
        ResolveResult res;
        res.is_terminal=true;
        res.terminal = terminal;

        m_symtab.insert({terminal->getName()->getId(), res});
        m_terminals.push_back(terminal);
    }
}

bool SymbolScope::resolve(
        const std::string       &name,
        ResolveResult           &result) {
    std::unordered_map<std::string,ResolveResult>::const_iterator it;

    if ((it=m_symtab.find(name)) != m_symtab.end()) {
        result = it->second;
        return true;
    } else {
        return false;
    }
}

}
}

