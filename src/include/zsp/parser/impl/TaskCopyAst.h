/**
 * TaskCopyAst.h
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
#include "zsp/ast/impl/VisitorBase.h"
#include "zsp/ast/IExprRefPathStatic.h"
#include "zsp/ast/IFactory.h"

namespace zsp {
namespace parser {

class TaskCopyAst : public ast::VisitorBase {
public:
    TaskCopyAst(ast::IFactory *factory) : m_factory(factory) { }

    virtual ~TaskCopyAst() { }

    ast::IConstraintStmt *copy(ast::IConstraintStmt *i) {
        m_constraint = 0;
        i->accept(m_this);

        if (!m_constraint) {
            fprintf(stdout, "Error: copy(constraint) failed\n");
            fflush(stdout);
        }
        return m_constraint;
    }

    template <class T> T *copyT(ast::IConstraintStmt *i) {
        T *ret = dynamic_cast<T *>(copy(i));
        if (!ret) {
            fprintf(stdout, "Error: copyT(constraint) failed\n");
            fflush(stdout);
        }
        return ret;
    }

    ast::IScopeChild *copy(ast::IScopeChild *i) {
        m_sc = 0;
        i->accept(m_this);
        if (!m_sc) {
            fprintf(stdout, "Error: copy(ScopeChild) failed\n");
            fflush(stdout);
        }
        return m_sc;
    };

    template <class T> T *copyT(ast::IScopeChild *i) {
        T *ret = dynamic_cast<T *>(copy(i));
        if (!ret) {
            fprintf(stdout, "Error: copyT(ScopeChild) failed\n");
            fflush(stdout);
        }
        return ret;
    }

    ast::IExpr *copy(ast::IExpr *i) {
        m_expr = 0;
        i->accept(m_this);
        if (!m_expr) {
            fprintf(stdout, "Error: copy(Expr) failed\n");
            fflush(stdout);
        }
        return m_expr;
    };

    template <class T> T *copyT(ast::IExpr *i) {
        T *ret = dynamic_cast<T *>(copy(i));
        if (!ret) {
            fprintf(stdout, "Error: copyT(Expr) failed\n");
            fflush(stdout);
        }
        return ret;
    }

    ast::IDataType *copy(ast::IDataType *i) {
        m_dt = 0;
        i->accept(m_this);
        if (!m_dt) {
            fprintf(stdout, "Error: copy(DataType) failed\n");
            fflush(stdout);
        }
        return m_dt;
    }

    template <class T> T *copyT(ast::IDataType *i) {
        T *ret = dynamic_cast<T *>(copy(i));
        if (!ret) {
            fprintf(stdout, "Error: copyT(Expr) failed\n");
            fflush(stdout);
        }
        return ret;
    }

    ast::ISymbolRefPath *copy(const ast::ISymbolRefPath *i) {
        ast::ISymbolRefPath *ret = m_factory->mkSymbolRefPath();
        ret->getPath().insert(
            ret->getPath().begin(),
            i->getPath().begin(),
            i->getPath().end()
        );
        return ret;
    }

    virtual void visitActivityJoinSpec(ast::IActivityJoinSpec *i) { }
    
    virtual void visitSymbolImportSpec(ast::ISymbolImportSpec *i) { }
    
    virtual void visitScopeChild(ast::IScopeChild *i) { }
    
    virtual void visitSymbolRefPath(ast::ISymbolRefPath *i) { }
    
    virtual void visitRefExpr(ast::IRefExpr *i) { }
    
    virtual void visitActivitySelectBranch(ast::IActivitySelectBranch *i) { }
    
    virtual void visitTemplateParamDeclList(ast::ITemplateParamDeclList *i) { }
    
    virtual void visitActivityMatchChoice(ast::IActivityMatchChoice *i) { }
    
    virtual void visitTemplateParamValueList(ast::ITemplateParamValueList *i) { }
    
    virtual void visitTemplateParamValue(ast::ITemplateParamValue *i) { }
    
    virtual void visitExecTargetTemplateParam(ast::IExecTargetTemplateParam *i) { }
    
    virtual void visitConstraintStmt(ast::IConstraintStmt *i) { }
    
    virtual void visitExprRefPathElem(ast::IExprRefPathElem *i) { }
    
    virtual void visitExprStaticRefPath(ast::IExprStaticRefPath *i) {
        ast::IExprStaticRefPath *ic = m_factory->mkExprStaticRefPath(
            i->getIs_global(),
            copyT<ast::IExprMemberPathElem>(i->getLeaf())
        );
        m_expr = ic;
    }
    
    virtual void visitExprString(ast::IExprString *i) { 
        m_expr = m_factory->mkExprString(i->getValue(), i->getIs_raw());
    }
    
    virtual void visitExprSubscript(ast::IExprSubscript *i) { }
    
    virtual void visitExprUnary(ast::IExprUnary *i) { }
    
    virtual void visitScope(ast::IScope *i) { }
    
    virtual void visitMethodParameterList(ast::IMethodParameterList *i) { }
    
    virtual void visitScopeChildRef(ast::IScopeChildRef *i) { }
    
    virtual void visitTypeIdentifier(ast::ITypeIdentifier *i) { 
        ast::ITypeIdentifier *ic = m_factory->mkTypeIdentifier();
        for (std::vector<ast::ITypeIdentifierElemUP>::const_iterator
            it=i->getElems().begin();
            it!=i->getElems().end(); it++) {
            ic->getElems().push_back(ast::ITypeIdentifierElemUP(
                copyT<ast::ITypeIdentifierElem>(it->get())
            ));
        }

        m_expr = ic;
    }
    
    virtual void visitTypeIdentifierElem(ast::ITypeIdentifierElem *i) { 
        ast::ITemplateParamValueList *plist = 0;

        ast::ITypeIdentifierElem *ic = m_factory->mkTypeIdentifierElem(
            copyT<ast::IExprId>(i->getId()),
            plist
        );

        m_expr = ic;
    }
    
    virtual void visitNamedScopeChild(ast::INamedScopeChild *i) { }
    
    virtual void visitFunctionDefinition(ast::IFunctionDefinition *i) { }
    
    virtual void visitPackageImportStmt(ast::IPackageImportStmt *i) { }
    
    virtual void visitFunctionParamDecl(ast::IFunctionParamDecl *i) { }
    
    virtual void visitFunctionImport(ast::IFunctionImport *i) { }
    
    virtual void visitDataType(ast::IDataType *i) { }
    
    virtual void visitExtendEnum(ast::IExtendEnum *i) { }
    
    virtual void visitSymbolScope(ast::ISymbolScope *i) { }
    
    virtual void visitRefExprTypeScopeGlobal(ast::IRefExprTypeScopeGlobal *i) { }
    
    virtual void visitRefExprTypeScopeContext(ast::IRefExprTypeScopeContext *i) { }
    
    virtual void visitRefExprScopeIndex(ast::IRefExprScopeIndex *i) { }
    
    virtual void visitTemplateParamDecl(ast::ITemplateParamDecl *i) { }
    
    virtual void visitTemplateParamTypeValue(ast::ITemplateParamTypeValue *i) { }
    
    virtual void visitTemplateParamExprValue(ast::ITemplateParamExprValue *i) { }
    
    virtual void visitActivityStmt(ast::IActivityStmt *i) { }
    
    virtual void visitActivitySchedulingConstraint(ast::IActivitySchedulingConstraint *i) { }
    
    virtual void visitActivityJoinSpecBranch(ast::IActivityJoinSpecBranch *i) { }
    
    virtual void visitActivityJoinSpecSelect(ast::IActivityJoinSpecSelect *i) { }
    
    virtual void visitActivityJoinSpecNone(ast::IActivityJoinSpecNone *i) { }
    
    virtual void visitActivityJoinSpecFirst(ast::IActivityJoinSpecFirst *i) { }
    
    virtual void visitExecStmt(ast::IExecStmt *i) { }
    
    virtual void visitExecTargetTemplateBlock(ast::IExecTargetTemplateBlock *i) { }
    
    virtual void visitExprBin(ast::IExprBin *i) { 
        m_expr = m_factory->mkExprBin(
            copy(i->getLhs()),
            i->getOp(),
            copy(i->getRhs())
        );
    }
    
    virtual void visitExprBitSlice(ast::IExprBitSlice *i) { 
        m_expr = m_factory->mkExprBitSlice(
            copy(i->getLhs()),
            copy(i->getRhs())
        );
    }
    
    virtual void visitExprBool(ast::IExprBool *i) { 
        m_expr = m_factory->mkExprBool(i->getValue());
    }
    
    virtual void visitExprCast(ast::IExprCast *i) { 
        m_expr = m_factory->mkExprCast(
            copy(i->getCasting_type()),
            copy(i->getExpr())
        );
    }
    
    virtual void visitExprCompileHas(ast::IExprCompileHas *i) { 
        m_expr = m_factory->mkExprCompileHas(
            copyT<ast::IExprRefPathStatic>(i->getRef())
        );
    }
    
    virtual void visitExprCond(ast::IExprCond *i) { 
        m_expr = m_factory->mkExprCond(
            copy(i->getCond_e()),
            copy(i->getTrue_e()),
            copy(i->getFalse_e())
        );
    }
    
    virtual void visitExprDomainOpenRangeList(ast::IExprDomainOpenRangeList *i) { }
    
    virtual void visitExprDomainOpenRangeValue(ast::IExprDomainOpenRangeValue *i) { }
    
    virtual void visitExprHierarchicalId(ast::IExprHierarchicalId *i) { 
        ast::IExprHierarchicalId *ic = m_factory->mkExprHierarchicalId();
        for (std::vector<ast::IExprMemberPathElemUP>::const_iterator
            it=i->getElems().begin();
            it!=i->getElems().end(); it++) {
            ic->getElems().push_back(ast::IExprMemberPathElemUP(
                copyT<ast::IExprMemberPathElem>(it->get())));
        }
        m_expr = ic;
    }
    
    virtual void visitExprId(ast::IExprId *i) { 
        m_expr = m_factory->mkExprId(
            i->getId(),
            i->getIs_escaped()
        );
    }
    
    virtual void visitExprIn(ast::IExprIn *i) { }
    
    virtual void visitExprMemberPathElem(ast::IExprMemberPathElem *i) { 
        ast::IMethodParameterList *plist = 0;

        if (i->getParams()) {
            plist = m_factory->mkMethodParameterList();
            for (std::vector<ast::IExprUP>::const_iterator
                it=i->getParams()->getParameters().begin();
                it!=i->getParams()->getParameters().end(); it++) {
                plist->getParameters().push_back(ast::IExprUP(copy(it->get())));
            }
        }
        m_expr = m_factory->mkExprMemberPathElem(
            copyT<ast::IExprId>(i->getId()),
            plist,
            (i->getSubscript())?copy(i->getSubscript()):0
        );
    }
    
    virtual void visitExprNull(ast::IExprNull *i) { 
        m_expr = m_factory->mkExprNull();
    }
    
    virtual void visitExprAggregateLiteral(ast::IExprAggregateLiteral *i) { }
    
    virtual void visitExprOpenRangeList(ast::IExprOpenRangeList *i) { }
    
    virtual void visitExprOpenRangeValue(ast::IExprOpenRangeValue *i) { }
    
    virtual void visitExprRefPath(ast::IExprRefPath *i) { }
    
    virtual void visitExprRefPathId(ast::IExprRefPathId *i) { 
        ast::IExprRefPathId *ic = m_factory->mkExprRefPathId(
            copyT<ast::IExprId>(i->getId()));
        if (i->getSlice()) {
            ic->setSlice(copyT<ast::IExprBitSlice>(i->getSlice()));
        }
        m_expr = ic;
    }
    
    virtual void visitConstraintScope(ast::IConstraintScope *i) { }
    
    virtual void visitExprRefPathContext(ast::IExprRefPathContext *i) { }
    
    virtual void visitConstraintStmtExpr(ast::IConstraintStmtExpr *i) { 
        m_constraint = m_factory->mkConstraintStmtExpr(
            copy(i->getExpr())
        );
    }
    
    virtual void visitExprRefPathStatic(ast::IExprRefPathStatic *i) { 

    }

    virtual void visitExprSignedNumber(ast::IExprSignedNumber *i) { 
        m_expr = m_factory->mkExprSignedNumber(
            i->getImage(),
            i->getWidth(),
            i->getValue()
        );
    }

    virtual void visitExprUnsignedNumber(ast::IExprUnsignedNumber *i) { 
        m_expr = m_factory->mkExprUnsignedNumber(
            i->getImage(),
            i->getWidth(),
            i->getValue()
        );
    }
    
    virtual void visitConstraintStmtField(ast::IConstraintStmtField *i) { }
    
    virtual void visitExprRefPathStaticRooted(ast::IExprRefPathStaticRooted *i) { 
        ast::IExprRefPathStaticRooted *ic = m_factory->mkExprRefPathStaticRooted(
            copyT<ast::IExprStaticRefPath>(i->getRoot()),
            (i->getLeaf())?copyT<ast::IExprHierarchicalId>(i->getLeaf()):0
        );
        m_expr = ic;
    }
    
    virtual void visitConstraintStmtIf(ast::IConstraintStmtIf *i) { 
        m_constraint = m_factory->mkConstraintStmtIf(
            copy(i->getCond()),
            copyT<ast::IConstraintScope>(i->getTrue_c()),
            (i->getFalse_c())?copyT<ast::IConstraintScope>(i->getFalse_c()):0
        );
    }
    
    virtual void visitConstraintStmtUnique(ast::IConstraintStmtUnique *i) { }
    
    virtual void visitConstraintStmtDefault(ast::IConstraintStmtDefault *i) { }
    
    virtual void visitConstraintStmtDefaultDisable(ast::IConstraintStmtDefaultDisable *i) { }
    
    virtual void visitPackageScope(ast::IPackageScope *i) { }
    
    virtual void visitFunctionPrototype(ast::IFunctionPrototype *i) { }
    
    virtual void visitFunctionImportType(ast::IFunctionImportType *i) { }
    
    virtual void visitFunctionImportProto(ast::IFunctionImportProto *i) { }
    
    virtual void visitDataTypeArray(ast::IDataTypeArray *i) { }
    
    virtual void visitDataTypeBool(ast::IDataTypeBool *i) { 
        m_dt = m_factory->mkDataTypeBool();
    }
    
    virtual void visitDataTypeChandle(ast::IDataTypeChandle *i) { 
        m_dt = m_factory->mkDataTypeChandle();
    }
    
    virtual void visitDataTypeEnum(ast::IDataTypeEnum *i) { 

    }
    
    virtual void visitEnumItem(ast::IEnumItem *i) { 

    }
    
    virtual void visitEnumDecl(ast::IEnumDecl *i) { }
    
    virtual void visitDataTypeInt(ast::IDataTypeInt *i) { 
        m_dt = m_factory->mkDataTypeInt(
            i->getIs_signed(),
            (i->getWidth())?copy(i->getWidth()):0,
            (i->getIn_range())?copyT<ast::IExprDomainOpenRangeList>(i->getIn_range()):0
        );
    }
    
    virtual void visitDataTypeRef(ast::IDataTypeRef *i) { }
    
    virtual void visitDataTypeString(ast::IDataTypeString *i) { 
        ast::IDataTypeString *ci = m_factory->mkDataTypeString(i->getHas_range());
        if (i->getHas_range()) {
            ci->getIn_range().insert(
                ci->getIn_range().begin(),
                i->getIn_range().begin(),
                i->getIn_range().end()
            );
        }

        m_dt = ci;
    }
    
    virtual void visitDataTypeUserDefined(ast::IDataTypeUserDefined *i) { 
        m_dt = m_factory->mkDataTypeUserDefined(
            i->getIs_global(),
            copyT<ast::ITypeIdentifier>(i->getType_id())
        );
    }
    
    virtual void visitExtendType(ast::IExtendType *i) { }
    
    virtual void visitField(ast::IField *i) { 
        m_sc = m_factory->mkField(
            copyT<ast::IExprId>(i->getName()),
            copy(i->getType()),
            i->getAttr(),
            (i->getArray_dim())?copy(i->getArray_dim()):0,
            (i->getInit())?copy(i->getInit()):0
        );
    }
    
    virtual void visitFieldCompRef(ast::IFieldCompRef *i) { }
    
    virtual void visitFieldRef(ast::IFieldRef *i) { }
    
    virtual void visitFieldClaim(ast::IFieldClaim *i) { }
    
    virtual void visitSymbolEnumScope(ast::ISymbolEnumScope *i) { }
    
    virtual void visitSymbolExecScope(ast::ISymbolExecScope *i) { }
    
    virtual void visitSymbolExtendScope(ast::ISymbolExtendScope *i) { }
    
    virtual void visitSymbolTypeScope(ast::ISymbolTypeScope *i) { }
    
    virtual void visitSymbolFunctionScope(ast::ISymbolFunctionScope *i) { }
    
    virtual void visitTemplateGenericTypeParamDecl(ast::ITemplateGenericTypeParamDecl *i) { }
    
    virtual void visitTemplateCategoryTypeParamDecl(ast::ITemplateCategoryTypeParamDecl *i) { }
    
    virtual void visitTemplateValueParamDecl(ast::ITemplateValueParamDecl *i) { }
    
    virtual void visitActivityDecl(ast::IActivityDecl *i) { }
    
    virtual void visitActivityBindStmt(ast::IActivityBindStmt *i) { }
    
    virtual void visitActivityConstraint(ast::IActivityConstraint *i) { }
    
    virtual void visitActivityLabeledStmt(ast::IActivityLabeledStmt *i) { }
    
    virtual void visitActivityLabeledScope(ast::IActivityLabeledScope *i) { }
    
    virtual void visitExecScope(ast::IExecScope *i) { }
    
    virtual void visitProceduralStmtAssignment(ast::IProceduralStmtAssignment *i) { }
    
    virtual void visitProceduralStmtExpr(ast::IProceduralStmtExpr *i) { }
    
    virtual void visitProceduralStmtFunctionCall(ast::IProceduralStmtFunctionCall *i) { }
    
    virtual void visitProceduralStmtReturn(ast::IProceduralStmtReturn *i) { }
    
    virtual void visitProceduralStmtRepeat(ast::IProceduralStmtRepeat *i) { }
    
    virtual void visitProceduralStmtRepeatWhile(ast::IProceduralStmtRepeatWhile *i) { }
    
    virtual void visitProceduralStmtWhile(ast::IProceduralStmtWhile *i) { }
    
    virtual void visitProceduralStmtForeach(ast::IProceduralStmtForeach *i) { }
    
    virtual void visitProceduralStmtIfElse(ast::IProceduralStmtIfElse *i) { }
    
    virtual void visitProceduralStmtMatch(ast::IProceduralStmtMatch *i) { }
    
    virtual void visitProceduralStmtMatchChoice(ast::IProceduralStmtMatchChoice *i) { }
    
    virtual void visitProceduralStmtBreak(ast::IProceduralStmtBreak *i) { }
    
    virtual void visitProceduralStmtContinue(ast::IProceduralStmtContinue *i) { }
    
    virtual void visitProceduralStmtDataDeclaration(ast::IProceduralStmtDataDeclaration *i) { }
    
    virtual void visitConstraintBlock(ast::IConstraintBlock *i) { 
        ast::IConstraintBlock *ic = m_factory->mkConstraintBlock(
            i->getName(),
            i->getIs_dynamic());

        for (std::vector<ast::IConstraintStmtUP>::const_iterator
            it=i->getConstraints().begin();
            it!=i->getConstraints().end(); it++) {
            ic->getConstraints().push_back(ast::IConstraintStmtUP(copy(it->get())));
        }

        m_sc = ic;
    }
    
    virtual void visitConstraintStmtForeach(ast::IConstraintStmtForeach *i) { }
    
    virtual void visitExprRefPathStaticFunc(ast::IExprRefPathStaticFunc *i) { }
    
    virtual void visitConstraintStmtForall(ast::IConstraintStmtForall *i) { }
    
    virtual void visitExprRefPathSuper(ast::IExprRefPathSuper *i) { }
    
    virtual void visitConstraintStmtImplication(ast::IConstraintStmtImplication *i) { }
    
    virtual void visitTypeScope(ast::ITypeScope *i) { }
    
    virtual void visitActivityActionHandleTraversal(ast::IActivityActionHandleTraversal *i) { }
    
    virtual void visitActivityActionTypeTraversal(ast::IActivityActionTypeTraversal *i) { }
    
    virtual void visitActivitySequence(ast::IActivitySequence *i) { }
    
    virtual void visitActivityParallel(ast::IActivityParallel *i) { }
    
    virtual void visitActivitySchedule(ast::IActivitySchedule *i) { }
    
    virtual void visitActivityRepeatCount(ast::IActivityRepeatCount *i) { }
    
    virtual void visitActivityRepeatWhile(ast::IActivityRepeatWhile *i) { }
    
    virtual void visitActivityForeach(ast::IActivityForeach *i) { }
    
    virtual void visitActivitySelect(ast::IActivitySelect *i) { }
    
    virtual void visitActivityIfElse(ast::IActivityIfElse *i) { }
    
    virtual void visitActivityMatch(ast::IActivityMatch *i) { }
    
    virtual void visitActivityReplicate(ast::IActivityReplicate *i) { }
    
    virtual void visitActivitySuper(ast::IActivitySuper *i) { }
    
    virtual void visitExecBlock(ast::IExecBlock *i) { }
    
    virtual void visitProceduralStmtSequenceBlock(ast::IProceduralStmtSequenceBlock *i) { }
    
    virtual void visitStruct(ast::IStruct *i) {
        ast::IStruct *ic = m_factory->mkStruct(
            copyT<ast::IExprId>(i->getName()),
            (i->getSuper_t())?copyT<ast::ITypeIdentifier>(i->getSuper_t()):0,
            i->getKind()
        );

        if (i->getParams()) {

        }

        for (std::vector<ast::IScopeChildUP>::const_iterator
            it=i->getChildren().begin();
            it!=i->getChildren().end(); it++) {
            ic->getChildren().push_back(ast::IScopeChildUP(copy(it->get())));
        }

        m_sc = ic;
    }
    
    virtual void visitAction(ast::IAction *i) { 
        ast::IAction *ic = m_factory->mkAction(
            copyT<ast::IExprId>(i->getName()),
            (i->getSuper_t())?copyT<ast::ITypeIdentifier>(i->getSuper_t()):0,
            i->getIs_abstract()
        );

        for (std::vector<ast::IScopeChildUP>::const_iterator
            it=i->getChildren().begin();
            it!=i->getChildren().end(); it++) {
            ic->getChildren().push_back(ast::IScopeChildUP(copy(it->get())));
        }

        m_sc = ic;
    }
    
    virtual void visitComponent(ast::IComponent *i) { 
        ast::IComponent *ic = m_factory->mkComponent(
            copyT<ast::IExprId>(i->getName()),
            (i->getSuper_t())?copyT<ast::ITypeIdentifier>(i->getSuper_t()):0
        );

        for (std::vector<ast::IScopeChildUP>::const_iterator
            it=i->getChildren().begin();
            it!=i->getChildren().end(); it++) {
            ic->getChildren().push_back(ast::IScopeChildUP(copy(it->get())));
        }

        m_sc = ic;
    }

private:
    ast::IFactory                   *m_factory;

    ast::IConstraintStmt            *m_constraint;
    ast::IDataType                  *m_dt;
    ast::IExpr                      *m_expr;
    ast::IScopeChild                *m_sc;

};

}
}

