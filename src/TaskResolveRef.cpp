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
        ast::IExprRefPath               *ref) {
    DEBUG_ENTER("resolve (RefPath)");
    m_symtab_it_s.push_back(ISymbolTableIteratorUP(scope->clone()));
    ref->accept(m_this);
    m_symtab_it_s.pop_back();
    DEBUG_LEAVE("resolve (RefPath) %p", m_ref);
    return m_ref;
}

ast::ISymbolRefPath *TaskResolveRef::resolve(
        const ISymbolTableIterator      *scope,
        ast::IExprId                    *ref) {
    DEBUG_ENTER("resolve");
	ISymbolTableIteratorUP it(scope->clone());

    ast::ISymbolRefPath *ret = findRoot(it.get(), ref);

    DEBUG_LEAVE("resolve (%p)", ret);

    return ret;
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
    }

    if (i->getElems().at(0)->getParams()) {
        ast::ISymbolRefPath *root_s = specializeParameterizedRef(
            root, i->getElems().at(0)->getParams());
        delete root;
        root = root_s;
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

ast::ISymbolRefPath *TaskResolveRef::searchImport(
        ISymbolTableIterator            *scope,
        ast::IPackageImportStmt         *imp,
        const std::string               &sym) {
	DEBUG_ENTER("searchImport %s", sym.c_str());
#ifdef UNDEFINED
	// ast::ISymbolRefPath *ret = 0;
	if (!imp->getPath()->getTarget()) {
		DEBUG("Skipping, due to unset import target");
		return 0;
	}
	for (uint32_t i=0; i<imp->getPath()->getTarget()->getPath().size(); i++) {
		DEBUG("Imp Path[%d] %d", i, imp->getPath()->getTarget()->getPath().at(i));
	}
	ast::IScopeChild *target_c = scope->resolveAbsPath(imp->getPath()->getTarget());
	ast::ISymbolScope *target_s = dynamic_cast<ast::ISymbolScope *>(target_c);
	DEBUG("target_c: %p ; target_s: %p", target_c, target_s);

	if (target_s) {
		DEBUG("Have a symbol scope (%s)", target_s->getName().c_str());
		std::map<std::string, int32_t>::const_iterator it;
		it = target_s->getSymtab().find(sym);

		if (it != target_s->getSymtab().end()) {
			DEBUG("Found the symbol (%s)", sym.c_str());
			ret = m_factory->getAstFactory()->mkSymbolRefPath();
			ret->getPath().insert(
				ret->getPath().begin(),
				imp->getPath()->getTarget()->getPath().begin(),
				imp->getPath()->getTarget()->getPath().end());
			ret->getPath().push_back({
                ast::SymbolRefPathElemKind::ElemKind_ChildIdx, it->second
            });
		}
	}
#endif /* UNDEFINED */

	DEBUG_LEAVE("searchImport %s", sym.c_str());
	return 0;
}

ast::ISymbolRefPath *TaskResolveRef::specializeParameterizedRef(
        ast::ISymbolRefPath             *target,
        ast::ITemplateParamValueList    *pvals) {
    DEBUG_ENTER("specializeParameterizedRef");

    // Find the base type
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
    ast::ISymbolScope *plist_sym = TaskBuildParamValList(
        m_root, m_factory, m_marker_l).build(
            target_c->getPlist(),
            pvals);
    ast::ITemplateParamDeclList *pdecl_list = 
        dynamic_cast<ast::ITemplateParamDeclList *>(plist_sym->getTarget());
    TaskGetSpecializedTemplateType typespec_getter(m_factory, m_root);

    ast::ISymbolRefPath *target_t = typespec_getter.find(target, pdecl_list);

    if (target_t) {
        // The new parameter list that we created is no longer needed
        delete plist_sym;
    } else {
        target_t= typespec_getter.mk(target, pdecl_list);
    }

    return target_t;
    DEBUG_LEAVE("specializeParameterizedRef");
}

dmgr::IDebug *TaskResolveRef::m_dbg = 0;

}
}
