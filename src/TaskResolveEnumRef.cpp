/*
 * TaskResolveEnumRef.cpp
 *
 * Copyright 2023 Matthew Ballance and Contributors
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
#include "TaskResolveEnumRef.h"


namespace zsp {
namespace parser {


TaskResolveEnumRef::TaskResolveEnumRef(IFactory *factory) {
    DEBUG_INIT("zsp::parser::TaskResolveEnumRef", factory->getDebugMgr());

}

TaskResolveEnumRef::~TaskResolveEnumRef() {

}

ast::ISymbolRefPath *TaskResolveEnumRef::resolve(
        ISymbolTableIterator            *scope,
        const ast::IExprId              *id) {
    DEBUG_ENTER("resolve");
    m_scope = scope;
    m_id = id;
    m_ref = 0;

    for (std::vector<ast::IScopeChild *>::const_iterator
        it=scope->getScope()->getChildren().begin();
        it!=scope->getScope()->getChildren().end(); it++) {
        (*it)->accept(m_this);
    }

    DEBUG_LEAVE("resolve");
    return m_ref;
}

void TaskResolveEnumRef::visitSymbolEnumScope(ast::ISymbolEnumScope *i) {
    DEBUG_ENTER("visitSymbolEnumScope %s (looking for %s)", 
        i->getName().c_str(),
        m_id->getId().c_str());
    std::map<std::string, int32_t>::const_iterator it = 
        i->getSymtab().find(m_id->getId());
    if (it != i->getSymtab().end()) {
        DEBUG("Found symbol %s", m_id->getId().c_str());
        m_ref = m_scope->getScopeSymbolPath();

        m_ref->getPath().push_back({
            ast::SymbolRefPathElemKind::ElemKind_ChildIdx, 
            i->getId()
        });

        m_ref->getPath().push_back({
            ast::SymbolRefPathElemKind::ElemKind_ChildIdx, 
            it->second
        });
        DEBUG("Path");
        for (std::vector<ast::SymbolRefPathElem>::const_iterator
            it=m_ref->getPath().begin();
            it!=m_ref->getPath().end(); it++) {
            DEBUG("  Elem: %d", it->idx);
        }
        fflush(stdout);
    }
    for (std::vector<ast::IScopeChild *>::const_iterator
        it=i->getChildren().begin();
        it!=i->getChildren().end(); it++) {
        (*it)->accept(m_this);
    }
    DEBUG_LEAVE("visitSymbolEnumScope %s", i->getName().c_str());
}

dmgr::IDebug *TaskResolveEnumRef::m_dbg = 0;

}
}
