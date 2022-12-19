/*
 * TaskApplyTypeExtensions.cpp
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
#include "TaskApplyTypeExtensions.h"
#include "TaskResolveImports.h"

#define DEBUG_ENTER(fmt, ...) \
	fprintf(stdout, "--> TaskApplyTypeExtensions::"); \
	fprintf(stdout, fmt, ##__VA_ARGS__); \
	fprintf(stdout, "\n");

#define DEBUG(fmt, ...) \
	fprintf(stdout, "TaskApplyTypeExtensions: "); \
	fprintf(stdout, fmt, ##__VA_ARGS__); \
	fprintf(stdout, "\n");

#define DEBUG_LEAVE(fmt, ...) \
	fprintf(stdout, "<-- TaskApplyTypeExtensions::"); \
	fprintf(stdout, fmt, ##__VA_ARGS__); \
	fprintf(stdout, "\n");

namespace zsp {


TaskApplyTypeExtensions::TaskApplyTypeExtensions(
    IFactory                *factory,
    IMarkerListener         *marker_l) : 
        m_factory(factory), m_marker_l(marker_l) {

}

TaskApplyTypeExtensions::~TaskApplyTypeExtensions() {

}

void TaskApplyTypeExtensions::apply(ast::ISymbolScope *root) {
    DEBUG_ENTER("apply");
    m_symtab_it = zsp::ISymbolTableIteratorUP(
        m_factory->mkAstSymbolTableIterator(root));

    root->accept(this);

    DEBUG_LEAVE("apply");
}

void TaskApplyTypeExtensions::visitExtendEnum(ast::IExtendEnum *i) {
    DEBUG_ENTER("visitExtendEnum");

    DEBUG_LEAVE("visitExtendEnum");
}

void TaskApplyTypeExtensions::visitExtendType(ast::IExtendType *i) {
    DEBUG_ENTER("visitExtendType");

    DEBUG_LEAVE("visitExtendType");
}

void TaskApplyTypeExtensions::visitSymbolScope(ast::ISymbolScope *i) {
    DEBUG_ENTER("visitSymbolScope");

    if (m_symtab_it->pushNamedScope(i->getName())) {
        // Internal error
    }

    ast::ISymbolScope *scope = m_symtab_it->getScope();
    if (scope->getImports()) {
        TaskResolveImports(m_factory, m_marker_l).resolve(
            m_symtab_it.get(),
            scope
        );
    }

    for (std::vector<ast::IScopeChild *>::const_iterator
        it=i->getChildren().begin();
        it!=i->getChildren().end(); it++) {
        (*it)->accept(this);
    }

    m_symtab_it->popScope();

    DEBUG_LEAVE("visitSymbolScope");
}

void TaskApplyTypeExtensions::visitPackageScope(ast::IPackageScope *i) {
    DEBUG_ENTER("visitPackageScope");

    if (m_symtab_it->pushNamedScope(i->getId().at(0)->getId()) == -1) {
        // Internal error
    }

    ast::ISymbolScope *scope = m_symtab_it->getScope();
    if (scope->getImports()) {
        TaskResolveImports(m_factory, m_marker_l).resolve(
            m_symtab_it.get(),
            scope
        );
    }

    m_symtab_it->popScope();
    DEBUG_LEAVE("visitPackageScope");
}

}
