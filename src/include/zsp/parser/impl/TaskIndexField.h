/**
 * TaskIndexField.h
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
#include "dmgr/IDebugMgr.h"
#include "dmgr/impl/DebugMacros.h"
#include "zsp/ast/impl/VisitorBase.h"
#include "zsp/parser/impl/TaskResolveSymbolPathRef.h"

namespace zsp {
namespace parser {



class TaskIndexField : ast::VisitorBase {
public:

    TaskIndexField(
        dmgr::IDebugMgr     *dmgr,
        ast::ISymbolScope   *root_scope) : 
        m_dmgr(dmgr), m_dbg(0), m_root_scope(root_scope) {
        DEBUG_INIT("zsp::parser::TaskIndexField", dmgr);
    }

    virtual ~TaskIndexField() { }

    ast::IScopeChild *index(ast::IScopeChild *root, int32_t index) {
        DEBUG_ENTER("index %d", index);
        m_index = index;
        m_ret = 0;

        root->accept(m_this);

        DEBUG_LEAVE("index => %p", m_ret);
        return m_ret;
    }

    virtual void visitFieldCompRef(ast::IFieldCompRef *i) override { 
        DEBUG_ENTER("visitFieldCompRef");
        i->getType()->accept(m_this);
        DEBUG_LEAVE("visitFieldCompRef");
    }

    virtual void visitDataTypeUserDefined(ast::IDataTypeUserDefined *i) override {
        DEBUG_ENTER("visitDataTypeUserDefined");
        ast::IScopeChild *target = TaskResolveSymbolPathRef(
            m_dmgr, m_root_scope).resolve(
                i->getType_id()->getTarget());
        target->accept(m_this);
        DEBUG_LEAVE("visitDataTypeUserDefined");
    }

    virtual void visitSymbolRefPath(ast::ISymbolRefPath *i) override {
        DEBUG_ENTER("visitSymbolRefPath");
        DEBUG_LEAVE("visitSymbolRefPath");
    }

    virtual void visitSymbolScope(ast::ISymbolScope *i) override {
        DEBUG_ENTER("visitSymbolScope");
        m_ret = i->getChildren().at(m_index);
        DEBUG_LEAVE("visitSymbolScope");
    }

    virtual void visitSymbolTypeScope(ast::ISymbolTypeScope *i) override {
        DEBUG_ENTER("visitSymbolTypeScope");
        m_ret = i->getChildren().at(m_index);
        DEBUG_LEAVE("visitSymbolTypeScope");
    }

protected:
    dmgr::IDebugMgr                     *m_dmgr;
    dmgr::IDebug                        *m_dbg;
    ast::ISymbolScope                   *m_root_scope;
    int32_t                             m_index;
    ast::IScopeChild                    *m_ret;

};

} /* namespace parser */
} /* namespace zsp */


