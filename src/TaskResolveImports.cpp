/*
 * TaskResolveImports.cpp
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
#include "TaskResolveImports.h"
#include "TaskResolveRef.h"

#define DEBUG_ENTER(fmt, ...) \
	fprintf(stdout, "--> TaskResolveImports::"); \
	fprintf(stdout, fmt, ##__VA_ARGS__); \
	fprintf(stdout, "\n");

#define DEBUG(fmt, ...) \
	fprintf(stdout, "TaskResolveImports: "); \
	fprintf(stdout, fmt, ##__VA_ARGS__); \
	fprintf(stdout, "\n");

#define DEBUG_LEAVE(fmt, ...) \
	fprintf(stdout, "<-- TaskResolveImports::"); \
	fprintf(stdout, fmt, ##__VA_ARGS__); \
	fprintf(stdout, "\n");

namespace zsp {


TaskResolveImports::TaskResolveImports(
    IFactory                *factory,
    IMarkerListener         *marker_l) : 
        m_factory(factory), m_marker_l(marker_l) {

}

TaskResolveImports::~TaskResolveImports() {

}

void TaskResolveImports::resolve(
    const ISymbolTableIterator      *scope,
    ast::ISymbolScope               *sym_scope) {
    DEBUG_ENTER("resolve");
    m_scope_it = ISymbolTableIteratorUP(scope->clone());
    if (sym_scope->getImports()) {
        for (std::vector<ast::IPackageImportStmt *>::const_iterator
            it=sym_scope->getImports()->getImports().begin();
            it!=sym_scope->getImports()->getImports().end(); it++) {
            (*it)->accept(this);
        }
    }
    DEBUG_LEAVE("resolve");
}

void TaskResolveImports::visitPackageImportStmt(ast::IPackageImportStmt *i) {
    DEBUG_ENTER("visitPackageImportStmt");
    if (!i->getPath()->getTarget()) {
        i->getPath()->setTarget(TaskResolveRef(m_factory, m_marker_l).resolve(
            m_scope_it.get(),
            i->getPath()
        ));
    }
    DEBUG_LEAVE("visitPackageImportStmt");
}

}
