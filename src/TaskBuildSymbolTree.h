/**
 * TaskBuildSymbolTree.h
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
#include "zsp/parser/IMarkerListener.h"
#include "zsp/ast/IFactory.h"
#include "zsp/ast/impl/VisitorBase.h"

namespace zsp {
namespace parser {




class TaskBuildSymbolTree : public virtual ast::VisitorBase {
public:
    TaskBuildSymbolTree(
        dmgr::IDebugMgr         *dmgr,
        ast::IFactory           *factory,
        IMarkerListener         *marker_l
    );

    virtual ~TaskBuildSymbolTree();

    ast::ISymbolScope *build(
        const std::vector<ast::IGlobalScope *>  &roots);

    virtual void visitPackageScope(ast::IPackageScope *i) override;

    virtual void visitEnumDecl(ast::IEnumDecl *i) override;

    virtual void visitEnumItem(ast::IEnumItem *i) override;

    virtual void visitExecStmt(ast::IExecStmt *i) override;

    virtual void visitExtendType(ast::IExtendType *i) override;

    virtual void visitFunctionDefinition(ast::IFunctionDefinition *i) override;

    virtual void visitFunctionImportProto(ast::IFunctionImportProto *i) override;

    virtual void visitFunctionImportType(ast::IFunctionImportType *i) override;

    virtual void visitFunctionPrototype(ast::IFunctionPrototype *i) override;

    virtual void visitPackageImportStmt(ast::IPackageImportStmt *i) override;

    virtual void visitScopeChild(ast::IScopeChild *i) override;

    virtual void visitTypeScope(ast::ITypeScope *i) override;;



protected:

    void reportDuplicateSymbol(
        ast::ISymbolScope       *scope,
        ast::IScopeChild        *orig,
        ast::IScopeChild        *dup);

    ast::IScopeChild *findSymbol(const std::string &name);

private:
    static dmgr::IDebug                 *m_dbg;
    ast::IFactory                       *m_factory;
    IMarkerListener                     *m_marker_l;
    std::vector<ast::ISymbolScope *>     m_scope_s;

};

}
}


