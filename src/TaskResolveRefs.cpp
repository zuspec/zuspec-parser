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
#include "dmgr/impl/DebugMacros.h"
#include "TaskResolveRef.h"
#include "TaskResolveRefs.h"

namespace zsp {
namespace parser {



TaskResolveRefs::TaskResolveRefs(
    dmgr::IDebugMgr     *dmgr,
    IFactory            *factory,
    IMarkerListener     *marker_l) : m_factory(factory), m_marker_l(marker_l) {
    m_dmgr = dmgr;
    DEBUG_INIT("TaskResolveRefs", dmgr);
}

TaskResolveRefs::~TaskResolveRefs() {

}

void TaskResolveRefs::resolve(ast::ISymbolScope *root) {
    DEBUG_ENTER("resolve");
    m_symtab_it = ISymbolTableIteratorUP(m_factory->mkAstSymbolTableIterator(root));
    for (std::vector<ast::IScopeChild *>::const_iterator
        it=root->getChildren().begin();
        it!=root->getChildren().end(); it++) {
        (*it)->accept(this);
    }
    DEBUG_LEAVE("resolve");
}

void TaskResolveRefs::visitSymbolScope(ast::ISymbolScope *i) {
    DEBUG_ENTER("visitSymbolScope %s", i->getName().c_str());
    if (m_symtab_it->pushNamedScope(i->getName()) == -1) {
        // TODO: internal error
        fprintf(stdout, "Internal Error: no scope named %s in %s\n", 
            i->getName().c_str(),
            m_symtab_it->getScope()->getName().c_str());
    }

    for (std::vector<ast::IScopeChild *>::const_iterator
        it=i->getChildren().begin();
        it!=i->getChildren().end(); it++) {
        (*it)->accept(this);
    }

    m_symtab_it->popScope();
    DEBUG_LEAVE("visitSymbolScope %s", i->getName().c_str());
}

void TaskResolveRefs::visitSymbolExtendScope(ast::ISymbolExtendScope *i) {
    DEBUG_ENTER("visitSymbolExtendScope");

    m_symtab_it->pushScope(i);

    for (std::vector<ast::IScopeChild *>::const_iterator
        it=i->getChildren().begin();
        it!=i->getChildren().end(); it++) {
        (*it)->accept(this);
    }

    m_symtab_it->popScope();

    DEBUG_LEAVE("visitSymbolExtendScope");
}

void TaskResolveRefs::visitSymbolTypeScope(ast::ISymbolTypeScope *i) {
    DEBUG_ENTER("visitSymbolTypeScope %s", i->getName().c_str());
    if (m_symtab_it->pushNamedScope(i->getName()) == -1) {
        // TODO: internal error
        fprintf(stdout, "Internal Error: no scope named %s in %s\n", 
            i->getName().c_str(),
            m_symtab_it->getScope()->getName().c_str());
    }

    if (dynamic_cast<ast::ITypeScope *>(i->getTarget())->getSuper_t()) {
        dynamic_cast<ast::ITypeScope *>(i->getTarget())->getSuper_t()->accept(this);
    }

    for (std::vector<ast::IScopeChild *>::const_iterator
        it=i->getChildren().begin();
        it!=i->getChildren().end(); it++) {
        (*it)->accept(this);
    }

    m_symtab_it->popScope();
    DEBUG_LEAVE("visitSymbolTypeScope %s", i->getName().c_str());
}

void TaskResolveRefs::visitDataTypeUserDefined(ast::IDataTypeUserDefined *i) {
    DEBUG_ENTER("visitDataTypeUserDefined");
    ast::ISymbolRefPath *target = TaskResolveRef(m_factory, m_marker_l).resolve(
        m_symtab_it.get(),
        i->getType_id()
    );

    if (target) {
        DEBUG("Success");
        i->getType_id()->setTarget(target);
    } else {
        DEBUG("Failed");
    }

    DEBUG_LEAVE("visitDataTypeUserDefined");
}

void TaskResolveRefs::visitTypeIdentifier(ast::ITypeIdentifier *i) {
    DEBUG_ENTER("visitTypeIdentifier");
    ast::ISymbolRefPath *target = TaskResolveRef(m_factory, m_marker_l).resolve(
        m_symtab_it.get(),
        i
    );
    DEBUG_LEAVE("visitTypeIdentifier");
}

void TaskResolveRefs::visitStruct(ast::IStruct *i) {
    DEBUG_ENTER("visitStruct");
    VisitorBase::visitStruct(i);
    DEBUG_LEAVE("visitStruct");
}

dmgr::IDebug *TaskResolveRefs::m_dbg = 0;

}
}
