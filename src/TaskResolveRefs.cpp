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
#include "TaskLinkActionCompRefFields.h"
#include "TaskResolveImports.h"
#include "TaskResolveRef.h"
#include "TaskResolveRefs.h"

namespace zsp {
namespace parser {



TaskResolveRefs::TaskResolveRefs(
    dmgr::IDebugMgr     *dmgr,
    IFactory            *factory,
    IMarkerListener     *marker_l) : m_factory(factory), m_marker_l(marker_l) {
    m_dmgr = dmgr;
    m_root = 0;
    DEBUG_INIT("TaskResolveRefs", dmgr);
}

TaskResolveRefs::~TaskResolveRefs() {

}

void TaskResolveRefs::resolve(ast::ISymbolScope *root) {
    DEBUG_ENTER("resolve (SymbolScope root)");
    m_root = root;
    m_symtab_it = ISymbolTableIteratorUP(m_factory->mkAstSymbolTableIterator(root));

    // First, ensure all actions have their 'comp' refs updated
    TaskLinkActionCompRefFields(m_factory).link(root);

    // Phases:
    // - 

    for (std::vector<ast::IScopeChild *>::const_iterator
        it=root->getChildren().begin();
        it!=root->getChildren().end(); it++) {
        (*it)->accept(this);
    }
    DEBUG_LEAVE("resolve");
}

void TaskResolveRefs::resolve(
    parser::ISymbolTableIterator            *root_it,
    ast::ISymbolTypeScope                   *scope) {
    DEBUG_ENTER("resolve (iterator, scope)");
    // TODO: obtain root
    parser::ISymbolTableIteratorUP root_it_c(root_it->clone());
    DEBUG("Scope Stack");
    while (root_it_c->hasScopes()) {
        DEBUG("  Scope: %d", 
            root_it_c->getScope()->getId());
        root_it_c->popScope();
    }
    m_root = root_it->getRootScope();
    m_symtab_it = ISymbolTableIteratorUP(root_it->clone());

    TaskLinkActionCompRefFields(m_factory).link(scope);

//    m_symtab_it->pushScope(scope);
    scope->accept(m_this);
//    m_symtab_it->popScope();

    /*
    for (std::vector<ast::IScopeChild *>::const_iterator
        it=root->getChildren().begin();
        it!=root->getChildren().end(); it++) {
        (*it)->accept(this);
    }
     */
    
    DEBUG_LEAVE("resolve (iterator, scope)");
}

void TaskResolveRefs::visitActivityActionHandleTraversal(ast::IActivityActionHandleTraversal *i) {
    DEBUG_ENTER("visitActivityActionHandleTraversal");
    ast::ISymbolRefPath *target_ref = TaskResolveRef(m_root, m_factory, m_marker_l).resolve(
        m_symtab_it.get(),
        i->getTarget());
    if (!target_ref) {
        return;
    }

    i->getTarget()->setTarget(target_ref);
    ast::IScopeChild *target = resolvePath(i->getTarget()->getTarget());
    ast::IField *field = dynamic_cast<ast::IField *>(target);
    DEBUG("target=%p field=%p", target, field);
    DEBUG("field: %s", field->getName()->getId().c_str());
    ast::IDataType *field_t = field->getType();
    ast::IDataTypeUserDefined *field_udt = dynamic_cast<ast::IDataTypeUserDefined *>(field_t);

    DEBUG("field_t=%p action_t=%p", field_t, field_udt);
    ast::IScopeChild *field_c = resolvePath(field_udt->getType_id()->getTarget());
    ast::ISymbolScope *field_scope = dynamic_cast<ast::ISymbolScope *>(field_c);
    DEBUG("field_c=%p field_scope=%s", field_c, field_scope->getName().c_str());
    m_symtab_it->pushScope(field_scope);
    if (i->getWith_c()) {
        DEBUG_ENTER(" ::getWith()");
        i->getWith_c()->accept(m_this);
        DEBUG_LEAVE(" ::getWith()");
    }
    m_symtab_it->popScope();
    DEBUG_LEAVE("visitActivityActionHandleTraversal");
}
    
void TaskResolveRefs::visitActivityActionTypeTraversal(ast::IActivityActionTypeTraversal *i) {
    DEBUG_ENTER("visitActivityActionTypeTraversal");
    i->getTarget()->accept(m_this);
    DEBUG_LEAVE("visitActivityActionTypeTraversal");
}

void TaskResolveRefs::visitExprRefPathContext(ast::IExprRefPathContext *i) {
    DEBUG_ENTER("visitExprRefPathContext %s", i->getHier_id()->getElems().at(0)->getId()->getId().c_str());
    // Find the first path element
    ast::ISymbolRefPath *target = TaskResolveRef(m_root, m_factory, m_marker_l).resolve(
        m_symtab_it.get(),
        i->getHier_id()->getElems().at(0)->getId());

    if (!target) {
        char tmp[1024];
        sprintf(tmp, "failed to find root ref-path element %s",
            i->getHier_id()->getElems().at(0)->getId()->getId().c_str());
        IMarkerUP marker(m_factory->mkMarker(
            tmp,
            MarkerSeverityE::Error,
            i->getHier_id()->getElems().at(0)->getId()->getLocation()
        ));
        m_marker_l->marker(marker.get());

        DEBUG_LEAVE("visitExprRefPathContext -- fail");
        return;
    }
    
    i->setTarget(target);

    if (i->getHier_id()->getElems().at(0)->getParams()) {
        i->getHier_id()->getElems().at(0)->getParams()->accept(m_this);
    }
    DEBUG_LEAVE("visitExprRefPathContext");
}


void TaskResolveRefs::visitExprRefPathId(ast::IExprRefPathId *i) {
    DEBUG_ENTER("visitExprRefPathId %s", i->getId()->getId().c_str());
    ast::ISymbolRefPath *target = TaskResolveRef(m_root, m_factory, m_marker_l).resolve(
        m_symtab_it.get(),
        i
    );
    if (!target) {
        fprintf(stdout, "Failed to resolve ref-path %s\n", i->getId()->getId().c_str());
    }
    i->setTarget(target);
    DEBUG_LEAVE("visitExprRefPathId");
}

void TaskResolveRefs::visitExprRefPathStaticRooted(ast::IExprRefPathStaticRooted *i) {
    DEBUG_ENTER("visitExprRefPathStaticRooted");
    DEBUG("TODO: visitExprRefPathStaticRooted");
    DEBUG_LEAVE("visitExprRefPathStaticRooted");
}

void TaskResolveRefs::visitExtendEnum(ast::IExtendEnum *i) {
    DEBUG_ENTER("visitExtendEnum");
    DEBUG("Note: Skip during core symbol resolution");
    DEBUG_LEAVE("visitExtendEnum");
}

void TaskResolveRefs::visitExtendType(ast::IExtendType *i) {
    DEBUG_ENTER("visitExtendType");
    DEBUG("Note: Skip during core symbol resolution");
    DEBUG_LEAVE("visitExtendType");
}

void TaskResolveRefs::visitFieldCompRef(ast::IFieldCompRef *i) {
    DEBUG_ENTER("visitFieldCompRef");
    DEBUG("Note: Skip during core symbol resolution");
    DEBUG_LEAVE("visitFieldCompRef");
}

void TaskResolveRefs::visitFunctionPrototype(ast::IFunctionPrototype *i) {
    DEBUG_ENTER("visitFunctionPrototype");

    if (i->getRtype()) {
        i->getRtype()->accept(m_this);
    }

    for (std::vector<ast::IFunctionParamDeclUP>::const_iterator
        it=i->getParameters().begin();
        it!=i->getParameters().end(); it++) {
        (*it)->getType()->accept(m_this);
    }
    DEBUG_LEAVE("visitFunctionPrototype");
} 

void TaskResolveRefs::visitSymbolScope(ast::ISymbolScope *i) {
    DEBUG_ENTER("visitSymbolScope \"%s\"", i->getName().c_str());
    if (i->getName() != "") {
        if (m_symtab_it->pushNamedScope(i->getName()) == -1) {
            // TODO: internal error
            fprintf(stdout, "Internal Error: no scope named %s in %s\n", 
                i->getName().c_str(),
                m_symtab_it->getScope()->getName().c_str());
        }
    } else {
        m_symtab_it->pushScope(i);
    }

    if (i->getImports()) {
        DEBUG_ENTER("  Resolve Imports");
        TaskResolveImports(m_root, m_factory, m_marker_l).resolve(
            m_symtab_it.get(),
            i);
        DEBUG_LEAVE("  Resolve Imports");
    }

    for (std::vector<ast::IScopeChild *>::const_iterator
        it=i->getChildren().begin();
        it!=i->getChildren().end(); it++) {
        (*it)->accept(this);
    }

    m_symtab_it->popScope();
    DEBUG_LEAVE("visitSymbolScope \"%s\"", i->getName().c_str());
}

void TaskResolveRefs::visitSymbolExtendScope(ast::ISymbolExtendScope *i) {
    DEBUG_ENTER("visitSymbolExtendScope");
    DEBUG("Note: Skipping during core symbol resolution");

/*
    m_symtab_it->pushScope(i);

    for (std::vector<ast::IScopeChild *>::const_iterator
        it=i->getChildren().begin();
        it!=i->getChildren().end(); it++) {
        (*it)->accept(this);
    }

    m_symtab_it->popScope();
 */

    DEBUG_LEAVE("visitSymbolExtendScope");
}

void TaskResolveRefs::visitSymbolExecScope(ast::ISymbolExecScope *i) {
    DEBUG_ENTER("visitSymbolExecScope \"%s\"", i->getName().c_str());
    m_symtab_it->pushScope(i);

    for (std::vector<ast::IScopeChild *>::const_iterator
        it=i->getChildren().begin();
        it!=i->getChildren().end(); it++) {
        (*it)->accept(this);
    }

    m_symtab_it->popScope();
    DEBUG_LEAVE("visitSymbolExecScope \"%s\"", i->getName().c_str());
}

void TaskResolveRefs::visitSymbolFunctionScope(ast::ISymbolFunctionScope *i) {
    DEBUG_ENTER("visitSymbolFunctionScope %s (%d)", 
    i->getName().c_str(),
    i->getPrototypes().size());


    for (std::vector<ast::IFunctionPrototype *>::const_iterator
        it=i->getPrototypes().begin();
        it!=i->getPrototypes().end(); it++) {
        (*it)->accept(m_this);
    }

    if (i->getBody()) {
        m_symtab_it->pushScope(i);
        m_symtab_it->pushScope(i->getBody());
        for (std::vector<ast::IScopeChild *>::const_iterator
            it=i->getBody()->getChildren().begin();
            it!=i->getBody()->getChildren().end(); it++) {
            (*it)->accept(m_this);
        }
        m_symtab_it->popScope();
        m_symtab_it->popScope();
    }


    DEBUG_LEAVE("visitSymbolFunctionScope %s", i->getName().c_str());
}

void TaskResolveRefs::visitSymbolTypeScope(ast::ISymbolTypeScope *i) {
    ast::ITypeScope *i_ts = dynamic_cast<ast::ITypeScope *>(i->getTarget());
    DEBUG_ENTER("visitSymbolTypeScope %s (param=%s specialized=%s)", 
        i->getName().c_str(),
        (i_ts->getParams())?"true":"false",
        (i_ts->getParams() && i_ts->getParams()->getSpecialized())?"true":"false");
    if (i_ts->getParams() && !i_ts->getParams()->getSpecialized()) {
        DEBUG("Note: Skipping symbol resolution in a templated type");
    } else {
        ast::SymbolRefPathElemKind kind = ast::SymbolRefPathElemKind::ElemKind_ChildIdx;

        if (i_ts->getParams() && i_ts->getParams()->getSpecialized()) {
            kind = ast::SymbolRefPathElemKind::ElemKind_TypeSpec;
            // Ensure parameter references are resolved
            i_ts->getParams()->accept(m_this);
        }

        // TODO: might need to defer this until after we've resolved
        // super-class
        m_symtab_it->pushScope(i, kind);

        // Resolve the super class (if any)
        if (dynamic_cast<ast::ITypeScope *>(i->getTarget())->getSuper_t()) {
            DEBUG("%s Has a super type ... resolving", i->getName().c_str());
            dynamic_cast<ast::ITypeScope *>(i->getTarget())->getSuper_t()->accept(this);
        } else {
            DEBUG("No super type");
        }

        if (i->getImports()) {
            DEBUG_ENTER("  Resolve Imports");
            TaskResolveImports(m_root, m_factory, m_marker_l).resolve(
                m_symtab_it.get(),
                i);
            DEBUG_LEAVE("  Resolve Imports");
        }

        // Check on children
        for (std::vector<ast::IScopeChild *>::const_iterator
            it=i->getChildren().begin();
            it!=i->getChildren().end(); it++) {
            (*it)->accept(m_this);
        }

        m_symtab_it->popScope();
    }
    DEBUG_LEAVE("visitSymbolTypeScope %s", i->getName().c_str());
}

void TaskResolveRefs::visitDataTypeUserDefined(ast::IDataTypeUserDefined *i) {
    DEBUG_ENTER("visitDataTypeUserDefined");
    ast::ISymbolRefPath *target = TaskResolveRef(m_root, m_factory, m_marker_l).resolve(
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
    ast::ISymbolRefPath *target = TaskResolveRef(m_root, m_factory, m_marker_l).resolve(
        m_symtab_it.get(),
        i
    );
    i->setTarget(target);
    DEBUG_LEAVE("visitTypeIdentifier");
}

void TaskResolveRefs::visitStruct(ast::IStruct *i) {
    DEBUG_ENTER("visitStruct");
    VisitorBase::visitStruct(i);
    DEBUG_LEAVE("visitStruct");
}

ast::IScopeChild *TaskResolveRefs::resolvePath(ast::ISymbolRefPath *path) {
    ast::ISymbolScope *scope = m_root;
    ast::IScopeChild *ret = m_root;

    for (std::vector<ast::SymbolRefPathElem>::const_iterator
        it=path->getPath().begin();
        it!=path->getPath().end(); it++) {
        ret = scope->getChildren().at(it->idx);

        if (it+1 != path->getPath().end()) {
            scope = dynamic_cast<ast::ISymbolScope *>(ret);
        }
    }
    
    return ret;
}

dmgr::IDebug *TaskResolveRefs::m_dbg = 0;

}
}
