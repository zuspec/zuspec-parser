/*
 * TaskCompareParamLists.cpp
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
#include "TaskCompareParamLists.h"


namespace zsp {
namespace parser {


TaskCompareParamLists::TaskCompareParamLists(dmgr::IDebugMgr *dmgr) {
    DEBUG_INIT("TaskCompareParamLists", dmgr);

}

TaskCompareParamLists::~TaskCompareParamLists() {

}

bool TaskCompareParamLists::equal(
        const ast::ITemplateParamDeclList     *plist1,
        const ast::ITemplateParamDeclList     *plist2) {
    DEBUG_ENTER("equal");

    DEBUG_LEAVE("equal");
    return false;
}

dmgr::IDebug *TaskCompareParamLists::m_dbg = 0;

}
}