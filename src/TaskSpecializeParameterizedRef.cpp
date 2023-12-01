/*
 * TaskSpecializeParameterizedRef.cpp
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
#include "zsp/parser/impl/TaskResolveSymbolPathRef.h"
#include "TaskSpecializeParameterizedRef.h"
#include "TaskGetSpecializedTemplateType.h"
#include "TaskBuildParamValList.h"


namespace zsp {
namespace parser {


TaskSpecializeParameterizedRef::TaskSpecializeParameterizedRef(
    ast::ISymbolScope       *root,
    IFactory                *factory,
    IMarkerListener         *marker_l) : 
        m_root(root), m_factory(factory), m_marker_l(marker_l) {
    DEBUG_INIT("zsp::parser::TaskSpecializeParameterizedRef", m_factory->getDebugMgr());
}

TaskSpecializeParameterizedRef::~TaskSpecializeParameterizedRef() {

}

ast::ISymbolRefPath *TaskSpecializeParameterizedRef::specialize(
        const parser::ISymbolTableIterator  *root_it,
        ast::ISymbolRefPath                 *target,
        ast::ITemplateParamValueList        *pvals) {
    DEBUG_ENTER("specialize");
    // Find the base type
    ast::IScopeChild *target_sc = TaskResolveSymbolPathRef(m_factory->getDebugMgr(), m_root).resolve(target);
    ast::ISymbolTypeScope *target_c = 
        TaskResolveSymbolPathRef(m_factory->getDebugMgr(), m_root).resolveT<ast::ISymbolTypeScope>(target);

    if (!target_c) {
        DEBUG("TODO: Flag error about templated type");
        return 0;
    }

    if (!target_c->getPlist()) {
        DEBUG("TODO: Flag type as not being templated");
        return 0;
    }

    DEBUG("target: %s", target_c->getName().c_str());

    // Form parameter list 
    ast::ITemplateParamDeclList *pdecl_list = TaskBuildParamValList(
        m_root, m_factory, m_marker_l).build(
            target_c->getPlist(),
            pvals);
    TaskGetSpecializedTemplateType typespec_getter(m_root, m_factory, m_marker_l);

    ast::ISymbolRefPath *target_t = typespec_getter.find(
        root_it,
        target, 
        pdecl_list);

    if (target_t) {
        // The new parameter list that we created is no longer needed
        DEBUG("Specialization already exists");
        delete pdecl_list;
    } else {
        DEBUG("Must create new specialization");
        target_t = typespec_getter.mk(
            root_it,
            target, 
            pdecl_list);
    }
    

    DEBUG_LEAVE("specialize %p", target_t);
    return target_t;
}

dmgr::IDebug *TaskSpecializeParameterizedRef::m_dbg = 0;

}
}
