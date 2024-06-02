/*
 * TaskApplyOverlay.cpp
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
#include "dmgr/impl/DebugMacros.h"
#include "zsp/ast/ISymbolScope.h"
#include "TaskApplyOverlay.h"


namespace zsp {
namespace parser {


TaskApplyOverlay::TaskApplyOverlay(dmgr::IDebugMgr *dmgr) {
    DEBUG_INIT("zsp::parser::TaskApplyOverlay", dmgr);
}

TaskApplyOverlay::~TaskApplyOverlay() {

}

void TaskApplyOverlay::apply(
        ast::IRootSymbolScope                   *root,
        ast::IGlobalScope                       *overlay) {
    DEBUG_ENTER("apply");

    // Go through each overlay file, patching its content
    // in and resolving its symbols against itself and
    // the base AST

    m_scope_s.clear();
    m_scope_s.push_back(root);
    for (std::vector<ast::IScopeChildUP>::const_iterator
        it=overlay->getChildren().begin();
        it!=overlay->getChildren().end(); it++) {
        (*it)->accept(m_this);
    }
    m_scope_s.pop_back();
    DEBUG_LEAVE("apply");
}

void TaskApplyOverlay::visitNamedScopeChild(ast::INamedScopeChild *i) {
    DEBUG_ENTER("visitNamedScopeChild %s", i->getName()->getId().c_str());
    ast::ISymbolScope *scope = m_scope_s.back();

    std::unordered_map<std::string,int32_t>::iterator ex_it;
    ex_it = scope->getSymtab().find(i->getName()->getId());

    int32_t i_id = scope->getChildren().size();
    scope->getChildren().push_back(ast::IScopeChildUP(i, false));

    if (ex_it != scope->getSymtab().end()) {
        // Need to add remove the existing entry
        DEBUG("Already exists in the symtab ; removing existing mapping");
        scope->getSymtab().erase(ex_it);
    }
    scope->getSymtab().insert({i->getName()->getId(), i_id});

    DEBUG_LEAVE("visitNamedScopeChild %s", i->getName()->getId().c_str());
}

void TaskApplyOverlay::visitPackageScope(ast::IPackageScope *i) {
    DEBUG_ENTER("visitPackageScope");
    // Lookup the matching SymbolScope
    ast::ISymbolScope *scope = m_scope_s.back();
    for (std::vector<ast::IExprIdUP>::const_iterator
        it=i->getId().begin();
        it!=i->getId().end(); it++) {
        std::unordered_map<std::string,int32_t>::const_iterator s_it;
        s_it = scope->getSymtab().find((*it)->getId());

        if (s_it == scope->getSymtab().end()) {
            // This means that this package doesn't exist in the base AST
            ERROR("TODO: handle new-package case");
        } else {
            scope = dynamic_cast<ast::ISymbolScope *>(scope->getChildren().at(s_it->second).get());
        }
    }

    m_scope_s.push_back(scope);
    for (std::vector<ast::IScopeChildUP>::const_iterator 
        it=scope->getChildren().begin();
        it!=scope->getChildren().end(); it++) {
        (*it)->accept(m_this);
    }
    m_scope_s.pop_back();

    DEBUG_LEAVE("visitPackageScope");
}

void TaskApplyOverlay::visitTypeScope(ast::ITypeScope *i) {
    DEBUG_ENTER("visitTypeScope");
    ast::ISymbolScope *scope = m_scope_s.back();

    std::unordered_map<std::string,int32_t>::const_iterator it_i;
    it_i = scope->getSymtab().find(i->getName()->getId());

    ast::ISymbolScope *scope_i = dynamic_cast<ast::ISymbolScope *>(
        scope->getChildren().at(it_i->second).get());
    
    // Update the target this the symbol scope points to
    scope_i->setTarget(i);

    m_scope_s.push_back(scope_i);
    for (std::vector<ast::IScopeChildUP>::const_iterator
        it=i->getChildren().begin();
        it!=i->getChildren().end(); it++) {
        (*it)->accept(m_this);
    }
    m_scope_s.pop_back();

    DEBUG_LEAVE("visitTypeScope");
}

dmgr::IDebug *TaskApplyOverlay::m_dbg = 0;

}
}