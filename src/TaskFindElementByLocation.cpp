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
#include "zsp/parser/impl/TaskResolveSymbolPathRef.h"
#include "TaskFindElementByLocation.h"


namespace zsp {
namespace parser {

/**
 * 
 * 
 * @param dmgr 
 */

TaskFindElementByLocation::TaskFindElementByLocation(dmgr::IDebugMgr *dmgr) {
    m_dmgr = dmgr;
    DEBUG_INIT("TaskFindElementByLocation", dmgr);
}

TaskFindElementByLocation::~TaskFindElementByLocation() {

}

ITaskFindElementByLocation::Result TaskFindElementByLocation::find(
        ast::ISymbolScope                   *root,
        ast::IGlobalScope                   *file,
        int32_t                             lineno,
        int32_t                             linepos) {
    DEBUG_ENTER("find");
    m_root = root;
    m_file = file;
    m_lineno = lineno;
    m_linepos = linepos;

    m_result = {false, false, 0, ""};

    root->accept(m_this);

    DEBUG_LEAVE("find (%d)", m_result.isValid);
    return m_result;
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

        // Now, must determine what we're looking at
        if (m_ctxt_s.back().expr) {
            DEBUG("Upper is an expression");
            if (dynamic_cast<ast::ITypeIdentifier *>(m_ctxt_s.back().expr)) {
                ast::ITypeIdentifier *t = dynamic_cast<ast::ITypeIdentifier *>(m_ctxt_s.back().expr);
                if (i == t->getElems().back().get()->getId()) {
                    // We're pointing at the last element of a path
                    DEBUG("Last Element");
                    m_result.isValid = true;
                    ast::IScopeChild *target = TaskResolveSymbolPathRef(
                        m_dmgr, m_root).resolve(t->getTarget());
                    if (dynamic_cast<ast::ISymbolScope *>(target)) {
                        m_result.target = dynamic_cast<ast::ISymbolScope *>(target)->getTarget();
                    } else {
                        m_result.target = target;
                    }
                    m_result.isType = true;
                    m_result.docComment = m_result.target->getDocstring();
                } else {
                    DEBUG("Not-last Element");
                }
            }
        } else {
            if (dynamic_cast<ast::ITypeScope *>(m_ctxt_s.back().child)) {
                ast::ITypeScope *t = dynamic_cast<ast::ITypeScope *>(m_ctxt_s.back().child);
                DEBUG("Upper is a type declaration (%s)", t->getName()->getId().c_str());
                m_result.isType = true;
                m_result.docComment = t->getDocstring();
                m_result.target = t;
            } else if (dynamic_cast<ast::IField *>(m_ctxt_s.back().child)) {
                ast::IField *t = dynamic_cast<ast::IField *>(m_ctxt_s.back().child);
                DEBUG("Upper is a field (%s)", t->getName()->getId().c_str());
                m_result.isType = false;
                m_result.docComment = t->getDocstring();
                m_result.target = t;
            }
            m_result.isValid = true;
        }
    }
    DEBUG_LEAVE("visitExprId");
}

void TaskFindElementByLocation::visitField(ast::IField *i) {
    DEBUG_ENTER("visitField");
    m_ctxt_s.push_back({0, i});
    VisitorBase::visitField(i);
    m_ctxt_s.pop_back();
    DEBUG_LEAVE("visitField");
}

void TaskFindElementByLocation::visitSymbolScope(ast::ISymbolScope *i) {
    bool push = (m_ctxt_s.size() == 0 || m_ctxt_s.back().child != i);
    DEBUG_ENTER("visitSymbolScope");

    if (push) {
        m_ctxt_s.push_back({0, i});
    }

    for (std::vector<ast::IScopeChildUP>::const_iterator
            it=i->getChildren().begin();
            it!=i->getChildren().end(); it++) {
        it->get()->accept(this);
    }
    if (i->getTarget()) {
        i->getTarget()->accept(this);
    }
    if (i->getImports()) {
        i->getImports()->accept(this);
    }

    if (push && !m_result.isValid) {
        m_ctxt_s.pop_back();
    }

    DEBUG_LEAVE("visitSymbolScope");
}

void TaskFindElementByLocation::visitTypeIdentifier(ast::ITypeIdentifier *i) {
    DEBUG_ENTER("visitTypeIdentifier");
    m_ctxt_s.push_back({i, 0});
    VisitorBase::visitTypeIdentifier(i);
    m_ctxt_s.pop_back();
    DEBUG_LEAVE("visitTypeIdentifier");
}

void TaskFindElementByLocation::visitTypeScope(ast::ITypeScope *i) {
    bool push = (m_ctxt_s.size() == 0 || m_ctxt_s.back().child != i);
    DEBUG_ENTER("visitTypeScope");
    if (push) {
        m_ctxt_s.push_back({0, i});
    }

    VisitorBase::visitTypeScope(i);

    if (push && !m_result.isValid) {
        m_ctxt_s.pop_back();
    }

    DEBUG_LEAVE("visitTypeScope");
}

dmgr::IDebug *TaskFindElementByLocation::m_dbg = 0;

}
}
