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
#include "AstLinker.h"
#include "AstSymbolTable.h"
#include "AstSymbolTableIterator.h"
#include "Marker.h"
#include "MarkerCollector.h"
#include "NameResolver.h"


namespace zsp {
namespace parser {


Factory::Factory() : m_dmgr(0), m_ast_factory(0) {

}

Factory::Factory(ast::IFactory *ast_factory) : m_ast_factory(ast_factory) {

}

Factory::~Factory() {

}

void Factory::init(
    dmgr::IDebugMgr     *dmgr,
    ast::IFactory       *ast_factory) {
    m_dmgr = dmgr;
    m_ast_factory = ast_factory;
}

ast::IFactory *Factory::getAstFactory() {
    return m_ast_factory;
}

IAstBuilder *Factory::mkAstBuilder(IMarkerListener *marker_l) {
    return new AstBuilder(m_dmgr, m_ast_factory, marker_l);
}

ILinker *Factory::mkAstLinker() {
    return new AstLinker(m_dmgr, this);
}

ISymbolTableIterator *Factory::mkAstSymbolTableIterator(
        ast::ISymbolScope       *root) {
    return new AstSymbolTableIterator(m_dmgr, m_ast_factory, root);
}

IMarker *Factory::mkMarker(
        const std::string           &msg,
        MarkerSeverityE             severity,
        const ast::Location         &loc) {
    return new Marker(msg, severity, loc);
}

IMarkerCollector *Factory::mkMarkerCollector() {
    return new MarkerCollector();
}

INameResolver *Factory::mkNameResolver(
        ISymbolTable            *symtab,
        IMarkerListener         *marker_l) {
    return new NameResolver(this, marker_l);
}

ISymbolTable *Factory::mkSymbolTable() {
    return new AstSymbolTable(m_dmgr);
//    return 0;
}

IFactory *Factory::inst() {
    if (!m_inst) {
        m_inst = FactoryUP(new Factory());
    }
    return m_inst.get();
}

extern "C" IFactory *getZuspecParserFactory() {
    return Factory::inst();
}

extern "C" IFactory *zsp_parser_getFactory() {
    return Factory::inst();
}

FactoryUP Factory::m_inst;

}
}
