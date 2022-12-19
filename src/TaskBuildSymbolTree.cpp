/*
 * TaskBuildSymbolTree.cpp
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
#include "TaskBuildSymbolTree.h"

#define DEBUG_ENTER(fmt, ...) \
	fprintf(stdout, "--> TaskBuildSymbolTree::"); \
	fprintf(stdout, fmt, ##__VA_ARGS__); \
	fprintf(stdout, "\n");

#define DEBUG(fmt, ...) \
	fprintf(stdout, "TaskBuildSymbolTree: "); \
	fprintf(stdout, fmt, ##__VA_ARGS__); \
	fprintf(stdout, "\n");

#define DEBUG_LEAVE(fmt, ...) \
	fprintf(stdout, "<-- TaskBuildSymbolTree::"); \
	fprintf(stdout, fmt, ##__VA_ARGS__); \
	fprintf(stdout, "\n");

namespace zsp {


TaskBuildSymbolTree::TaskBuildSymbolTree(
    ast::IFactory               *factory,
    IMarkerListener             *marker_l) :
    m_factory(factory), m_marker_l(marker_l) {

}

TaskBuildSymbolTree::~TaskBuildSymbolTree() {

}

ast::ISymbolScope *TaskBuildSymbolTree::build(
        const std::vector<ast::IGlobalScope *>  &roots) {
    DEBUG_ENTER("build");
    ast::ISymbolScope *root = m_factory->mkSymbolScope(
        -1,
        "");
    m_scope_s.push_back(root);

    for (std::vector<ast::IGlobalScope *>::const_iterator
        it=roots.begin();
        it!=roots.end(); it++) {
        for (std::vector<ast::IScopeChildUP>::const_iterator
            c_it=(*it)->getChildren().begin();
            c_it!=(*it)->getChildren().end(); c_it++) {
            (*c_it)->accept(this);
        }
    }

    m_scope_s.pop_back();

    DEBUG_LEAVE("build");
    return root;
}

void TaskBuildSymbolTree::visitPackageScope(ast::IPackageScope *i) {
    DEBUG_ENTER("visitPackageScope");
    for (std::vector<ast::IExprIdUP>::const_iterator
        id_it=i->getId().begin();
        id_it!=i->getId().end(); id_it++) {
        DEBUG("  process name-elem %s", (*id_it)->getId().c_str());
        ast::ISymbolScope *scope = 
            dynamic_cast<ast::ISymbolScope *>(m_scope_s.back());
        std::map<std::string,int32_t>::const_iterator p_it;
        p_it = scope->getSymtab().find((*id_it)->getId());

        if (p_it == scope->getSymtab().end()) {
            int32_t id = scope->getChildren().size();
            ast::ISymbolScope *pkg = 
                m_factory->mkSymbolScope(id, (*id_it)->getId());

            fprintf(stdout, "Add package %s with id %d\n", (*id_it)->getId().c_str(), id);
            scope->getSymtab().insert({(*id_it)->getId(), id});
            scope->getChildren().push_back(pkg);
            scope->getOwned().push_back(ast::IScopeChildUP(pkg));
            m_scope_s.push_back(pkg);
            scope = pkg;
        } else {
            ast::ISymbolScope *new_scope = 
                dynamic_cast<ast::ISymbolScope *>(scope->getChildren().at(p_it->second));
            m_scope_s.push_back(new_scope);
            scope = new_scope;
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
    DEBUG_LEAVE("visitPackageScope");
}

void TaskBuildSymbolTree::visitEnumDecl(ast::IEnumDecl *i) {
    DEBUG_ENTER("visitEnumDecl %s", i->getName()->getId().c_str());
    ast::ISymbolScope *scope = m_scope_s.back();

    int32_t id = scope->getChildren().size();
    ast::ISymbolScope *ts = m_factory->mkSymbolScope(
        id,
        i->getName()->getId());

    std::map<std::string, int32_t>::const_iterator it =
        scope->getSymtab().find(i->getName()->getId());

    if (it != scope->getSymtab().end()) {
        reportDuplicateSymbol(
            scope,
            scope->getChildren().at(it->second),
            i);
    } else {
        scope->getSymtab().insert({i->getName()->getId(), id});
        scope->getChildren().push_back(ts);
        scope->getOwned().push_back(ast::IScopeChildUP(ts));

        m_scope_s.push_back(ts);
        for (std::vector<ast::IEnumItemUP>::const_iterator
            it=i->getItems().begin();
            it!=i->getItems().end(); it++) {
            (*it)->accept(this);
        }
        m_scope_s.pop_back();
    }
    DEBUG_LEAVE("visitEnumDecl %s", i->getName()->getId().c_str());
}

void TaskBuildSymbolTree::visitEnumItem(ast::IEnumItem *i) {
    DEBUG_ENTER("visitEnumItem %s", i->getName()->getId().c_str());
    ast::ISymbolScope *scope = m_scope_s.back();

    std::map<std::string, int32_t>::const_iterator it =
        scope->getSymtab().find(i->getName()->getId());
    if (it != scope->getSymtab().end()) {
        reportDuplicateSymbol(
            scope,
            scope->getChildren().at(it->second),
            i
        );
    } else {
        int32_t id = scope->getChildren().size();
        scope->getSymtab().insert({i->getName()->getId(), id});
        scope->getChildren().push_back(i);
    }
    DEBUG_LEAVE("visitEnumItem %s", i->getName()->getId().c_str());
}

void TaskBuildSymbolTree::visitPackageImportStmt(ast::IPackageImportStmt *i) {
    DEBUG_ENTER("visitPackageImportStmt");
    ast::ISymbolScope *scope = m_scope_s.back();

    if (!scope->getImports()) {
        scope->setImports(m_factory->mkSymbolImportSpec());
    }

    scope->getImports()->getImports().push_back(i);

    DEBUG_LEAVE("visitPackageImportStmt");
}

void TaskBuildSymbolTree::visitScopeChild(ast::IScopeChild *i) {
    DEBUG_ENTER("visitScopeChild");
    m_scope_s.back()->getChildren().push_back(i);
    DEBUG_LEAVE("visitScopeChild");
}

void TaskBuildSymbolTree::visitTypeScope(ast::ITypeScope *i) {
    DEBUG_ENTER("visitTypeScope %s", i->getName()->getId().c_str());
    ast::ISymbolScope *scope = m_scope_s.back();

    int32_t id = scope->getChildren().size();
    ast::ISymbolScope *plist = 0;
    ast::ISymbolTypeScope *ts = m_factory->mkSymbolTypeScope(
        id,
        i->getName()->getId(),
        plist);

    std::map<std::string, int32_t>::const_iterator it =
        scope->getSymtab().find(i->getName()->getId());
    
    if (it != scope->getSymtab().end()) {
        reportDuplicateSymbol(
            scope,
            scope->getChildren().at(it->second),
            i
        );
    } else {
        scope->getSymtab().insert({i->getName()->getId(), id});
        scope->getChildren().push_back(ts);
        scope->getOwned().push_back(ast::IScopeChildUP(ts));

        m_scope_s.push_back(ts);
        for (std::vector<ast::IScopeChildUP>::const_iterator
            it=i->getChildren().begin();
            it!=i->getChildren().end(); it++) {
            (*it)->accept(this);
        }
        m_scope_s.pop_back();
    }
    DEBUG_LEAVE("visitTypeScope %s", i->getName()->getId().c_str());
}

void TaskBuildSymbolTree::reportDuplicateSymbol(
        ast::ISymbolScope       *scope,
        ast::IScopeChild        *orig,
        ast::IScopeChild        *dup) {
    fprintf(stdout, "Error: duplicate declaration");
}

}
