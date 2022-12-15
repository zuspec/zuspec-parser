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
#include "zsp/ast/ISymbolScope.h"
#include "zsp/ISymbolTableIterator.h"

namespace zsp {



class AstSymbolTableIterator : public virtual ISymbolTableIterator {
public:
    AstSymbolTableIterator(ast::ISymbolScope *root);

    AstSymbolTableIterator(const AstSymbolTableIterator &other);

    virtual ~AstSymbolTableIterator();

    virtual bool pushNamedScope(const std::string &name) override;

    virtual void popScope() override;

    virtual bool hasScopes() override;

    virtual ISymbolTableIterator *clone() override;

private:
    std::vector<ast::ISymbolScope *>        m_scope_s;

};

}


