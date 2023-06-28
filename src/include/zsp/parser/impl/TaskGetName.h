/**
 * TaskGetName.h
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
#include <string>
#include "zsp/ast/impl/VisitorBase.h"

namespace zsp {
namespace parser {

class TaskGetName : public virtual ast::VisitorBase {
public:
    TaskGetName() { }

    virtual ~TaskGetName() { }

    const std::string &get(ast::IScopeChild *c, bool bottom_up=false) {
        m_ret = "";
        if (bottom_up) {
            ast::IScopeChild *ci = c;

            c->accept(m_this);
            std::string full_path;

            do {
                m_ret = "";
                c->accept(m_this);
                
                if (full_path.size() && m_ret.size()) {
                    full_path = "::" + full_path;
                }
                full_path = m_ret + full_path;
            } while ((ci=ci->getParent()));

            m_ret = full_path;
        } else {
            c->accept(m_this);
        }
        return m_ret;
    }

    virtual void visitNamedScopeChild(ast::INamedScopeChild *i) override {
        m_ret = i->getName()->getId();
    }

    virtual void visitNamedScope(ast::INamedScope *i) override {
        m_ret = i->getName()->getId();
    }

    virtual void visitSymbolScope(ast::ISymbolScope *i) override {
        m_ret = i->getName();
    }

    virtual void visitSymbolTypeScope(ast::ISymbolTypeScope *i) override {
        m_ret = i->getName();
    }

private:
    std::string                 m_ret;
};

}
}


