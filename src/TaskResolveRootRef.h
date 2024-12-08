/**
 * TaskResolveRootRef.h
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
#include "zsp/ast/impl/VisitorBase.h"
#include "zsp/parser/IFactory.h"
#include "TaskResolveBase.h"

namespace zsp {
namespace parser {



class TaskResolveRootRef : public TaskResolveBase {
public:
    TaskResolveRootRef(
        ResolveContext      *ctxt,
        bool                search_imp=true);

    virtual ~TaskResolveRootRef();

    ast::ISymbolRefPath *resolve(const ast::IExprId *id);

    virtual void visitProceduralStmtRepeat(ast::IProceduralStmtRepeat *i) override;

    virtual void visitRootSymbolScope(ast::IRootSymbolScope *i) override;

    virtual void visitSymbolScope(ast::ISymbolScope *i) override;

//    virtual void visitSymbolExecScope(ast::ISymbolExecScope *i) override;

    virtual void visitSymbolTypeScope(ast::ISymbolTypeScope *i) override;

    virtual void visitSymbolFunctionScope(ast::ISymbolFunctionScope *i) override;

private:

    ast::ISymbolRefPath *searchImports(
        const ast::IExprId          *id,
        ast::ISymbolImportSpec      *imp);

    ast::ISymbolRefPath *searchImport(
        const ast::IExprId          *id,
        ast::IPackageImportStmt     *imp);

private:
    static dmgr::IDebug             *m_dbg;
    bool                            m_search_imp;
    const ast::IExprId              *m_id;
    ast::ISymbolRefPath             *m_ref;
};

}
}


