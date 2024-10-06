/**
 * ScopeUtil.h
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
#pragma once
#include "zsp/ast/IScopeChild.h"
#include "zsp/ast/impl/VisitorBase.h"

namespace zsp {
namespace parser {



class ScopeUtil :
    public virtual ast::VisitorBase {
public:
    ScopeUtil(ast::IScopeChild *c) {
        init(c);
    }

    virtual ~ScopeUtil() { }

    bool init(ast::IScopeChild *c) {
        m_constraint_s = 0;
        m_sym_cs = 0;
        m_scope = 0;
        c->accept(m_this);
        return valid();
    }

    bool valid() const {
        return (m_sym_cs || m_scope || m_constraint_s);
    }

    ast::IScopeChild *get() const {
        if (m_sym_cs) {
            return m_sym_cs;
        } else if (m_scope) {
            return m_scope;
        } else {
            return 0;
        }
    }

    template <class T> T *getT() const {
        return dynamic_cast<T *>(get());
    }

/*
    const std::vector<ast::IScopeChildUP> &getChildren() {
        if (m_sym_cs) {
            return m_sym_cs->getChildren();
        } else if (m_scope) {
            return m_scope->getChildren();
        } else {
//            return m_null;
        }
    }
 */

    int32_t getNumChildren() const {
        if (m_sym_cs) {
            return m_sym_cs->getChildren().size();
        } else if (m_scope) {
            return m_scope->getChildren().size();
        } else if (m_constraint_s) {
            return m_constraint_s->getConstraints().size();
        } else {
            return 0;
        }
    }

    ast::IScopeChild *getChild(int32_t idx) {
        ast::IScopeChild *ret = 0;
        if (m_constraint_s) {
            if (idx < m_constraint_s->getConstraints().size()) {
                ret = m_constraint_s->getConstraints().at(idx).get();
            }
        } else if (m_scope) {
            if (idx < m_scope->getChildren().size()) {
                ret = m_scope->getChildren().at(idx).get();
            }
        } else if (m_sym_cs) {
            if (idx < m_sym_cs->getChildren().size()) {
                ret = m_sym_cs->getChildren().at(idx).get();
            }
        }

        return ret;
    }

    std::string getName() {
        if (m_sym_cs) {
            return m_sym_cs->getName();
        } else {
            return "";
        }
    }

    virtual void visitConstraintBlock(ast::IConstraintBlock *i) override {
        m_constraint_s = i;
    }

    virtual void visitConstraintScope(ast::IConstraintScope *i) override {
        m_constraint_s = i;
    }

    virtual void visitExecScope(ast::IExecScope *i) override {
        m_sym_cs = i;
    }

    virtual void visitFunctionPrototype(ast::IFunctionPrototype *i) override {
        //
    }

    virtual void visitRootSymbolScope(ast::IRootSymbolScope *i) override {
        m_sym_cs = i;
    }

    virtual void visitSymbolChildrenScope(ast::ISymbolChildrenScope *i) override {
        m_sym_cs = i;
    }

    virtual void visitSymbolFunctionScope(ast::ISymbolFunctionScope *i) override {
        m_sym_cs = i;
    }

    virtual void visitSymbolTypeScope(ast::ISymbolTypeScope *i) override {
        m_sym_cs = i;
    }

    virtual void visitScope(ast::IScope *i) override {
        m_scope = i;
    }

    virtual void visitTypeScope(ast::ITypeScope *i) override {
        m_scope = i;
    }

private:
//    std::vector<ast::IScopeChildUP>     m_null;
    ast::IConstraintScope               *m_constraint_s;
    ast::ISymbolChildrenScope           *m_sym_cs;
    ast::IScope                         *m_scope;

};

} /* namespace parser */
} /* namespace zsp */


