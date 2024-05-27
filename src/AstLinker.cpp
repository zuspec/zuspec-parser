/*
 * AstLinker.cpp
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
#include "zsp/parser/impl/TaskCloneSymbolScope.h"
#include "AstLinker.h"
#include "ResolveContext.h"
#include "TaskApplyOverlay.h"
#include "TaskApplyTypeExtensions.h"
#include "TaskBuildSymbolTree.h"
#include "TaskResolveRefsOverlay.h"
#include "TaskResolveRefs.h"


namespace zsp {
namespace parser {



AstLinker::AstLinker(
    dmgr::IDebugMgr     *dmgr,
    IFactory            *factory) : m_dmgr(dmgr), m_factory(factory) {
    DEBUG_INIT("AstLinker", dmgr);
    m_ast_factory = m_factory->getAstFactory();
}

AstLinker::~AstLinker() {

}

ast::IRootSymbolScope *AstLinker::link(
        IMarkerListener                         *marker_l,
        const std::vector<ast::IGlobalScope *>  &scopes) {
    ast::IRootSymbolScope *symtree = TaskBuildSymbolTree(
        m_dmgr,
        m_ast_factory,
        marker_l).build(scopes);

    // Now, apply type extension
    TaskApplyTypeExtensions(m_dmgr, m_factory, marker_l).apply(symtree);

    // Finally, resolve remaining names

    ResolveContext ctxt(m_factory, marker_l, symtree);
    TaskResolveRefs(&ctxt).resolve(symtree);

    return symtree;
}

ast::IRootSymbolScope *AstLinker::linkOverlay(
        IMarkerListener                         *marker_l,
        ast::IRootSymbolScope                   *base_symtab,
        ast::IGlobalScope                       *overlay) {
    DEBUG_ENTER("linkOverlay");
    // First, clone the base symbol table
    ast::IRootSymbolScope *root = TaskCloneSymbolScope(
        m_dmgr, m_ast_factory).clone(base_symtab);

    ResolveContext ctxt(m_factory, marker_l, root);

    TaskApplyOverlay(m_dmgr).apply(
        root,
        overlay);

    TaskResolveRefsOverlay(&ctxt).resolve(overlay);

    // Match overlay with original files base fileId

    // Apply the overlay files to the newly-cloned root,
    // replacing symbol-table references to files whose
    // content will be overlaid

    // Now, resolve symbols just in the overlay files

    DEBUG_LEAVE("linkOverlay");
    return root;
}

dmgr::IDebug *AstLinker::m_dbg = 0;

}
}
