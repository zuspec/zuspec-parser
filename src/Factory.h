/**
 * Factory.h
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
#include "zsp/IFactory.h"
#include "zsp/ast/IFactory.h"
#include "zsp/ISymbolTable.h"
#include "zsp/ast/IFactory.h"

namespace zsp {



class Factory : public virtual IFactory {
public:
    Factory(ast::IFactory *ast_factory);

    virtual ~Factory();

    virtual ast::IFactory *getAstFactory() override;

    virtual IAstBuilder *mkAstBuilder(IMarkerListener *marker_l) override;

    virtual INameResolver *mkNameResolver(
        ISymbolTable            *symtab,
        IMarkerListener         *marker_l) override;

    virtual ISymbolTable *mkSymbolTable() override;

private:
    ast::IFactory                       *m_ast_factory;

};

}


