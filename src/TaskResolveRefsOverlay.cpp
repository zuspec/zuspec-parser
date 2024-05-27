/*
 * TaskResolveRefsOverlay.cpp
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
#include "TaskResolveRefsOverlay.h"


namespace zsp {
namespace parser {


TaskResolveRefsOverlay::TaskResolveRefsOverlay(ResolveContext *ctxt) : 
    m_ctxt(ctxt) {
    DEBUG_INIT("zsp::parser::TaskResolveRefsOverlay", ctxt->getDebugMgr());
}

TaskResolveRefsOverlay::~TaskResolveRefsOverlay() {

}

void TaskResolveRefsOverlay::resolve(ast::IGlobalScope * overlay) {
    DEBUG_ENTER("resolve");

    m_scope_s.clear();
    m_ctxt->pushSymtab(m_ctxt->getFactory()->mkAstSymbolTableIterator(
        m_ctxt->root()));
    m_scope_s.push_back(m_ctxt->root());
    for (std::vector<ast::IScopeChildUP>::const_iterator
        it=overlay->getChildren().begin();
        it!=overlay->getChildren().end(); it++) {
        (*it)->accept(m_this);
    }
    m_scope_s.pop_back();

    DEBUG_LEAVE("resolve");
}

void TaskResolveRefsOverlay::visitTypeIdentifier(ast::ITypeIdentifier *i) {
    DEBUG_ENTER("visitTypeIdentifier");

    // TODO: 
    DEBUG_LEAVE("visitTypeIdentifier");
}

void TaskResolveRefsOverlay::visitPackageScope(ast::IPackageScope *i) {
    DEBUG_ENTER("visitPackageScope");
    // TODO: push symbol scopes

    for (std::vector<ast::IScopeChildUP>::const_iterator
        it=i->getChildren().begin();
        it!=i->getChildren().end(); it++) {
        (*it)->accept(m_this);
    }

    // TODO: pop symbol scopes

    DEBUG_LEAVE("visitPackageScope");
}

void TaskResolveRefsOverlay::visitTypeScope(ast::ITypeScope *i) {
    DEBUG_ENTER("visitTypeScope");
    // TODO: push symbol scope


    DEBUG_LEAVE("visitTypeScope");
}

dmgr::IDebug *TaskResolveRefsOverlay::m_dbg = 0;

}
}
