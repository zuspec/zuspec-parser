/*
 * TaskBuildParamValList.cpp
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
#include "TaskBuildParamValList.h"
#include "zsp/parser/impl/TaskCopyAst.h"


namespace zsp {
namespace parser {


TaskBuildParamValList::TaskBuildParamValList(
    ast::ISymbolScope           *root,
    IFactory                    *factory,
    IMarkerListener             *marker_l) : 
        m_root(root), m_factory(factory), m_marker_l(marker_l) {

}

TaskBuildParamValList::~TaskBuildParamValList() {

}

ast::ISymbolScope *TaskBuildParamValList::build(
        ast::ISymbolScope               *plist,
        ast::ITemplateParamValueList    *pvals) {
    TaskCopyAst copier(m_factory->getAstFactory());
    m_ret = 0;

    if (pvals->getValues().size() > plist->getChildren().size()) {
        fprintf(stdout, "TODO: Flag error \"Type accepts %d parameters ; %d supplied\"\n",
            plist->getChildren().size(),
            pvals->getValues().size());
        return 0;
    }

    m_ret = m_factory->getAstFactory()->mkSymbolScope(
        plist->getId(),
        plist->getName());
    
    // First, pick up explicitly-supplied parameter values
//    m_ptype_mk_pval = false;
    for (uint32_t i=0; i<pvals->getValues().size(); i++) {
        pvals->getValues().at(i)->accept(m_this);
        plist->getChildren().at(i)->accept(m_this);

        if (m_pval_expr) {
            if (!m_ptype_value) {
                fprintf(stdout, "TODO: expression supplied for value %d, but ptype is not value\n", i);
                return 0;
            }
            ast::ITemplateValueParamDecl *p = m_factory->getAstFactory()->mkTemplateValueParamDecl(
                copier.copyT<ast::IExprId>(m_ptype_value->getName()),
                copier.copyT<ast::IDataType>(m_ptype_value->getType()),
                copier.copyT<ast::IExpr>(m_pval_expr->getValue()));

            m_ret->getSymtab().insert({p->getName()->getId(), m_ret->getChildren().size()});            
            m_ret->getChildren().push_back(p);
        } else {
            // Type value. We always specialize as a generic type parameter
            ast::IExprId *name = 0;
            if (m_ptype_category_type) {
                name = m_ptype_category_type->getName();

            } else if (m_ptype_generic_type) {
                name = m_ptype_generic_type->getName();
            } else {
                fprintf(stdout, "TODO: no ptype_decl captured\n");
            }

            ast::ITemplateGenericTypeParamDecl *p = m_factory->getAstFactory()->mkTemplateGenericTypeParamDecl(
                copier.copyT<ast::IExprId>(name),
                copier.copyT<ast::ITypeIdentifier>(m_pval_type->getValue())
            );
        }
    }

    return m_ret;
}

void TaskBuildParamValList::visitTemplateParamTypeValue(ast::ITemplateParamTypeValue *i) {
    m_pval_type = i;
}
    
void TaskBuildParamValList::visitTemplateParamExprValue(ast::ITemplateParamExprValue *i) { 
    m_pval_expr = i;
}

void TaskBuildParamValList::visitTemplateGenericTypeParamDecl(ast::ITemplateGenericTypeParamDecl *i) { 
    m_ptype_generic_type = i;
}
    
void TaskBuildParamValList::visitTemplateCategoryTypeParamDecl(ast::ITemplateCategoryTypeParamDecl *i) { 
    m_ptype_category_type = i;
}
    
void TaskBuildParamValList::visitTemplateValueParamDecl(ast::ITemplateValueParamDecl *i) { 
    m_ptype_value = i;
}

}
}
