/*
 * TaskResolveRef.cpp
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
#include "zsp/parser/impl/TaskResolveSymbolPathRef.h"
#include "TaskBuildParamValList.h"
#include "TaskGetSpecializedTemplateType.h"
#include "TaskResolveRef.h"
#include "TaskResolveRefs.h"
#include "TaskResolveRootRef.h"
#include "TaskResolveFieldRef.h"
#include "Marker.h"

namespace zsp {
namespace parser {



TaskResolveRef::TaskResolveRef(
    ast::ISymbolScope               *root,
    IFactory                        *factory,
    IMarkerListener                 *marker_l,
    bool                            search_imp) : 
        m_root(root), m_factory(factory), m_marker_l(marker_l),
        m_search_imp(search_imp) {
    DEBUG_INIT("TaskResolveRef", factory->getDebugMgr());
    m_ref = 0;
}

TaskResolveRef::~TaskResolveRef() {

}

ast::ISymbolRefPath *TaskResolveRef::resolve(
        const ISymbolTableIterator      *scope,
        ast::ITypeIdentifier            *type_id) {
    DEBUG_ENTER("resolve");

    // Push a copy of the symbol iterator
    m_symtab_it_s.push_back(ISymbolTableIteratorUP(scope->clone()));
    type_id->accept(m_this);
    m_symtab_it_s.pop_back();

    DEBUG_LEAVE("resolve %p", m_ref);
    return m_ref;
}

ast::ISymbolRefPath *TaskResolveRef::resolve(
        const ISymbolTableIterator      *scope,
        ast::IExpr                      *ref) {
    DEBUG_ENTER("resolve (RefPath)");
    m_symtab_it_s.push_back(ISymbolTableIteratorUP(scope->clone()));
    ref->accept(m_this);
    m_symtab_it_s.pop_back();
    DEBUG_LEAVE("resolve (RefPath) %p", m_ref);
    return m_ref;
}

void TaskResolveRef::visitExprRefPathStaticRooted(ast::IExprRefPathStaticRooted *i) {
    DEBUG_ENTER("visitExprRefPathStaticRooted");
    DEBUG("TODO: visitExprRefPathStaticRooted");
    DEBUG_LEAVE("visitExprRefPathStaticRooted");
}

void TaskResolveRef::visitExprRefPathId(ast::IExprRefPathId *i) {
    DEBUG_ENTER("visitExprRefPathId");

	// Find the first element
    ISymbolTableIterator *it = m_symtab_it_s.back().get();

    ast::ISymbolRefPath *root = findRoot(it, i->getId());

    m_ref = root;

    DEBUG_LEAVE("visitExprRefPathId");
}

void TaskResolveRef::visitExprRefPathContext(ast::IExprRefPathContext *i) {
    DEBUG_ENTER("visitExprRefPathContext");
    DEBUG("TODO: visitExprRefPathContext");
    DEBUG_LEAVE("visitExprRefPathContext");
}

void TaskResolveRef::visitExprRefPathStatic(ast::IExprRefPathStatic *i) {
    DEBUG_ENTER("visitExprRefPathStatic");
    DEBUG("TODO: visitExprRefPathStatic");
    DEBUG_LEAVE("visitExprRefPathStatic");
}

void TaskResolveRef::visitSymbolScope(ast::ISymbolScope *i) { 
//    m_ref = 
}

void TaskResolveRef::visitSymbolExecScope(ast::ISymbolExecScope *i) { 

}

void TaskResolveRef::visitSymbolTypeScope(ast::ISymbolTypeScope *i) {

}

void TaskResolveRef::visitSymbolFunctionScope(ast::ISymbolFunctionScope *i) { 

}

void TaskResolveRef::visitTypeIdentifier(ast::ITypeIdentifier *i) {
    DEBUG_ENTER("visitTypeIdentifier");
	// Find the first element

    ISymbolTableIterator *it = m_symtab_it_s.back().get();

    ast::ISymbolRefPath *root = findRoot(it, i->getElems().at(0)->getId());

    if (!root) {
        // resolution failure

        if (m_marker_l) {
            std::string msg = "resolution failed for ";
            msg += i->getElems().at(0)->getId()->getId();

            if (!m_marker.get()) {
                m_marker = IMarkerUP(m_factory->mkMarker(
                    "", 
                    MarkerSeverityE::Error,
                    {-1, -1, -1}));
            }
            m_marker->setMsg(msg);
            m_marker->setSeverity(MarkerSeverityE::Error);
            m_marker->setLocation(i->getElems().at(0)->getId()->getLocation());
            fprintf(stdout, "Send marker");
            m_marker_l->marker(m_marker.get());
        }
        fprintf(stdout, "Error: resolution failed for %s (%p)\n",
            i->getElems().at(0)->getId()->getId().c_str(),
            m_marker_l);
        fflush(stdout);
        return;
    }

    if (i->getElems().at(0)->getParams()) {
        // Resolve parameter refs

        for (std::vector<ast::ITemplateParamValueUP>::const_iterator
            it=i->getElems().at(0)->getParams()->getValues().begin();
            it!=i->getElems().at(0)->getParams()->getValues().end(); it++) {
            (*it)->accept(m_this);
        }

        ast::ISymbolRefPath *root_s = specializeParameterizedRef(
            root, i->getElems().at(0)->getParams());
        delete root;
        root = root_s;
        fflush(stdout);
    }

    ast::IScopeChild *root_t = TaskResolveSymbolPathRef(m_root).resolve(root);

    for (std::vector<ast::ITypeIdentifierElemUP>::const_iterator
        it=i->getElems().begin()+1;
        it!=i->getElems().end(); it++) {
        ast::IScopeChild *next = TaskResolveFieldRef(m_factory->getDebugMgr(), m_marker_l).resolve(
            (*it)->getId(),
            root_t,
            root);

        if (next) {
            if ((*it)->getParams()) {
               root = specializeParameterizedRef(root, (*it)->getParams());
               root_t = TaskResolveSymbolPathRef(m_root).resolve(root);
            } else {
                root_t = next;
            }
        } else {
            // Assume 
            delete root;
            root = 0;
            break;
        }
    }

    m_ref = root;
    
    DEBUG_LEAVE("visitTypeIdentifier");
}

ast::ISymbolRefPath *TaskResolveRef::findRoot(
        ISymbolTableIterator            *scope,
        const ast::IExprId              *sym) {
    return TaskResolveRootRef(m_factory, m_marker_l).resolve(scope, sym);
}

ast::ISymbolRefPath *TaskResolveRef::specializeParameterizedRef(
        ast::ISymbolRefPath             *target,
        ast::ITemplateParamValueList    *pvals) {
    DEBUG_ENTER("specializeParameterizedRef");

    // Find the base type
    ast::IScopeChild *target_sc = TaskResolveSymbolPathRef(m_root).resolve(target);
    ast::ISymbolTypeScope *target_c = 
        TaskResolveSymbolPathRef(m_root).resolveT<ast::ISymbolTypeScope>(target);

    if (!target_c) {
        DEBUG("TODO: Flag error about templated type");
        return 0;
    }

    if (!target_c->getPlist()) {
        DEBUG("TODO: Flag type as not being templated");
        return 0;
    }

    // Form parameter list 
    ast::ITemplateParamDeclList *pdecl_list = TaskBuildParamValList(
        m_root, m_factory, m_marker_l).build(
            target_c->getPlist(),
            pvals);
    TaskGetSpecializedTemplateType typespec_getter(m_root, m_factory, m_marker_l);

    ast::ISymbolRefPath *target_t = typespec_getter.find(target, pdecl_list);

    if (target_t) {
        // The new parameter list that we created is no longer needed
        delete pdecl_list;
    } else {
        target_t = typespec_getter.mk(target, pdecl_list);
    }
    

    DEBUG_LEAVE("specializeParameterizedRef %p", target_t);
    return target_t;
}

dmgr::IDebug *TaskResolveRef::m_dbg = 0;

}
}
