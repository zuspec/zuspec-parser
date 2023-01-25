/**
 * TaskResolveRef.h
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
#include "zsp/parser/ISymbolTableIterator.h"
#include "zsp/ast/impl/VisitorBase.h"

namespace zsp {
namespace parser {


class TaskResolveRef : public ast::VisitorBase {
public:
    TaskResolveRef(
        IFactory            *factory,
        IMarkerListener     *marker_l);

    virtual ~TaskResolveRef();

    ast::ISymbolRefPath *resolve(
        const ISymbolTableIterator      *scope,
        ast::ITypeIdentifier            *type_id);

    ast::ISymbolRefPath *resolve(
        const ISymbolTableIterator      *scope,
        ast::IExprRefPath               *ref);

    ast::ISymbolRefPath *resolve(
        const ISymbolTableIterator      *scope,
        ast::IExprId                    *ref);

    virtual void visitExprRefPathStaticRooted(ast::IExprRefPathStaticRooted *i) override;

    virtual void visitExprRefPathId(ast::IExprRefPathId *i) override;

    virtual void visitExprRefPathContext(ast::IExprRefPathContext *i) override;

    virtual void visitExprRefPathStatic(ast::IExprRefPathStatic *i) override;

private:
    ast::ISymbolRefPath *searchImport(
        ISymbolTableIterator            *scope,
        ast::IPackageImportStmt         *imp,
        const std::string               &sym);

private:
    static dmgr::IDebug                 *m_dbg;
    const ISymbolTableIterator          *m_scope;
    IFactory                            *m_factory;
    IMarkerListener                     *m_marker_l;    
    ast::ISymbolRefPath                 *m_ref;

};

}
}


