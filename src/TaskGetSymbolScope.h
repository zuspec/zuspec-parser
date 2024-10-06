/**
 * TaskGetSymbolScope.h
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
#include "zsp/ast/impl/VisitorBase.h"

namespace zsp {
namespace parser {



class TaskGetSymbolScope :
    public virtual ast::VisitorBase {
public:

    virtual ~TaskGetSymbolScope() { }

    ast::ISymbolScope *get(ast::IScopeChild *i) {
        m_ret = 0;
        i->accept(m_this);
        return m_ret;
    }

    virtual void visitSymbolScope(ast::ISymbolScope *s) override {
        m_ret = s;
    }

protected:
    ast::ISymbolScope       *m_ret;
};

} /* namespace parser */
} /* namespace zsp */


