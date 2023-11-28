/**
 * TaskIsPyRef.h
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

namespace zsp {
namespace parser {



class TaskIsPyRef : public ast::VisitorBase {
public:

    TaskIsPyRef(dmgr::IDebugMgr *dmgr) : m_dbg(0) {
        DEBUG_INIT("zsp::parser::TaskIsPyRef", dmgr);
    }

    virtual ~TaskIsPyRef() { }

    bool check(ast::IScopeChild *it) {
        DEBUG_ENTER("check");
        m_is_pyref = false;
        it->accept(m_this);
        DEBUG_LEAVE("check %d", m_is_pyref);
        return m_is_pyref;
    }

    virtual void visitPyImportStmt(ast::IPyImportStmt *i) override {
        DEBUG_ENTER("visitPyImportStmt");
        m_is_pyref = true;
        DEBUG_LEAVE("visitPyImportStmt");
    }

    virtual void visitPyImportFromStmt(ast::IPyImportFromStmt *i) override {
        DEBUG_ENTER("visitPyImportFromStmt");
        m_is_pyref = true;
        DEBUG_LEAVE("visitPyImportFromStmt");
    }

private:
    dmgr::IDebug            *m_dbg;
    bool                    m_is_pyref;
};

} /* namespace parser */
} /* namespace zsp */


