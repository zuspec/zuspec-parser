/*
 * TaskFindElementByLocation.cpp
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
#include "TaskFindElementByLocation.h"


namespace zsp {
namespace parser {


TaskFindElementByLocation::TaskFindElementByLocation(dmgr::IDebugMgr *dmgr) {
    DEBUG_INIT("TaskFindElementByLocation", dmgr);
}

TaskFindElementByLocation::~TaskFindElementByLocation() {

}

bool TaskFindElementByLocation::find(
        std::vector<ast::IScopeChild *>     &path,
        ast::ISymbolScope                   *root,
        int32_t                             lineno,
        int32_t                             linepos) {
    DEBUG_ENTER("find");
    m_found = false;
    path.clear();
    m_path = &path;
    m_lineno = lineno;
    m_linepos = linepos;

    root->accept(m_this);

    DEBUG_LEAVE("find (%d)", path.size());
    return m_found;
}

void TaskFindElementByLocation::visitExprId(ast::IExprId *i) {
    DEBUG_ENTER("visitExprId");
    DEBUG("%s: %d %d..%d", i->getId().c_str(), 
        i->getLocation().lineno, 
        i->getLocation().linepos,
        i->getLocation().linepos+i->getId().size()-1);
    if (i->getLocation().lineno == m_lineno &&
        m_linepos >= i->getLocation().linepos &&
        m_linepos < i->getLocation().linepos+i->getId().size()) {
        DEBUG("Found");
        m_found = true;
    }
    DEBUG_LEAVE("visitExprId");
}

void TaskFindElementByLocation::visitSymbolScope(ast::ISymbolScope *i) {
    bool push = (m_path->size() == 0 || m_path->back() != i);
    DEBUG_ENTER("visitSymbolScope");

    if (push) {
        m_path->push_back(i);
    }

    for (std::vector<ast::IScopeChild *>::const_iterator
            it=i->getChildren().begin();
            it!=i->getChildren().end(); it++) {
        (*it)->accept(this);
    }
    if (i->getTarget()) {
        i->getTarget()->accept(this);
    }
    if (i->getImports()) {
        i->getImports()->accept(this);
    }

    if (push && !m_found) {
        m_path->pop_back();
    }

    DEBUG_LEAVE("visitSymbolScope");
}

void TaskFindElementByLocation::visitTypeScope(ast::ITypeScope *i) {
    bool push = (m_path->size() == 0 || m_path->back() != i);
    DEBUG_ENTER("visitTypeScope");
    if (push) {
        m_path->push_back(i);
    }

    VisitorBase::visitTypeScope(i);

    if (push && !m_found) {
        m_path->pop_back();
    }

    DEBUG_LEAVE("visitTypeScope");
}

dmgr::IDebug *TaskFindElementByLocation::m_dbg = 0;

}
}
