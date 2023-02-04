/**
 * TaskGetSpecializedTemplateType.h
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
#include "dmgr/IDebugMgr.h"
#include "zsp/parser/IFactory.h"
#include "zsp/ast/ISymbolScope.h"

namespace zsp {
namespace parser {



class TaskGetSpecializedTemplateType {
public:
    TaskGetSpecializedTemplateType(
        IFactory           *factory,
        ast::ISymbolScope  *root);

    virtual ~TaskGetSpecializedTemplateType();

    ast::ISymbolRefPath *find(
        const ast::ISymbolRefPath           *type,
        const ast::ITemplateParamDeclList   *params);

    ast::ISymbolRefPath *mk(
        const ast::ISymbolRefPath           *type,
        ast::ITemplateParamDeclList         *params);

private:
    static dmgr::IDebug                 *m_dbg;
    IFactory                            *m_factory;
    ast::ISymbolScope                   *m_root;
};

}
}


