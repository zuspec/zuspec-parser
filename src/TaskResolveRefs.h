/**
 * TaskResolveRefs.h
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
#pragma once
#include "dmgr/IDebugMgr.h"
#include "zsp/parser/IFactory.h"
#include "zsp/parser/IMarkerListener.h"
#include "zsp/ast/ISymbolScope.h"
#include "zsp/ast/impl/VisitorBase.h"

namespace zsp {
namespace parser {



class TaskResolveRefs : public ast::VisitorBase {
public:
    TaskResolveRefs(
        dmgr::IDebugMgr     *dmgr,
        IFactory            *factory,
        IMarkerListener     *marker_l);

    virtual ~TaskResolveRefs();

    void resolve(ast::ISymbolScope *root);

    virtual void visitExprRefPathContext(ast::IExprRefPathContext *i) override;

    virtual void visitExprRefPathId(ast::IExprRefPathId *i) override;

    virtual void visitExprRefPathStaticRooted(ast::IExprRefPathStaticRooted *i) override;

    virtual void visitSymbolScope(ast::ISymbolScope *i) override;

    virtual void visitSymbolExtendScope(ast::ISymbolExtendScope *i) override;

    virtual void visitSymbolExecScope(ast::ISymbolExecScope *i) override;

    virtual void visitSymbolFunctionScope(ast::ISymbolFunctionScope *i) override;

    virtual void visitSymbolTypeScope(ast::ISymbolTypeScope *i) override;

    virtual void visitDataTypeUserDefined(ast::IDataTypeUserDefined *i) override;
    
    virtual void visitTypeIdentifier(ast::ITypeIdentifier *i) override;

    virtual void visitStruct(ast::IStruct *i) override;

private:
    static dmgr::IDebug     *m_dbg;
    dmgr::IDebugMgr         *m_dmgr;
    IFactory                *m_factory;
    IMarkerListener         *m_marker_l;
    ISymbolTableIteratorUP  m_symtab_it;

};

}
}


