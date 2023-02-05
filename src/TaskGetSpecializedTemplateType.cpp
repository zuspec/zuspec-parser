/*
 * TaskGetSpecializedTemplateType.cpp
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
#include "TaskGetSpecializedTemplateType.h"
#include "zsp/parser/impl/TaskCopyAst.h"
#include "zsp/parser/impl/TaskResolveSymbolPathRef.h"
#include "TaskBuildSymbolTree.h"
#include "TaskCompareParamLists.h"
#include "TaskResolveRefs.h"


namespace zsp {
namespace parser {


TaskGetSpecializedTemplateType::TaskGetSpecializedTemplateType(
    ast::ISymbolScope       *root,
    IFactory                *factory,
    IMarkerListener         *marker_l) : 
        m_root(root), m_factory(factory), m_marker_l(marker_l) {
    DEBUG_INIT("TaskGetSpecializedTemplateType", factory->getDebugMgr());

}

TaskGetSpecializedTemplateType::~TaskGetSpecializedTemplateType() {

}

ast::ISymbolRefPath *TaskGetSpecializedTemplateType::find(
    const ast::ISymbolRefPath           *type,
    const ast::ITemplateParamDeclList   *params) {
    DEBUG_ENTER("find");
    ast::ISymbolTypeScope *type_up = 
        TaskResolveSymbolPathRef(m_root).resolveT<ast::ISymbolTypeScope>(type);

    ast::ISymbolRefPath *ret = 0;

    // Search through the list of available specializations for
    // a matching one
    TaskCompareParamLists p_comp(m_factory->getDebugMgr());
    for (int32_t i=0; i<type_up->getSpec_types().size(); i++) {
        ast::ISymbolTypeScope *sym_type_s_t = type_up->getSpec_types().at(i).get();
        ast::ITypeScope *type_s_t = dynamic_cast<ast::ITypeScope  *>(sym_type_s_t->getTarget());

        if (p_comp.equal(params, type_s_t->getParams())) {
            // Have a match!
            ret = m_factory->getAstFactory()->mkSymbolRefPath();

            // Copy over initial path
            ret->getPath().insert(
                ret->getPath().begin(),
                type->getPath().begin(),
                type->getPath().end());
            
            // Now, add on a directive to get a specialization
            ret->getPath().push_back({
                ast::SymbolRefPathElemKind::ElemKind_TypeSpec,
                i
            });
            break;
        }
    }

    DEBUG_LEAVE("find %p", ret);
    return ret;
}

ast::ISymbolRefPath *TaskGetSpecializedTemplateType::mk(
    const ast::ISymbolRefPath           *type,
    ast::ITemplateParamDeclList         *params) {
    DEBUG_ENTER("mk params=%p", params);
    ast::ISymbolTypeScope *type_up = 
        TaskResolveSymbolPathRef(m_root).resolveT<ast::ISymbolTypeScope>(type);

    TaskCopyAst copier(m_factory->getAstFactory());

    ast::ITypeScope *type_s = 
        copier.copyT<ast::ITypeScope>(type_up->getTarget());

    // Replace the declaration parameter list with the properly-parameterized one
    // Note: UP takes care of freeing previous
    type_s->setParams(params);

    // We must now build a symbolscope node for the type scope
    ast::ISymbolTypeScope *type_ss = TaskBuildSymbolTree(
        m_factory->getDebugMgr(),
        m_factory->getAstFactory(),
        0).build(type_s);

    // Store the specialized AST under the symbol table
    type_ss->getOwned().push_back(ast::IScopeChildUP(type_s));

    int32_t id = type_up->getSpec_types().size();
    type_up->getSpec_types().push_back(ast::ISymbolTypeScopeUP(type_ss));

    TaskResolveRefs(
        m_factory->getDebugMgr(),
        m_factory,
        m_marker_l).resolve(type_ss);

    ast::ISymbolRefPath *ret = m_factory->getAstFactory()->mkSymbolRefPath();

    // Copy over initial path
    ret->getPath().insert(
        ret->getPath().begin(),
        type->getPath().begin(),
        type->getPath().end());
            
    // Now, add on a directive to get the new specialization
    ret->getPath().push_back({
        ast::SymbolRefPathElemKind::ElemKind_TypeSpec,
        id
    });
    
    DEBUG_LEAVE("mk %p", ret);

    return ret;
}

dmgr::IDebug *TaskGetSpecializedTemplateType::m_dbg = 0;

}
}
