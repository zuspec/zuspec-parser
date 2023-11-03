/**
 * TaskGetElemSymbolScope.h
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
#include "TaskResolveSymbolPathRef.h"

namespace zsp {
namespace parser {

class TaskGetElemSymbolScope : public virtual ast::VisitorBase {
public:
    TaskGetElemSymbolScope(
        dmgr::IDebugMgr         *dmgr,
        ast::ISymbolScope       *root) : 
        m_dbg(0), m_path_resolver(dmgr, root) {
        DEBUG_INIT("zsp::parser::TaskGetElemSymbolScope", dmgr);
    }

    virtual ~TaskGetElemSymbolScope() { }

    ast::ISymbolScope *resolve(ast::IScopeChild *c) {
        m_ret = 0;
        c->accept(m_this);
        return m_ret;
    }
    
    virtual void visitField(ast::IField *i) override {
        DEBUG_ENTER("visitField %s", i->getName()->getId().c_str());
        i->getType()->accept(m_this);
        DEBUG_LEAVE("visitField %s", i->getName()->getId().c_str());
    }

    virtual void visitDataTypeUserDefined(ast::IDataTypeUserDefined *i) override {
        DEBUG_ENTER("visitDataTypeUserDefined");
        ast::IScopeChild *c = m_path_resolver.resolve(i->getType_id()->getTarget());
        m_ret = dynamic_cast<ast::ISymbolScope *>(c);
        DEBUG_LEAVE("visitDataTypeUserDefined");
    }

    virtual void visitTypeIdentifier(ast::ITypeIdentifier *i) override {
        DEBUG_ENTER("visitTypeIdentifier");
        ast::IScopeChild *c = m_path_resolver.resolve(i->getTarget());
        m_ret = dynamic_cast<ast::ISymbolScope *>(c);
        DEBUG_LEAVE("visitTypeIdentifier");
    }

protected:
    dmgr::IDebug                *m_dbg;
    TaskResolveSymbolPathRef    m_path_resolver;
    ast::ISymbolScope           *m_ret;

};

}
}


