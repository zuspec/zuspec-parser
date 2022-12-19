/*
 * TaskResolveRefs.cpp
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
#include "TaskResolveRef.h"
#include "TaskResolveRefs.h"

#define DEBUG_ENTER(fmt, ...) \
	fprintf(stdout, "--> TaskResolveRefs::"); \
	fprintf(stdout, fmt, ##__VA_ARGS__); \
	fprintf(stdout, "\n");

#define DEBUG(fmt, ...) \
	fprintf(stdout, "TaskResolveRefs: "); \
	fprintf(stdout, fmt, ##__VA_ARGS__); \
	fprintf(stdout, "\n");

#define DEBUG_LEAVE(fmt, ...) \
	fprintf(stdout, "<-- TaskResolveRefs::"); \
	fprintf(stdout, fmt, ##__VA_ARGS__); \
	fprintf(stdout, "\n");

namespace zsp {


TaskResolveRefs::TaskResolveRefs(
    IFactory            *factory,
    IMarkerListener     *marker_l) : m_factory(factory), m_marker_l(marker_l) {

}

TaskResolveRefs::~TaskResolveRefs() {

}

void TaskResolveRefs::resolve(ast::ISymbolScope *root) {
    DEBUG_ENTER("resolve");
    m_symtab_it = ISymbolTableIteratorUP(m_factory->mkAstSymbolTableIterator(root));
    root->accept(this);
    DEBUG_LEAVE("resolve");
}

void TaskResolveRefs::visitSymbolScope(ast::ISymbolScope *i) {
    DEBUG_ENTER("visitSymbolScope");
    if (!m_symtab_it->pushNamedScope(i->getName())) {
        // TODO: internal error
    }

    for (std::vector<ast::IScopeChild *>::const_iterator
        it=i->getChildren().begin();
        it!=i->getChildren().end(); it++) {
        (*it)->accept(this);
    }

    m_symtab_it->popScope();
    DEBUG_LEAVE("visitSymbolScope");
}

void TaskResolveRefs::visitSymbolTypeScope(ast::ISymbolTypeScope *i) {
    DEBUG_ENTER("visitSymbolTypeScope");
    if (!m_symtab_it->pushNamedScope(i->getName())) {
        // TODO: internal error
    }

    for (std::vector<ast::IScopeChild *>::const_iterator
        it=i->getChildren().begin();
        it!=i->getChildren().end(); it++) {
        (*it)->accept(this);
    }

    m_symtab_it->popScope();
    DEBUG_LEAVE("visitSymbolTypeScope");
}

void TaskResolveRefs::visitDataTypeUserDefined(ast::IDataTypeUserDefined *i) {
    DEBUG_ENTER("visitDataTypeUserDefined");
    ast::ISymbolRefPath *target = TaskResolveRef(m_factory, m_marker_l).resolve(
        m_symtab_it.get(),
        i->getType_id()
    );

    if (target) {
        DEBUG("Success");
    } else {
        DEBUG("Failed");
    }
    DEBUG_LEAVE("visitDataTypeUserDefined");
}

}
