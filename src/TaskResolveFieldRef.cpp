/*
 * TaskResolveFieldRef.cpp
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
#include "TaskResolveFieldRef.h"


namespace zsp {
namespace parser {


TaskResolveFieldRef::TaskResolveFieldRef(ResolveContext *ctxt) : TaskResolveBase(ctxt) {
    DEBUG_INIT("TaskResolveFieldRef", ctxt->getDebugMgr());
    m_id = 0;
    m_path = 0;
    m_ret = 0;
}

TaskResolveFieldRef::~TaskResolveFieldRef() {

}

ast::IScopeChild *TaskResolveFieldRef::resolve(
        ast::IExprId            *id,
        ast::IScopeChild        *ctxt,
        ast::ISymbolRefPath     *path) {
    m_id = id;
    m_path = path;
    m_ret = 0;
    ctxt->accept(m_this);
    return m_ret;
}

void TaskResolveFieldRef::visitNamedScope(ast::INamedScope *i) { 

}

void TaskResolveFieldRef::visitNamedScopeChild(ast::INamedScopeChild *i) { 

}

void TaskResolveFieldRef::visitSymbolScope(ast::ISymbolScope *i) { 

}

//void TaskResolveFieldRef::visitSymbolExecScope(ast::ISymbolExecScope *i) { 
//
//}

void TaskResolveFieldRef::visitSymbolTypeScope(ast::ISymbolTypeScope *i) { 

}

void TaskResolveFieldRef::visitScopeChild(ast::IScopeChild *i) { 

}

dmgr::IDebug *TaskResolveFieldRef::m_dbg = 0;

}
}
