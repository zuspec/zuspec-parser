/**
 * TaskFindElementByLocation.h
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
#include "dmgr/IDebugMgr.h"
#include "zsp/ast/impl/VisitorBase.h"
#include "zsp/parser/ITaskFindElementByLocation.h"

namespace zsp {
namespace parser {


class TaskFindElementByLocation : 
    public virtual ITaskFindElementByLocation,
    public virtual ast::VisitorBase {
public:
    TaskFindElementByLocation(dmgr::IDebugMgr *dmgr);

    virtual ~TaskFindElementByLocation();

    bool find(
        std::vector<ast::IScopeChild *>     &path,
        ast::ISymbolScope                   *root,
        int32_t                             lineno,
        int32_t                             linepos);

    virtual void visitExprId(ast::IExprId *i) override;

    virtual void visitSymbolScope(ast::ISymbolScope *i) override;

    virtual void visitTypeScope(ast::ITypeScope *i) override;

private:
    static dmgr::IDebug                     *m_dbg;
    std::vector<ast::IScopeChild *>         *m_path;
    int32_t                                 m_lineno;
    int32_t                                 m_linepos;
    bool                                    m_found;


};

}
}


