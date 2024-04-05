/**
 * TaskResolveSymbolPathRef.h
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
#pragma once
#include <vector>
#include "dmgr/impl/DebugMacros.h"
#include "dmgr/IDebugMgr.h"
#include "zsp/ast/ISymbolScope.h"
#include "zsp/ast/ISymbolRefPath.h"
#include "zsp/ast/ISymbolTypeScope.h"
#include "zsp/ast/impl/VisitorBase.h"
#include "zsp/parser/ISymbolTableIterator.h"
#include "zsp/parser/impl/TaskGetName.h"
#include "zsp/parser/impl/TaskResolveSymbolPathRefResult.h"

namespace zsp {
namespace parser {


class TaskResolveSymbolPathRef : public ast::VisitorBase {
public:
    TaskResolveSymbolPathRef(
        dmgr::IDebugMgr             *dmgr,
        ast::ISymbolChildrenScope   *root) : m_dbg(0), m_root(root) { 
        DEBUG_INIT("TaskResolveSymbolPathRef", dmgr);
    }

    virtual ~TaskResolveSymbolPathRef() { }

    ast::IScopeChild *resolve(const ast::ISymbolRefPath *ref) {
        DEBUG_ENTER("resolve root=%p", m_root);
        ast::IScopeChild *ret = 0;
        ast::ISymbolChildrenScope *scope = m_root;

        for (std::vector<ast::SymbolRefPathElem>::const_iterator
            it=ref->getPath().begin();
            it!=ref->getPath().end(); it++) {
            DEBUG("Path: %d %d", it->kind, it->idx);
        }

        for (std::vector<ast::SymbolRefPathElem>::const_iterator
            it=ref->getPath().begin();
            it!=ref->getPath().end(); it++) {
            
            switch (it->kind) {
                case ast::SymbolRefPathElemKind::ElemKind_ChildIdx: {
                    DEBUG("Elem: ChildIdx %d", it->idx);
                    ret = scope->getChildren().at(it->idx).get();
                    DEBUG("  scope %p => %p", scope, ret);
                } break;
                case ast::SymbolRefPathElemKind::ElemKind_ArgIdx: {
                    DEBUG("Elem: ArgIdx %d", it->idx);
                    ast::ISymbolFunctionScope *fs = dynamic_cast<ast::ISymbolFunctionScope *>(scope);
                    ret = fs->getPlist()->getChildren().at(it->idx).get();
                } break;
                case ast::SymbolRefPathElemKind::ElemKind_ParamIdx: {
                    DEBUG("Elem: ParamIdx %d", it->idx);
                    ast::ISymbolTypeScope *scope_ts = dynamic_cast<ast::ISymbolTypeScope *>(scope);
                    ret = scope_ts->getPlist()->getChildren().at(it->idx).get();
                    DEBUG("  scope %p => %p", scope_ts, ret);
                } break;
                case ast::SymbolRefPathElemKind::ElemKind_Super: {
                    ast::ISymbolTypeScope *scope_ts = dynamic_cast<ast::ISymbolTypeScope *>(scope);
                    fprintf(stdout, "TODO: handle super ref\n");
                    fflush(stdout);
                } break;
                case ast::SymbolRefPathElemKind::ElemKind_TypeSpec: {
                    ast::ISymbolTypeScope *scope_ts = dynamic_cast<ast::ISymbolTypeScope *>(scope);
                    DEBUG("Elem: TypeSpec %d", it->idx);
                    DEBUG("Scope: %s (%d specializations)",
                        scope_ts->getName().c_str(),
                        scope_ts->getSpec_types().size());
                    ret = scope_ts->getSpec_types().at(it->idx).get();
                    DEBUG("  scope %p => %p", scope_ts, ret);
                } break;
                default:
                    fprintf(stdout, "TODO: handle ElemKind %d\n", it->kind);
                    fflush(stdout);
                    break;
            }
            
            if (it+1 != ref->getPath().end()) {
                scope = dynamic_cast<ast::ISymbolScope *>(ret);
            }

            if (!scope) {
                ERROR("Failed to get scope @ %d/%d",
                    (it-ref->getPath().begin()), ref->getPath().size());
                ret = 0;
                break;
            }
        }

        DEBUG_LEAVE("resolve");

        return ret;
    }

    template <class T> T *resolveT(const ast::ISymbolRefPath *ref) {
        return dynamic_cast<T *>(resolve(ref));
    }

    TaskResolveSymbolPathRefResult resolveFull(const ast::ISymbolRefPath *ref) {
        TaskResolveSymbolPathRefResult ret;

        ast::IScopeChild *ref_t = resolve(ref);
        m_ts = 0;
        m_ss = 0;
        m_dt = 0;
        ref_t->accept(m_this);

        if (m_ts) {
            ret.kind = TaskResolveSymbolPathRefResult::SymbolTypeScope;
            ret.val.ts = m_ts;
        } else if (m_ss) {
            ret.kind = TaskResolveSymbolPathRefResult::SymbolScope;
            ret.val.ss = m_ss;
        } else if (m_dt) {
            ret.kind = TaskResolveSymbolPathRefResult::DataType;
            ret.val.dt = m_dt;
        } else {
            fprintf(stdout, "ERROR: unhandled resolveFull case\n");
            *((uint32_t *)0) = 1;
        }
        return ret;
    }

    parser::ISymbolTableIterator *mkIterator(
            parser::ISymbolTableIterator    *ret,
            const ast::ISymbolRefPath       *ref) {
        DEBUG_ENTER("mkIterator root=%p", m_root);
        ast::ISymbolChildrenScope *scope = m_root;

        for (std::vector<ast::SymbolRefPathElem>::const_iterator
            it=ref->getPath().begin();
            it!=ref->getPath().end(); it++) {
            
            switch (it->kind) {
                case ast::SymbolRefPathElemKind::ElemKind_ChildIdx: {
                    DEBUG("Elem: ChildIdx %d", it->idx);
                    ast::IScopeChild *c = scope->getChildren().at(it->idx).get();
                    if ((scope=dynamic_cast<ast::ISymbolScope *>(c))) {
                        ret->pushScope(dynamic_cast<ast::ISymbolScope *>(scope));
                    } else {
                        break;
                    }
                    DEBUG("  scope %p => %p", scope, ret);
                } break;
                case ast::SymbolRefPathElemKind::ElemKind_ParamIdx: {
                    DEBUG("Elem: ParamIdx %d", it->idx);
//                    ast::ISymbolTypeScope *scope_ts = dynamic_cast<ast::ISymbolTypeScope *>(scope);
//                    ret = scope_ts->getPlist()->getChildren().at(it->idx);
//                    DEBUG("  scope %p => %p", scope_ts, ret);
                } break;
                case ast::SymbolRefPathElemKind::ElemKind_Super: {
                    ast::ISymbolTypeScope *scope_ts = dynamic_cast<ast::ISymbolTypeScope *>(scope);
                    fprintf(stdout, "TODO: handle super ref\n");
                    fflush(stdout);
                } break;
                case ast::SymbolRefPathElemKind::ElemKind_TypeSpec: {
                    ast::ISymbolTypeScope *scope_ts = dynamic_cast<ast::ISymbolTypeScope *>(scope);
                    DEBUG("Elem: TypeSpec %d", it->idx);
                    ast::ISymbolTypeScope *c = scope_ts->getSpec_types().at(it->idx).get();
                    ret->pushScope(c, ast::SymbolRefPathElemKind::ElemKind_TypeSpec);
                    scope = c;
                    DEBUG("  scope %p => %p", scope_ts, ret);
                } break;
                default:
                    fprintf(stdout, "TODO: handle ElemKind %d\n", it->kind);
                    fflush(stdout);
                    break;
            }
            
//            if (it+1 != ref->getPath().end()) {
//                scope = dynamic_cast<ast::ISymbolScope *>(ret);
//            }
        }

        DEBUG_LEAVE("mkIterator");

        return ret;
    }

    parser::ISymbolTableIterator *mkIterator(
            parser::ISymbolTableIterator    *ret,
            ast::ISymbolScope               *target) {
        DEBUG_ENTER("mkIterator root=%p", m_root);
        ast::ISymbolChildrenScope *scope = m_root;

        std::vector<ast::ISymbolScope *> scopes;

        ast::ISymbolScope *c = target;
        while (c && c != m_root) {
            DEBUG("Scope: %s", c->getName().c_str());
            scopes.push_back(c);
            c = c->getUpper();
        }

        for (std::vector<ast::ISymbolScope *>::const_reverse_iterator
            it=scopes.rbegin();
            it!=scopes.rend(); it++) {
            DEBUG("pushScope");
            if (dynamic_cast<ast::ISymbolTypeScope *>(*it)) {
                ast::ISymbolTypeScope *ts = dynamic_cast<ast::ISymbolTypeScope *>(*it);
                ast::ITypeScope *tst = dynamic_cast<ast::ITypeScope *>(ts->getTarget());
                if (tst->getParams()->getSpecialized()) {
                    ret->pushScope(dynamic_cast<ast::ISymbolScope *>(*it),
                        ast::SymbolRefPathElemKind::ElemKind_TypeSpec);
                } else {
                    ret->pushScope(dynamic_cast<ast::ISymbolScope *>(*it));
                }
            } else {
                ret->pushScope(dynamic_cast<ast::ISymbolScope *>(*it));
            }
        }

        DEBUG_LEAVE("mkIterator");

        return ret;
    }

    std::string mkName(
            const ast::ISymbolRefPath       *ref) {
        DEBUG_ENTER("mkName root=%p", m_root);
        std::string ret;
        ast::IScopeChild *item;
        ast::ISymbolChildrenScope *scope = m_root;

        for (std::vector<ast::SymbolRefPathElem>::const_iterator
            it=ref->getPath().begin();
            it!=ref->getPath().end(); it++) {
            
            switch (it->kind) {
                case ast::SymbolRefPathElemKind::ElemKind_ChildIdx: {
                    DEBUG("Elem: ChildIdx %d", it->idx);
                    item = scope->getChildren().at(it->idx).get();
                    ret = TaskGetName().get(item);
                    if (!(scope=dynamic_cast<ast::ISymbolScope *>(item))) {
                        break;
                    }
                } break;
                case ast::SymbolRefPathElemKind::ElemKind_ParamIdx: {
                    DEBUG("Elem: ParamIdx %d", it->idx);
//                    ast::ISymbolTypeScope *scope_ts = dynamic_cast<ast::ISymbolTypeScope *>(scope);
//                    ret = scope_ts->getPlist()->getChildren().at(it->idx);
//                    DEBUG("  scope %p => %p", scope_ts, ret);
                } break;
                case ast::SymbolRefPathElemKind::ElemKind_Super: {
                    ast::ISymbolTypeScope *scope_ts = dynamic_cast<ast::ISymbolTypeScope *>(scope);
                    fprintf(stdout, "TODO: handle super ref\n");
                    fflush(stdout);
                } break;
                case ast::SymbolRefPathElemKind::ElemKind_TypeSpec: {
                    ast::ISymbolTypeScope *scope_ts = dynamic_cast<ast::ISymbolTypeScope *>(scope);
                    DEBUG("Elem: TypeSpec %d", it->idx);
//                    ast::ISymbolTypeScope *c = scope_ts->getSpec_types().at(it->idx).get();
//                    ret->pushScope(c);
                    DEBUG("  scope %p => %p", scope_ts, ret.c_str());
                } break;
                default:
                    fprintf(stdout, "TODO: handle ElemKind %d\n", it->kind);
                    fflush(stdout);
                    break;
            }
            
//            if (it+1 != ref->getPath().end()) {
//                scope = dynamic_cast<ast::ISymbolScope *>(i);
//            }
        }

        DEBUG_LEAVE("mkName");

        return ret;
    }

    std::string mkQName(
            const ast::ISymbolRefPath       *ref) {
        DEBUG_ENTER("mkQName root=%p", m_root);
        std::string ret;
        ast::IScopeChild *item;
        ast::ISymbolChildrenScope *scope = m_root;

        for (std::vector<ast::SymbolRefPathElem>::const_iterator
            it=ref->getPath().begin();
            it!=ref->getPath().end(); it++) {
            
            switch (it->kind) {
                case ast::SymbolRefPathElemKind::ElemKind_ChildIdx: {
                    DEBUG("Elem: ChildIdx %d", it->idx);
                    item = scope->getChildren().at(it->idx).get();
                    if (ret.size()) {
                        ret += "::";
                    }
                    ret += TaskGetName().get(item);
                    if (!(scope=dynamic_cast<ast::ISymbolScope *>(item))) {
                        break;
                    }
                } break;
                case ast::SymbolRefPathElemKind::ElemKind_ParamIdx: {
                    DEBUG("Elem: ParamIdx %d", it->idx);
//                    ast::ISymbolTypeScope *scope_ts = dynamic_cast<ast::ISymbolTypeScope *>(scope);
//                    ret = scope_ts->getPlist()->getChildren().at(it->idx);
//                    DEBUG("  scope %p => %p", scope_ts, ret);
                } break;
                case ast::SymbolRefPathElemKind::ElemKind_Super: {
                    ast::ISymbolTypeScope *scope_ts = dynamic_cast<ast::ISymbolTypeScope *>(scope);
                    fprintf(stdout, "TODO: handle super ref\n");
                    fflush(stdout);
                } break;
                case ast::SymbolRefPathElemKind::ElemKind_TypeSpec: {
                    ast::ISymbolTypeScope *scope_ts = dynamic_cast<ast::ISymbolTypeScope *>(scope);
                    DEBUG("Elem: TypeSpec %d", it->idx);
//                    ast::ISymbolTypeScope *c = scope_ts->getSpec_types().at(it->idx).get();
//                    ret->pushScope(c);
                    DEBUG("  scope %p => %p", scope_ts, ret.c_str());
                } break;
                default:
                    fprintf(stdout, "TODO: handle ElemKind %d\n", it->kind);
                    fflush(stdout);
                    break;
            }
            
//            if (it+1 != ref->getPath().end()) {
//                scope = dynamic_cast<ast::ISymbolScope *>(i);
//            }
        }

        DEBUG_LEAVE("mkQName");

        return ret;
    }

    virtual void visitDataTypeBool(ast::IDataTypeBool *i) override {
        m_dt = i;
    }

    virtual void visitDataTypeChandle(ast::IDataTypeChandle *i) override {
        m_dt = i;
    }

    virtual void visitDataTypeEnum(ast::IDataTypeEnum *i) override {
        m_dt = i;
    }

    virtual void visitDataTypeInt(ast::IDataTypeInt *i) override {
        m_dt = i;
    }

    virtual void visitDataTypeString(ast::IDataTypeString *i) override {
        m_dt = i;
    }

    virtual void visitDataTypeUserDefined(ast::IDataTypeUserDefined *i) override {
        DEBUG_ENTER("visitDataTypeUserDefined");
        // See where this redirects
        ast::IScopeChild *ref_t = resolve(i->getType_id()->getTarget());
        ref_t->accept(m_this);
        DEBUG_LEAVE("visitDataTypeUserDefined");
    }

    virtual void visitSymbolEnumScope(ast::ISymbolEnumScope *i) override {
        DEBUG_ENTER("visitSymbolEnumScope %s", i->getName().c_str());
        m_ss = i;
        DEBUG_LEAVE("visitSymbolEnumScope");
    }

    virtual void visitSymbolTypeScope(ast::ISymbolTypeScope *i) override {
        DEBUG_ENTER("visitSymbolTypeScope");
        m_ss = i;
        m_ts = i;
        DEBUG_LEAVE("visitSymbolTypeScope");
    }

    virtual void visitTemplateGenericTypeParamDecl(ast::ITemplateGenericTypeParamDecl *i) override {
        DEBUG_ENTER("visitTemplateGenericTypeParamDecl");
        i->getDflt()->accept(m_this);
        DEBUG_LEAVE("visitTemplateGenericTypeParamDecl");
    }

    virtual void visitTemplateCategoryTypeParamDecl(ast::ITemplateCategoryTypeParamDecl *i) override {
        DEBUG_ENTER("visitTemplateCategoryTypeParamDecl");
        i->getDflt()->accept(m_this);
        DEBUG_LEAVE("visitTemplateCategoryTypeParamDecl");
    }

private:
    dmgr::IDebug                         *m_dbg;
    ast::ISymbolChildrenScope            *m_root;
    ast::ISymbolTypeScope                *m_ts;
    ast::ISymbolScope                    *m_ss;
    ast::IDataType                       *m_dt;


};

}
}


