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
#include "dmgr/impl/DebugMacros.h"
#include "BuiltinsFactory.h"
#include "TaskBuildSymbolTree.h"

namespace zsp {
namespace parser {



TaskBuildSymbolTree::TaskBuildSymbolTree(
    dmgr::IDebugMgr             *dmgr,
    ast::IFactory               *factory,
    IMarkerListener             *marker_l) :
    m_factory(factory), m_marker_l(marker_l) {
    DEBUG_INIT("TaskBuildSymbolTree", dmgr);

}

TaskBuildSymbolTree::~TaskBuildSymbolTree() {

}

ast::ISymbolScope *TaskBuildSymbolTree::build(
        const std::vector<ast::IGlobalScope *>  &roots) {
    DEBUG_ENTER("build");
    ast::ISymbolScope *root = m_factory->mkSymbolScope("");
    pushSymbolScope(root);

    DEBUG_ENTER("visitBuiltins");
    ast::IGlobalScope *builtins = BuiltinsFactory(m_factory).build();
    for (std::vector<ast::IScopeChildUP>::const_iterator
        c_it=builtins->getChildren().begin();
        c_it!=builtins->getChildren().end(); c_it++) {
        (*c_it)->accept(this);
    }
    DEBUG_LEAVE("visitBuiltins");

    for (std::vector<ast::IGlobalScope *>::const_iterator
        it=roots.begin();
        it!=roots.end(); it++) {
        for (std::vector<ast::IScopeChildUP>::const_iterator
            c_it=(*it)->getChildren().begin();
            c_it!=(*it)->getChildren().end(); c_it++) {
            (*c_it)->accept(this);
        }
    }

    popSymbolScope();

    DEBUG_LEAVE("build");
    return root;
}

void TaskBuildSymbolTree::visitActivityDecl(ast::IActivityDecl *i) {
    DEBUG_ENTER("visitActivityDecl");
    addChild(i, false);
    DEBUG_LEAVE("visitActivityDecl");
}

ast::ISymbolTypeScope *TaskBuildSymbolTree::build(ast::ITypeScope *ts) {
    DEBUG_ENTER("build");
    ast::ISymbolTypeScope *ret = 0;
    ast::ISymbolScope *root = m_factory->mkSymbolScope("");
    root->setLocation(ts->getLocation());
    root->setOpaque(ts->getOpaque());
    pushSymbolScope(root);

    ts->accept(m_this);

    popSymbolScope();

    ret = dynamic_cast<ast::ISymbolTypeScope *>(root->getChildren().at(0).get());
    root->getChildren().at(0).release();

    DEBUG_LEAVE("build");
    return ret;
}

void TaskBuildSymbolTree::visitConstraintBlock(ast::IConstraintBlock *i) {
    DEBUG_ENTER("visitConstraintBlock");
    addChild(i, false);
    DEBUG_LEAVE("visitConstraintBlock");
}
    
void TaskBuildSymbolTree::visitConstraintStmt(ast::IConstraintStmt *i) {
    DEBUG_ENTER("visitConstraintStmt");
    addChild(i, false);
    DEBUG_LEAVE("visitConstraintStmt");
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
            ast::ISymbolScope *pkg = m_factory->mkSymbolScope((*id_it)->getId());
            pkg->setLocation(i->getLocation());
            addChild(pkg, (*id_it)->getId());

            pushSymbolScope(pkg);
            scope = pkg;
        } else {
            ast::ISymbolScope *new_scope = 
                dynamic_cast<ast::ISymbolScope *>(scope->getChildren().at(p_it->second).get());
            new_scope->setUpper(symbolScope());
            pushSymbolScope(new_scope);
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
        popSymbolScope();
    }
    DEBUG_LEAVE("visitPackageScope");
}

void TaskBuildSymbolTree::visitEnumDecl(ast::IEnumDecl *i) {
    DEBUG_ENTER("visitEnumDecl %s", i->getName()->getId().c_str());
    ast::ISymbolScope *scope = symbolScope();

    int32_t id = scope->getChildren().size();
    ast::ISymbolEnumScope *ts = m_factory->mkSymbolEnumScope(i->getName()->getId());
    ts->setLocation(i->getLocation());


    if (addChild(ts, i->getName()->getId())) {
        pushSymbolScope(ts);
        for (std::vector<ast::IEnumItemUP>::const_iterator
            it=i->getItems().begin();
            it!=i->getItems().end(); it++) {
            (*it)->accept(this);
        }
        popSymbolScope();
    }
    DEBUG_LEAVE("visitEnumDecl %s", i->getName()->getId().c_str());
}

void TaskBuildSymbolTree::visitEnumItem(ast::IEnumItem *i) {
    DEBUG_ENTER("visitEnumItem %s", i->getName()->getId().c_str());
    addChild(i, i->getName()->getId());
    DEBUG_LEAVE("visitEnumItem %s", i->getName()->getId().c_str());
}

void TaskBuildSymbolTree::visitExecStmt(ast::IExecStmt *i) {
    DEBUG_ENTER("visitExecStmt");
    addChild(i, false);
    DEBUG_LEAVE("visitExecStmt");
}

void TaskBuildSymbolTree::visitExecBlock(ast::IExecBlock *i) {
    DEBUG_ENTER("visitExecBlock");
    visitExecScope(i);
    DEBUG_LEAVE("visitExecBlock");
}

void TaskBuildSymbolTree::visitExecScope(ast::IExecScope *i) {
    DEBUG_ENTER("visitExecScope");
    ast::ISymbolScope *scope = m_factory->mkSymbolExecScope("<inner-exec>");
    scope->setLocation(i->getLocation());
    scope->setTarget(i);
    addChild(scope, true);
    DEBUG("Adding to scope %s", (symbolScope())?symbolScope()->getName().c_str():"<null>");

    m_scope_s.push_back(scope);
    for (std::vector<ast::IExecStmtUP>::const_iterator
        it=i->getChildren().begin();
        it!=i->getChildren().end(); it++) {
        (*it)->accept(m_this);
    }
    m_scope_s.pop_back();

    DEBUG_LEAVE("visitExecScope");
}

void TaskBuildSymbolTree::visitExtendType(ast::IExtendType *i) {
    DEBUG_ENTER("visitExtendType");
    ast::ISymbolExtendScope *ext = m_factory->mkSymbolExtendScope("");
    ext->setLocation(i->getLocation());
    ext->setTarget(i);

    addChild(i, false);

    pushSymbolScope(ext);
    for (std::vector<ast::IScopeChildUP>::const_iterator
        it=i->getChildren().begin();
        it!=i->getChildren().end(); it++) {
        (*it)->accept(this);
    }
    popSymbolScope();

    DEBUG_LEAVE("visitExtendType");
}

void TaskBuildSymbolTree::visitField(ast::IField *i) {
    DEBUG_ENTER("visitField %s", i->getName()->getId().c_str());

    addChild(i, i->getName()->getId());

    DEBUG_LEAVE("visitField %s", i->getName()->getId().c_str());
}

void TaskBuildSymbolTree::visitFieldCompRef(ast::IFieldCompRef *i) {
    DEBUG_ENTER("visitFieldCompRef %s", i->getName()->getId().c_str());
    addChild(i, i->getName()->getId());
    DEBUG_LEAVE("visitFieldCompRef %s", i->getName()->getId().c_str());
}

void TaskBuildSymbolTree::visitFunctionDefinition(ast::IFunctionDefinition *i) { 
    DEBUG_ENTER("visitFunctionDefinition %s", i->getProto()->getName()->getId().c_str());

    ast::IScopeChild *ex_func_b = findSymbol(i->getProto()->getName()->getId());
    ast::ISymbolFunctionScope *func_sym = dynamic_cast<ast::ISymbolFunctionScope *>(ex_func_b);

    // If the existing symbol isn't a FunctionScope, then we have
    // a duplicate symbol
    if (ex_func_b && !func_sym) {
        reportDuplicateSymbol(symbolScope(), ex_func_b, i);
        return;
    }

    // Otherwise, we need to create
    if (!func_sym) {
        DEBUG("mkSymbolFunctionScope %s (1)", i->getProto()->getName()->getId().c_str());
        func_sym = m_factory->mkSymbolFunctionScope(i->getProto()->getName()->getId());
        func_sym->setLocation(i->getLocation());
        addChild(func_sym, i->getProto()->getName()->getId());
        func_sym->getPrototypes().push_back(i->getProto());

        // Add parameters to the function symbol scope
        for (std::vector<ast::IFunctionParamDeclUP>::const_iterator
            it=i->getProto()->getParameters().begin();
            it!=i->getProto()->getParameters().end(); it++) {
            int32_t id = func_sym->getChildren().size();
            std::map<std::string, int32_t>::const_iterator sym_it =
                func_sym->getSymtab().find((*it)->getName()->getId());
            
            if (sym_it != func_sym->getSymtab().end()) {
                // Duplicate
                reportDuplicateSymbol(
                    func_sym,
                    func_sym->getChildren().at(sym_it->second).get(),
                    it->get());
            } else {
                DEBUG("Add parameter %s to function symtab", (*it)->getName()->getId().c_str());
                func_sym->getSymtab().insert({(*it)->getName()->getId(), id});
                func_sym->getChildren().push_back(ast::IScopeChildUP(it->get(), false));
            }
        }
    }

    if (func_sym->getDefinition()) {
        // TODO: Report duplicate function error
    }

    // Build the body (and subscopes) symbol scopes
    int32_t id = func_sym->getChildren().size();
    ast::ISymbolExecScope *body = m_factory->mkSymbolExecScope("");
    body->setLocation(i->getLocation());
    body->setUpper(symbolScope());
    pushSymbolScope(body);
    func_sym->setBody(body);
    func_sym->getChildren().push_back(ast::IScopeChildUP(body, false));
    DEBUG("Function body has %d statements", i->getBody()->getChildren().size());
    for (std::vector<ast::IExecStmtUP>::const_iterator
        it=i->getBody()->getChildren().begin();
        it!=i->getBody()->getChildren().end(); it++) {
        (*it)->accept(m_this);
    }
    popSymbolScope();

    func_sym->setDefinition(i);
    // Ensure that the definition takes the primary prototype location
    func_sym->getPrototypes().insert(
        func_sym->getPrototypes().begin(),
        i->getProto()
    );

    DEBUG_LEAVE("visitFunctionDefinition %s", i->getProto()->getName()->getId().c_str());
}

void TaskBuildSymbolTree::visitFunctionImportProto(ast::IFunctionImportProto *i) { 
    DEBUG_ENTER("visitFunctionImportProto %s", i->getProto()->getName()->getId().c_str());

    ast::IScopeChild *ex_func_b = findSymbol(i->getProto()->getName()->getId());
    ast::ISymbolFunctionScope *func_sym = dynamic_cast<ast::ISymbolFunctionScope *>(ex_func_b);

    // If the existing symbol isn't a FunctionScope, then we have
    // a duplicate symbol
    if (ex_func_b && !func_sym) {
        reportDuplicateSymbol(symbolScope(), ex_func_b, i);
        return;
    }

    // Otherwise, we need to create
    if (!func_sym) {
        DEBUG("mkSymbolFunctionScope %s (2)", i->getProto()->getName()->getId().c_str());
        func_sym = m_factory->mkSymbolFunctionScope(i->getProto()->getName()->getId());
        func_sym->setLocation(i->getLocation());
        addChild(func_sym, i->getProto()->getName()->getId());

        // Add parameters to the function symbol scope
        for (std::vector<ast::IFunctionParamDeclUP>::const_iterator
            it=i->getProto()->getParameters().begin();
            it!=i->getProto()->getParameters().end(); it++) {
            int32_t id = func_sym->getChildren().size();
            std::map<std::string, int32_t>::const_iterator sym_it =
                func_sym->getSymtab().find((*it)->getName()->getId());
            
            if (sym_it != func_sym->getSymtab().end()) {
                // Duplicate
                reportDuplicateSymbol(
                    func_sym,
                    func_sym->getChildren().at(sym_it->second).get(),
                    it->get());
            } else {
                func_sym->getSymtab().insert({(*it)->getName()->getId(), id});
                func_sym->getChildren().push_back(ast::IScopeChildUP(it->get(), false));
            }
        }
    }

    if (func_sym->getDefinition()) {
        // TODO: Cannot both define and import an implementation
    }

    i->getProto()->accept(m_this);

    if (i->getPlat() == ast::PlatQual::PlatQual_Solve) {
        i->getProto()->setIs_solve(true);
    }
    if (i->getPlat() == ast::PlatQual::PlatQual_Target) {
        i->getProto()->setIs_target(true);
    }

    DEBUG_LEAVE("visitFunctionImportProto %s", i->getProto()->getName()->getId().c_str());
}

void TaskBuildSymbolTree::visitFunctionImportType(ast::IFunctionImportType *i) { 
    DEBUG_ENTER("visitFunctionImportType");
    DEBUG("TODO: visitFunctionImportType");
    DEBUG_LEAVE("visitFunctionImportType");
}

void TaskBuildSymbolTree::visitFunctionPrototype(ast::IFunctionPrototype *i) { 
    DEBUG_ENTER("visitFunctionPrototype %s", i->getName()->getId().c_str());
    ast::IScopeChild *ex_func_b = findSymbol(i->getName()->getId());
    ast::ISymbolFunctionScope *func_sym = dynamic_cast<ast::ISymbolFunctionScope *>(ex_func_b);

    // If the existing symbol isn't a FunctionScope, then we have
    // a duplicate symbol
    if (ex_func_b && !func_sym) {
        DEBUG("Duplicate symbol");
        reportDuplicateSymbol(symbolScope(), ex_func_b, i);
        return;
    }

    // Otherwise, we need to create
    if (!func_sym) {
        DEBUG("mkSymbolFunctionScope %s (3)", i->getName()->getId().c_str());
        func_sym = m_factory->mkSymbolFunctionScope(i->getName()->getId());
        func_sym->setLocation(i->getLocation());
        addChild(func_sym, i->getName()->getId());
    } else {
        DEBUG("Note: Function %s is already defined", func_sym->getName().c_str());
    }

    func_sym->getPrototypes().push_back(i);
    DEBUG_LEAVE("visitFunctionPrototype %s", i->getName()->getId().c_str());
}

void TaskBuildSymbolTree::visitPackageImportStmt(ast::IPackageImportStmt *i) {
    DEBUG_ENTER("visitPackageImportStmt");
    ast::ISymbolScope *scope = symbolScope();

    if (!scope->getImports()) {
        DEBUG("Create new ImportSpec");
        scope->setImports(m_factory->mkSymbolImportSpec());
    }

    DEBUG("Add import to scope %s", scope->getName().c_str());

    scope->getImports()->getImports().push_back(i);

    DEBUG_LEAVE("visitPackageImportStmt");
}

void TaskBuildSymbolTree::visitPyImportStmt(ast::IPyImportStmt *i) {
    DEBUG_ENTER("visitPyImportStmt");
    ast::ISymbolScope *scope = symbolScope();
    std::map<std::string, int32_t>::const_iterator it;

    if (i->getAlias()) {
        // Register the alias name
        if ((it=scope->getSymtab().find(i->getAlias()->getId())) != scope->getSymtab().end()) {
            // Error: 
            ERROR("TODO: symbol collision with pyimport %s", i->getAlias()->getId().c_str());
        } else {
            int32_t id = scope->getChildren().size();
            scope->getChildren().push_back(ast::IScopeChildUP(i, false));
            scope->getSymtab().insert({
                i->getAlias()->getId(),
                id
            });
        }
    } else {
        // Register the basename
        if ((it=scope->getSymtab().find(i->getPath().front()->getId())) != scope->getSymtab().end()) {
            // Error: 
            ERROR("TODO: symbol collision with pyimport %s", i->getPath().front()->getId().c_str());
        } else {
            int32_t id = scope->getChildren().size();
            scope->getChildren().push_back(ast::IScopeChildUP(i, false));
            scope->getSymtab().insert({
                i->getPath().front()->getId(),
                id
            });
        }
    }
    DEBUG_LEAVE("visitPyImportStmt");
}

void TaskBuildSymbolTree::visitPyImportFromStmt(ast::IPyImportFromStmt *i) {
    DEBUG_ENTER("visitPyImportFromStmt");
    DEBUG("TODO: visitPyImportFromStmt");
    DEBUG_LEAVE("visitPyImportFromStmt");
}

void TaskBuildSymbolTree::visitProceduralStmtDataDeclaration(ast::IProceduralStmtDataDeclaration *i) {
    DEBUG_ENTER("visitProceduralStmtDataDeclaration %s", i->getName()->getId().c_str());
    ast::ISymbolExecScope *scope = dynamic_cast<ast::ISymbolExecScope *>(m_scope_s.back());

    std::map<std::string, int32_t>::const_iterator it =
        scope->getSymtab().find(i->getName()->getId());
    
    if (it != scope->getSymtab().end()) {
        reportDuplicateSymbol(
            scope,
            scope->getChildren().at(it->second).get(),
            i
        );
    } else {
        int32_t id = scope->getChildren().size();
        DEBUG("DataDeclaration %s: %d", i->getName()->getId().c_str(), id);
        scope->getSymtab().insert({i->getName()->getId(), id});
        scope->getChildren().push_back(ast::IScopeChildUP(i, false));
    }

    DEBUG_LEAVE("visitProceduralStmtDataDeclaration");
}

void TaskBuildSymbolTree::visitProceduralStmtIfElse(ast::IProceduralStmtIfElse *i) {
    DEBUG_ENTER("visitProceduralStmtIfElse");
    ast::ISymbolScope *scope = symbolScope();

    int32_t id = scope->getChildren().size();
//    ast::ISymbolChildrenScope *if_scope = m_factory->mkSymbolChildrenScope("<if>");
    ast::ISymbolScope *if_scope = m_factory->mkSymbolScope("<if>");
    if_scope->setLocation(i->getLocation());
    if_scope->setTarget(i);
    addChild(if_scope, true);
    pushSymbolScope(if_scope);
    for (std::vector<ast::IProceduralStmtIfClauseUP>::const_iterator
        it=i->getIf_then().begin();
        it!=i->getIf_then().end(); it++) {
        ast::ISymbolCondConnector *cc = m_factory->mkSymbolCondConnector((*it)->getCond(), 0);
        addChild(cc, true);
        pushSymbolScope(cc);
        (*it)->accept(m_this);
        popSymbolScope();
    }
    if (i->getElse_then()) {
        i->getElse_then()->accept(m_this);
    }
    popSymbolScope();

    DEBUG_LEAVE("visitProceduralStmtIfElse");
}

/*
void TaskBuildSymbolTree::visitProceduralStmtIfClause(ast::IProceduralStmtIfClause *i) {
    DEBUG_ENTER("visitProceduralStmtIfClause");
    DEBUG_LEAVE("visitProceduralStmtIfClause");
}
 */

void TaskBuildSymbolTree::visitScope(ast::IScope *i) {
    DEBUG_ENTER("visitScope");
    addChild(i, false);
    DEBUG_LEAVE("visitScope");
}

void TaskBuildSymbolTree::visitScopeChild(ast::IScopeChild *i) {
    DEBUG_ENTER("visitScopeChild");
    addChild(i, false);
    DEBUG_LEAVE("visitScopeChild");
}

void TaskBuildSymbolTree::visitTypeScope(ast::ITypeScope *i) {
    DEBUG_ENTER("visitTypeScope %s", i->getName()->getId().c_str());
    ast::ISymbolScope *scope = symbolScope();

    ast::ISymbolScope *plist = 0;
    if (i->getParams()) {
        DEBUG("Build out plist %d", i->getParams()->getParams().size());
        plist = m_factory->mkSymbolScope("");
        for (std::vector<ast::ITemplateParamDeclUP>::const_iterator
            it=i->getParams()->getParams().begin();
            it!=i->getParams()->getParams().end(); it++) {
            int32_t id = plist->getChildren().size();
            std::map<std::string, int32_t>::const_iterator s_it;
            DEBUG("  Param: %", (*it)->getName()->getId().c_str());
            
            s_it = plist->getSymtab().find((*it)->getName()->getId());
            if (s_it == plist->getSymtab().end()) {
                plist->getChildren().push_back(ast::IScopeChildUP(it->get(), false));
                plist->getSymtab().insert({(*it)->getName()->getId(), id});
            } else {
                // TODO: Find a proper way to report
                fprintf(stdout, "Error: duplicate parameter name\n");
            }
        }
    } else {
        DEBUG("No plist");
    }
    ast::ISymbolTypeScope *ts = m_factory->mkSymbolTypeScope(i->getName()->getId(), plist);
    ts->setLocation(i->getLocation());
    ts->setTarget(i);

    // pyobj fields are opaque, since Python is a dynamically-typed library
    if (i->getName()->getId() == "pyobj") {
        ts->setOpaque(true);
    }

    if (addChild(ts, i->getName()->getId())) {
        pushSymbolScope(ts);

        for (std::vector<ast::IScopeChildUP>::const_iterator
            it=i->getChildren().begin();
            it!=i->getChildren().end(); it++) {
            (*it)->accept(m_this);
        }
        popSymbolScope();
    }

    DEBUG_LEAVE("visitTypeScope %s", i->getName()->getId().c_str());
}

void TaskBuildSymbolTree::reportDuplicateSymbol(
        ast::ISymbolScope       *scope,
        ast::IScopeChild        *orig,
        ast::IScopeChild        *dup) {
    fprintf(stdout, "Error: duplicate declaration");
}

ast::IScopeChild *TaskBuildSymbolTree::findSymbol(const std::string &name) {
    ast::ISymbolScope *scope = symbolScope();
    if (scope) {
        std::map<std::string, int32_t>::const_iterator it =
            scope->getSymtab().find(name);
        if (it != scope->getSymtab().end()) {
            return scope->getChildren().at(it->second).get();
        } else {
            return 0;
        }
    } else {
        return 0;
    }
}

void TaskBuildSymbolTree::pushSymbolScope(ast::ISymbolChild *s) {
    m_scope_s.push_back(s);
}

ast::ISymbolScope *TaskBuildSymbolTree::symbolScope() {
    if (m_scope_s.size()) {
        return dynamic_cast<ast::ISymbolScope *>(m_scope_s.back());
    } else {
        return 0;
    }
}

void TaskBuildSymbolTree::popSymbolScope() {
    m_scope_s.pop_back();
}

void TaskBuildSymbolTree::addChild(
    ast::IScopeChild    *c,
    bool                owned) {
    DEBUG_ENTER("addChild(ScopeChild");
    if (dynamic_cast<ast::ISymbolChildrenScope *>(m_scope_s.back())) {
        dynamic_cast<ast::ISymbolChildrenScope *>(m_scope_s.back())->getChildren().push_back(
            ast::IScopeChildUP(c, owned));
    } else {
        ast::ISymbolCondConnector *cond = dynamic_cast<ast::ISymbolCondConnector *>(m_scope_s.back());
        DEBUG("Setting cond-connector target");
        cond->setStmt(c);
    }
    DEBUG_LEAVE("addChild(ScopeChild");
}

bool TaskBuildSymbolTree::addChild(
    ast::IScopeChild    *c, 
    const std::string   &name,
    bool                owned) {
    ast::ISymbolScope *scope = symbolScope();
    if (c == scope) {
        ERROR("recursive");
    }
    std::map<std::string, int32_t>::const_iterator it =
        scope->getSymtab().find(name);
    
    if (it == scope->getSymtab().end()) {
        int32_t id = scope->getChildren().size();
        scope->getChildren().push_back(c);
        scope->getSymtab().insert({name, id});
        return true;
    } else {
        reportDuplicateSymbol(
            scope,
            scope->getChildren().at(it->second).get(),
            c);
        return false;
    }
}

bool TaskBuildSymbolTree::addChild(
    ast::ISymbolChild   *c, 
    const std::string   &name,
    bool                owned) {
    DEBUG_ENTER("addChild(SymbolChild");
    ast::ISymbolScope *scope = symbolScope();

    if (c == scope) {
        ERROR("recursive");
    }
    int32_t id = scope->getChildren().size();
    c->setId(id);
    if (name != "") {
        std::map<std::string, int32_t>::const_iterator it =
            scope->getSymtab().find(name);
        
        if (it != scope->getSymtab().end()) {
            reportDuplicateSymbol(
                scope,
                scope->getChildren().at(it->second).get(),
                c);
            return false;
        } else {
            scope->getSymtab().insert({name, id});
        }
    }
    scope->getChildren().push_back(ast::IScopeChildUP(c, owned));
    c->setUpper(scope);
    DEBUG_LEAVE("addChild(SymbolChild");
    return true;
}

dmgr::IDebug *TaskBuildSymbolTree::m_dbg = 0;

}
}
