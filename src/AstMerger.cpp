/*
 * AstMerger.cpp
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
#include "AstMerger.h"

namespace zsp {

AstMerger::AstMerger(ast::IFactory *factory) : m_factory(factory) {

}

AstMerger::~AstMerger() {

}

ast::IGlobalScope *AstMerger::merge(
        const std::vector<ast::IGlobalScope *> &asts) {
    ast::IGlobalScope *ret = m_factory->mkGlobalScope(0);
    Scope root(ret);
    m_scope_s.push_back(&root);

    for (std::vector<ast::IGlobalScope *>::const_iterator
        it_ast=asts.begin();
        it_ast!=asts.end(); it_ast++) {
        for (std::vector<ast::IScopeChildUP>::const_iterator
            it_c=(*it_ast)->getChildren().begin();
            it_c!=(*it_ast)->getChildren().end(); it_c++) {
            (*it_c)->accept(this);
        }
    }
    m_scope_s.pop_back();
    return ret;
}

void AstMerger::visitPackageScope(ast::IPackageScope *i) {
    for (std::vector<ast::IExprIdUP>::const_iterator
        id_it=i->getId().begin();
        id_it!=i->getId().end(); id_it++) {
        std::map<std::string,ScopeUP>::const_iterator p_it;
        p_it = m_scope_s.back()->subscope_m.find((*id_it)->getId());

        if (p_it == m_scope_s.back()->subscope_m.end()) {
            ast::IPackageScope *pkg = m_factory->mkPackageScope();
            pkg->getId().push_back(ast::IExprIdUP(
                m_factory->mkExprId(
                    (*id_it)->getId(),
                    (*id_it)->getIs_escaped())));
            Scope *s = new Scope(pkg);
            m_scope_s.back()->scope->getChildren().push_back(ast::IScopeUP(s->scope));
            m_scope_s.back()->subscope_m.insert({(*id_it)->getId(), ScopeUP(s)});
            m_scope_s.push_back(s);
        } else {
            m_scope_s.push_back(p_it->second.get());
        }
    }

    for (std::vector<ast::IScopeChildUP>::const_iterator
        it=i->getChildren().begin();
        it!=i->getChildren().end(); it++) {
        (*it)->accept(this);
    }

    for (std::vector<ast::IExprIdUP>::const_iterator
        id_it=i->getId().begin();
        id_it!=i->getId().end(); id_it++) {
        m_scope_s.pop_back();
    }
}

void AstMerger::visitScopeChild(ast::IScopeChild *i) {
    m_scope_s.back()->scope->getChildren().push_back(
        ast::IScopeChildUP(m_factory->mkScopeChildRef(i)));
}

}
