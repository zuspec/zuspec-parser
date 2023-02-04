/*
 * TaskGetSpecializedTemplateType.cpp
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
#include "TaskGetSpecializedTemplateType.h"


namespace zsp {
namespace parser {


TaskGetSpecializedTemplateType::TaskGetSpecializedTemplateType(
    IFactory            *factory,
    ast::ISymbolScope   *root) : m_factory(factory), m_root(root) {
    DEBUG_INIT("TaskGetSpecializedTemplateType", factory->getDebugMgr());

}

TaskGetSpecializedTemplateType::~TaskGetSpecializedTemplateType() {

}

ast::ISymbolRefPath *TaskGetSpecializedTemplateType::find(
    const ast::ISymbolRefPath           *type,
    const ast::ITemplateParamDeclList   *params) {

}

ast::ISymbolRefPath *TaskGetSpecializedTemplateType::mk(
    const ast::ISymbolRefPath           *type,
    ast::ITemplateParamDeclList         *params) {

}

dmgr::IDebug *TaskGetSpecializedTemplateType::m_dbg = 0;

}
}
