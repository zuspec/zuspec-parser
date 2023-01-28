/**
 * AstSymbolTableIterator.h
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
#include <vector>
#include "dmgr/IDebugMgr.h"
#include "zsp/ast/IFactory.h"
#include "zsp/ast/ISymbolScope.h"
#include "zsp/parser/ISymbolTableIterator.h"

namespace zsp {
namespace parser {




class AstSymbolTableIterator : public virtual ISymbolTableIterator {
public:
    AstSymbolTableIterator(
        dmgr::IDebugMgr     *dmgr,
        ast::IFactory       *factory,
        ast::ISymbolScope   *root);

    AstSymbolTableIterator(const AstSymbolTableIterator &other);

    virtual ~AstSymbolTableIterator();

    virtual int32_t findLocalSymbol(const std::string &name) override;

    virtual ast::ISymbolRefPath *findLocalSymbolPath(const std::string &name) override;

    virtual ast::ISymbolRefPath *getScopeSymbolPath(int off=0) const override;

    virtual ast::ISymbolScope *getScope(int32_t off=0) const override;

    virtual ast::IScopeChild *getScopeChild(int32_t idx) const override;

    virtual ast::IScopeChild *resolveAbsPath(const ast::ISymbolRefPath *path) override;

    virtual int32_t pushNamedScope(const std::string &name) override;

    virtual void pushScope(ast::ISymbolScope *s) override;

    virtual void popScope() override;

    virtual bool hasScopes() override;

    virtual ISymbolTableIterator *clone() const override;

private:
    static dmgr::IDebug                     *m_dbg;
    ast::IFactory                           *m_factory;
    std::vector<ast::SymbolRefPathElem>     m_path;
    std::vector<ast::ISymbolScope *>        m_scope_s;

};

}
}


