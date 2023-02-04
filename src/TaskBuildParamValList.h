/**
 * TaskBuildParamValList.h
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
#include "zsp/ast/impl/VisitorBase.h"
#include "zsp/ast/ISymbolScope.h"
#include "zsp/parser/IFactory.h"

namespace zsp {
namespace parser {



class TaskBuildParamValList : public ast::VisitorBase {
public:
    TaskBuildParamValList(
        ast::ISymbolScope       *root,
        IFactory                *factory,
        IMarkerListener         *marker_l);

    virtual ~TaskBuildParamValList();

    ast::ISymbolScope *build(
        ast::ISymbolScope               *plist,
        ast::ITemplateParamValueList    *pvals);

    virtual void visitTemplateParamTypeValue(ast::ITemplateParamTypeValue *i) override;
    
    virtual void visitTemplateParamExprValue(ast::ITemplateParamExprValue *i) override;

    virtual void visitTemplateGenericTypeParamDecl(ast::ITemplateGenericTypeParamDecl *i) override;
    
    virtual void visitTemplateCategoryTypeParamDecl(ast::ITemplateCategoryTypeParamDecl *i) override;
    
    virtual void visitTemplateValueParamDecl(ast::ITemplateValueParamDecl *i) override;

private:
    static dmgr::IDebug                 *m_dbg; 
    ast::ISymbolScope                   *m_root;
    IFactory                            *m_factory;
    IMarkerListener                     *m_marker_l;
    ast::ISymbolScope                   *m_ret;
    ast::ITemplateParamTypeValue        *m_pval_type;
    ast::ITemplateParamExprValue        *m_pval_expr;
    ast::ITemplateGenericTypeParamDecl  *m_ptype_generic_type;
    ast::ITemplateCategoryTypeParamDecl *m_ptype_category_type;
    ast::ITemplateValueParamDecl        *m_ptype_value;


};

}
}


