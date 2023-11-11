/*
 * BuiltinsFactory.cpp
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
#include "BuiltinsFactory.h"


namespace zsp {
namespace parser {


BuiltinsFactory::BuiltinsFactory(ast::IFactory *ast_f) : m_ast_f(ast_f) {

}

BuiltinsFactory::~BuiltinsFactory() {

}

ast::IGlobalScope *BuiltinsFactory::build() {
    m_builtins = ast::IGlobalScopeUP(m_ast_f->mkGlobalScope(-1));

    ast::ITypeScope *pyobj = m_ast_f->mkTypeScope(
        m_ast_f->mkExprId("pyobj", false),
        0);
    pyobj->setOpaque(true);
    pyobj->setParent(m_builtins.get());
    m_builtins->getChildren().push_back(ast::IScopeChildUP(pyobj));

    return m_builtins.release();
}

}
}
