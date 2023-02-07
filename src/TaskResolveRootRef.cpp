/*
 * TaskResolveRootRef.cpp
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
#include "zsp/ast/IPackageImportStmt.h"
#include "TaskResolveRootRef.h"


namespace zsp {
namespace parser {


TaskResolveRootRef::TaskResolveRootRef(
    IFactory            *factory,
    IMarkerListener     *marker_l,
    bool                search_imp) : 
        m_factory(factory), m_marker_l(marker_l), m_search_imp(search_imp) {
    DEBUG_INIT("TaskResolveRootRef", factory->getDebugMgr());

}

TaskResolveRootRef::~TaskResolveRootRef() {

}

ast::ISymbolRefPath *TaskResolveRootRef::resolve(
        const ISymbolTableIterator      *scope,
        const ast::IExprId              *id) {
    DEBUG_ENTER("resolve");
    m_ref = 0;

    m_scope = ISymbolTableIteratorUP(scope->clone());
    m_id    = id;

    while (!m_ref && m_scope->hasScopes()) {
        m_scope->getScope()->accept(m_this);

        if (!m_ref) {
            m_scope->popScope();
        }
    }

    DEBUG_LEAVE("resolve %p", m_ref);

    return m_ref;
}

void TaskResolveRootRef::visitSymbolScope(ast::ISymbolScope *i) {
    DEBUG_ENTER("visitSymbolScope id=%s (%s)", 
        m_id->getId().c_str(), i->getName().c_str());
    std::map<std::string,int32_t>::const_iterator it = i->getSymtab().find(m_id->getId());

    DEBUG("imports: %p", i->getImports());
    if (it != i->getSymtab().end()) {
        m_ref = m_scope->getScopeSymbolPath(); // Path to 'i'

        // Now, add in the child element that we just found
        m_ref->getPath().push_back({ast::SymbolRefPathElemKind::ElemKind_ChildIdx, it->second});
    } else if (m_search_imp && i->getImports() && (m_ref=searchImports(m_id, i->getImports()))) {
        // Found in imports
    }

    DEBUG_LEAVE("visitSymbolScope");
}

void TaskResolveRootRef::visitSymbolExecScope(ast::ISymbolExecScope *i) {
    DEBUG_ENTER("visitSymbolExecScope");

    DEBUG_LEAVE("visitSymbolExecScope");
}

void TaskResolveRootRef::visitSymbolTypeScope(ast::ISymbolTypeScope *i) {
    DEBUG_ENTER("visitSymbolTypeScope %s", i->getName().c_str());
    visitSymbolScope(i); // Look in primary declaration scope

    if (!m_ref && i->getPlist()) {
        std::map<std::string,int32_t>::const_iterator it;

        if ((it=i->getPlist()->getSymtab().find(m_id->getId())) != i->getPlist()->getSymtab().end()) {
            // Target is a parameter value
            m_ref = m_scope->getScopeSymbolPath();

            m_ref->getPath().push_back({
                ast::SymbolRefPathElemKind::ElemKind_ParamIdx, 
                it->second
            });
        }
    }

    if (!m_ref) {
        // Didn't find, so let's look elsewhere...
        // TODO: template parameters
        // TODO: 

    }

    DEBUG_LEAVE("visitSymbolTypeScope");
}

void TaskResolveRootRef::visitSymbolFunctionScope(ast::ISymbolFunctionScope *i) {
    DEBUG_ENTER("visitSymbolFunctionScope");

    DEBUG_LEAVE("visitSymbolFunctionScope");
}

ast::ISymbolRefPath *TaskResolveRootRef::searchImports(
    const ast::IExprId          *id,
    ast::ISymbolImportSpec      *imp) {
    DEBUG_ENTER("searchImports");
    ast::ISymbolRefPath *ret = 0;
	for (std::vector<ast::IPackageImportStmt *>::const_iterator
		imp_it=imp->getImports().begin();
		imp_it!=imp->getImports().end(); imp_it++) {
        ast::ISymbolRefPath *ret_t = 0;
		if ((ret_t=searchImport(id, *imp_it))) {
			// Found it.
			if (ret) {
				// Uh-oh. We have ambiguity...
				std::string msg = "Ambiguous symbol resolution when looking up ";
				msg += id->getId();
                if (!m_marker) {
                    m_marker = IMarkerUP(m_factory->mkMarker("", MarkerSeverityE::Error, {-1,-1,-1}));
                }
                m_marker->setMsg(msg);
                m_marker->setSeverity(MarkerSeverityE::Error);
                m_marker->setMsg(msg);
                m_marker->setLocation(id->getLocation());
				m_marker_l->marker(m_marker.get());
				delete ret_t;
				break;
			} else {
				ret = ret_t;
			}
		}
    }

    DEBUG_LEAVE("searchImports %p", ret);
    return ret;
}

ast::ISymbolRefPath *TaskResolveRootRef::searchImport(
        const ast::IExprId          *id,
        ast::IPackageImportStmt     *imp) {
	DEBUG_ENTER("searchImport %s", id->getId().c_str());
    ast::ISymbolRefPath *ret = 0;

	// ast::ISymbolRefPath *ret = 0;
	if (!imp->getPath()->getTarget()) {
		DEBUG("Skipping, due to unset import target");
		return 0;
	}
	for (uint32_t i=0; i<imp->getPath()->getTarget()->getPath().size(); i++) {
		DEBUG("Imp Path[%d] %d", i, imp->getPath()->getTarget()->getPath().at(i));
	}
	ast::IScopeChild *target_c = m_scope->resolveAbsPath(imp->getPath()->getTarget());
	ast::ISymbolScope *target_s = dynamic_cast<ast::ISymbolScope *>(target_c);
	DEBUG("target_c: %p ; target_s: %p", target_c, target_s);

	if (target_s) {
		DEBUG("Have a symbol scope (%s)", target_s->getName().c_str());
		std::map<std::string, int32_t>::const_iterator it;
		it = target_s->getSymtab().find(id->getId());

		if (it != target_s->getSymtab().end()) {
			DEBUG("Found the symbol (%s)", id->getId().c_str());
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

	DEBUG_LEAVE("searchImport %s", id->getId().c_str());
	return ret;
}

dmgr::IDebug *TaskResolveRootRef::m_dbg = 0;

}
}
