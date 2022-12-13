/*
 * Factory.cpp
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
#include "Factory.h"
#include "AstBuilder.h"
#include "AstSymbolTable.h"
#include "NameResolver.h"


namespace zsp {


Factory::Factory(ast::IFactory *ast_factory) : m_ast_factory(ast_factory) {

}

Factory::~Factory() {

}

ast::IFactory *Factory::getAstFactory() {

}

IAstBuilder *Factory::mkAstBuilder(IMarkerListener *marker_l) {
    return new AstBuilder(m_ast_factory, marker_l);
}

INameResolver *Factory::mkNameResolver(
        ISymbolTable            *symtab,
        IMarkerListener         *marker_l) {
    return new NameResolver(symtab, marker_l);
}

ISymbolTable *Factory::mkSymbolTable() {
    return new AstSymbolTable();
//    return 0;
}

}
