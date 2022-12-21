#pragma once
#include "zsp/ast/impl/VisitorBase.h"
#include <Python.h>
namespace zsp {
namespace ast {

class PyBaseVisitor : public VisitorBase {
public:
    PyBaseVisitor(PyObject *proxy);
    virtual ~PyBaseVisitor();
private:
    PyObject *m_proxy;
    public:
    virtual void visitSymbolImportSpec(ISymbolImportSpec *i) override;
    void py_visitSymbolImportSpec(ISymbolImportSpec *i);
    virtual void visitScopeChild(IScopeChild *i) override;
    void py_visitScopeChild(IScopeChild *i);
    virtual void visitActivityJoinSpec(IActivityJoinSpec *i) override;
    void py_visitActivityJoinSpec(IActivityJoinSpec *i);
    virtual void visitSymbolRefPath(ISymbolRefPath *i) override;
    void py_visitSymbolRefPath(ISymbolRefPath *i);
    virtual void visitRefExpr(IRefExpr *i) override;
    void py_visitRefExpr(IRefExpr *i);
    virtual void visitTemplateParamDeclList(ITemplateParamDeclList *i) override;
    void py_visitTemplateParamDeclList(ITemplateParamDeclList *i);
    virtual void visitTemplateParamDecl(ITemplateParamDecl *i) override;
    void py_visitTemplateParamDecl(ITemplateParamDecl *i);
    virtual void visitActivitySelectBranch(IActivitySelectBranch *i) override;
    void py_visitActivitySelectBranch(IActivitySelectBranch *i);
    virtual void visitTemplateParamValueList(ITemplateParamValueList *i) override;
    void py_visitTemplateParamValueList(ITemplateParamValueList *i);
    virtual void visitTemplateParamValue(ITemplateParamValue *i) override;
    void py_visitTemplateParamValue(ITemplateParamValue *i);
    virtual void visitActivityMatchChoice(IActivityMatchChoice *i) override;
    void py_visitActivityMatchChoice(IActivityMatchChoice *i);
    virtual void visitTemplateParamTypeValue(ITemplateParamTypeValue *i) override;
    void py_visitTemplateParamTypeValue(ITemplateParamTypeValue *i);
    virtual void visitTemplateParamExprValue(ITemplateParamExprValue *i) override;
    void py_visitTemplateParamExprValue(ITemplateParamExprValue *i);
    virtual void visitExecStmt(IExecStmt *i) override;
    void py_visitExecStmt(IExecStmt *i);
    virtual void visitExpr(IExpr *i) override;
    void py_visitExpr(IExpr *i);
    virtual void visitActivityStmt(IActivityStmt *i) override;
    void py_visitActivityStmt(IActivityStmt *i);
    virtual void visitActivitySchedulingConstraint(IActivitySchedulingConstraint *i) override;
    void py_visitActivitySchedulingConstraint(IActivitySchedulingConstraint *i);
    virtual void visitActivityJoinSpecBranch(IActivityJoinSpecBranch *i) override;
    void py_visitActivityJoinSpecBranch(IActivityJoinSpecBranch *i);
    virtual void visitActivityJoinSpecSelect(IActivityJoinSpecSelect *i) override;
    void py_visitActivityJoinSpecSelect(IActivityJoinSpecSelect *i);
    virtual void visitActivityJoinSpecNone(IActivityJoinSpecNone *i) override;
    void py_visitActivityJoinSpecNone(IActivityJoinSpecNone *i);
    virtual void visitActivityJoinSpecFirst(IActivityJoinSpecFirst *i) override;
    void py_visitActivityJoinSpecFirst(IActivityJoinSpecFirst *i);
    virtual void visitConstraintStmt(IConstraintStmt *i) override;
    void py_visitConstraintStmt(IConstraintStmt *i);
    virtual void visitScope(IScope *i) override;
    void py_visitScope(IScope *i);
    virtual void visitScopeChildRef(IScopeChildRef *i) override;
    void py_visitScopeChildRef(IScopeChildRef *i);
    virtual void visitNamedScopeChild(INamedScopeChild *i) override;
    void py_visitNamedScopeChild(INamedScopeChild *i);
    virtual void visitPackageImportStmt(IPackageImportStmt *i) override;
    void py_visitPackageImportStmt(IPackageImportStmt *i);
    virtual void visitDataType(IDataType *i) override;
    void py_visitDataType(IDataType *i);
    virtual void visitExecScope(IExecScope *i) override;
    void py_visitExecScope(IExecScope *i);
    virtual void visitProceduralStmtDataDeclaration(IProceduralStmtDataDeclaration *i) override;
    void py_visitProceduralStmtDataDeclaration(IProceduralStmtDataDeclaration *i);
    virtual void visitExprBin(IExprBin *i) override;
    void py_visitExprBin(IExprBin *i);
    virtual void visitExprBitSlice(IExprBitSlice *i) override;
    void py_visitExprBitSlice(IExprBitSlice *i);
    virtual void visitExprBool(IExprBool *i) override;
    void py_visitExprBool(IExprBool *i);
    virtual void visitExprCast(IExprCast *i) override;
    void py_visitExprCast(IExprCast *i);
    virtual void visitExprCompileHas(IExprCompileHas *i) override;
    void py_visitExprCompileHas(IExprCompileHas *i);
    virtual void visitExprCond(IExprCond *i) override;
    void py_visitExprCond(IExprCond *i);
    virtual void visitExprDomainOpenRangeList(IExprDomainOpenRangeList *i) override;
    void py_visitExprDomainOpenRangeList(IExprDomainOpenRangeList *i);
    virtual void visitExprDomainOpenRangeValue(IExprDomainOpenRangeValue *i) override;
    void py_visitExprDomainOpenRangeValue(IExprDomainOpenRangeValue *i);
    virtual void visitExprHierarchicalId(IExprHierarchicalId *i) override;
    void py_visitExprHierarchicalId(IExprHierarchicalId *i);
    virtual void visitExprId(IExprId *i) override;
    void py_visitExprId(IExprId *i);
    virtual void visitExprIn(IExprIn *i) override;
    void py_visitExprIn(IExprIn *i);
    virtual void visitExprMemberPathElem(IExprMemberPathElem *i) override;
    void py_visitExprMemberPathElem(IExprMemberPathElem *i);
    virtual void visitExprNull(IExprNull *i) override;
    void py_visitExprNull(IExprNull *i);
    virtual void visitExprNumber(IExprNumber *i) override;
    void py_visitExprNumber(IExprNumber *i);
    virtual void visitExprAggregateLiteral(IExprAggregateLiteral *i) override;
    void py_visitExprAggregateLiteral(IExprAggregateLiteral *i);
    virtual void visitExprOpenRangeList(IExprOpenRangeList *i) override;
    void py_visitExprOpenRangeList(IExprOpenRangeList *i);
    virtual void visitExprOpenRangeValue(IExprOpenRangeValue *i) override;
    void py_visitExprOpenRangeValue(IExprOpenRangeValue *i);
    virtual void visitExprRefPath(IExprRefPath *i) override;
    void py_visitExprRefPath(IExprRefPath *i);
    virtual void visitExprRefPathContext(IExprRefPathContext *i) override;
    void py_visitExprRefPathContext(IExprRefPathContext *i);
    virtual void visitExprRefPathElem(IExprRefPathElem *i) override;
    void py_visitExprRefPathElem(IExprRefPathElem *i);
    virtual void visitExprRefPathStaticRooted(IExprRefPathStaticRooted *i) override;
    void py_visitExprRefPathStaticRooted(IExprRefPathStaticRooted *i);
    virtual void visitExprStaticRefPath(IExprStaticRefPath *i) override;
    void py_visitExprStaticRefPath(IExprStaticRefPath *i);
    virtual void visitExprString(IExprString *i) override;
    void py_visitExprString(IExprString *i);
    virtual void visitExprSubscript(IExprSubscript *i) override;
    void py_visitExprSubscript(IExprSubscript *i);
    virtual void visitExprUnary(IExprUnary *i) override;
    void py_visitExprUnary(IExprUnary *i);
    virtual void visitMethodParameterList(IMethodParameterList *i) override;
    void py_visitMethodParameterList(IMethodParameterList *i);
    virtual void visitTypeIdentifier(ITypeIdentifier *i) override;
    void py_visitTypeIdentifier(ITypeIdentifier *i);
    virtual void visitTypeIdentifierElem(ITypeIdentifierElem *i) override;
    void py_visitTypeIdentifierElem(ITypeIdentifierElem *i);
    virtual void visitExtendEnum(IExtendEnum *i) override;
    void py_visitExtendEnum(IExtendEnum *i);
    virtual void visitSymbolScope(ISymbolScope *i) override;
    void py_visitSymbolScope(ISymbolScope *i);
    virtual void visitRefExprTypeScopeGlobal(IRefExprTypeScopeGlobal *i) override;
    void py_visitRefExprTypeScopeGlobal(IRefExprTypeScopeGlobal *i);
    virtual void visitRefExprTypeScopeContext(IRefExprTypeScopeContext *i) override;
    void py_visitRefExprTypeScopeContext(IRefExprTypeScopeContext *i);
    virtual void visitRefExprScopeIndex(IRefExprScopeIndex *i) override;
    void py_visitRefExprScopeIndex(IRefExprScopeIndex *i);
    virtual void visitTemplateGenericTypeParamDecl(ITemplateGenericTypeParamDecl *i) override;
    void py_visitTemplateGenericTypeParamDecl(ITemplateGenericTypeParamDecl *i);
    virtual void visitTemplateCategoryTypeParamDecl(ITemplateCategoryTypeParamDecl *i) override;
    void py_visitTemplateCategoryTypeParamDecl(ITemplateCategoryTypeParamDecl *i);
    virtual void visitTemplateValueParamDecl(ITemplateValueParamDecl *i) override;
    void py_visitTemplateValueParamDecl(ITemplateValueParamDecl *i);
    virtual void visitActivityBindStmt(IActivityBindStmt *i) override;
    void py_visitActivityBindStmt(IActivityBindStmt *i);
    virtual void visitActivityConstraint(IActivityConstraint *i) override;
    void py_visitActivityConstraint(IActivityConstraint *i);
    virtual void visitActivityLabeledStmt(IActivityLabeledStmt *i) override;
    void py_visitActivityLabeledStmt(IActivityLabeledStmt *i);
    virtual void visitActivityLabeledScope(IActivityLabeledScope *i) override;
    void py_visitActivityLabeledScope(IActivityLabeledScope *i);
    virtual void visitConstraintScope(IConstraintScope *i) override;
    void py_visitConstraintScope(IConstraintScope *i);
    virtual void visitConstraintStmtExpr(IConstraintStmtExpr *i) override;
    void py_visitConstraintStmtExpr(IConstraintStmtExpr *i);
    virtual void visitConstraintStmtField(IConstraintStmtField *i) override;
    void py_visitConstraintStmtField(IConstraintStmtField *i);
    virtual void visitConstraintStmtIf(IConstraintStmtIf *i) override;
    void py_visitConstraintStmtIf(IConstraintStmtIf *i);
    virtual void visitConstraintStmtUnique(IConstraintStmtUnique *i) override;
    void py_visitConstraintStmtUnique(IConstraintStmtUnique *i);
    virtual void visitConstraintStmtDefault(IConstraintStmtDefault *i) override;
    void py_visitConstraintStmtDefault(IConstraintStmtDefault *i);
    virtual void visitConstraintStmtDefaultDisable(IConstraintStmtDefaultDisable *i) override;
    void py_visitConstraintStmtDefaultDisable(IConstraintStmtDefaultDisable *i);
    virtual void visitGlobalScope(IGlobalScope *i) override;
    void py_visitGlobalScope(IGlobalScope *i);
    virtual void visitNamedScope(INamedScope *i) override;
    void py_visitNamedScope(INamedScope *i);
    virtual void visitPackageScope(IPackageScope *i) override;
    void py_visitPackageScope(IPackageScope *i);
    virtual void visitDataTypeArray(IDataTypeArray *i) override;
    void py_visitDataTypeArray(IDataTypeArray *i);
    virtual void visitDataTypeBool(IDataTypeBool *i) override;
    void py_visitDataTypeBool(IDataTypeBool *i);
    virtual void visitDataTypeChandle(IDataTypeChandle *i) override;
    void py_visitDataTypeChandle(IDataTypeChandle *i);
    virtual void visitDataTypeEnum(IDataTypeEnum *i) override;
    void py_visitDataTypeEnum(IDataTypeEnum *i);
    virtual void visitEnumItem(IEnumItem *i) override;
    void py_visitEnumItem(IEnumItem *i);
    virtual void visitEnumDecl(IEnumDecl *i) override;
    void py_visitEnumDecl(IEnumDecl *i);
    virtual void visitDataTypeInt(IDataTypeInt *i) override;
    void py_visitDataTypeInt(IDataTypeInt *i);
    virtual void visitDataTypeRef(IDataTypeRef *i) override;
    void py_visitDataTypeRef(IDataTypeRef *i);
    virtual void visitDataTypeString(IDataTypeString *i) override;
    void py_visitDataTypeString(IDataTypeString *i);
    virtual void visitDataTypeUserDefined(IDataTypeUserDefined *i) override;
    void py_visitDataTypeUserDefined(IDataTypeUserDefined *i);
    virtual void visitExprRefPathStatic(IExprRefPathStatic *i) override;
    void py_visitExprRefPathStatic(IExprRefPathStatic *i);
    virtual void visitExprRefPathSuper(IExprRefPathSuper *i) override;
    void py_visitExprRefPathSuper(IExprRefPathSuper *i);
    virtual void visitExprSignedNumber(IExprSignedNumber *i) override;
    void py_visitExprSignedNumber(IExprSignedNumber *i);
    virtual void visitExprUnsignedNumber(IExprUnsignedNumber *i) override;
    void py_visitExprUnsignedNumber(IExprUnsignedNumber *i);
    virtual void visitExtendType(IExtendType *i) override;
    void py_visitExtendType(IExtendType *i);
    virtual void visitField(IField *i) override;
    void py_visitField(IField *i);
    virtual void visitFieldRef(IFieldRef *i) override;
    void py_visitFieldRef(IFieldRef *i);
    virtual void visitFieldClaim(IFieldClaim *i) override;
    void py_visitFieldClaim(IFieldClaim *i);
    virtual void visitSymbolTypeScope(ISymbolTypeScope *i) override;
    void py_visitSymbolTypeScope(ISymbolTypeScope *i);
    virtual void visitSymbolFunctionScope(ISymbolFunctionScope *i) override;
    void py_visitSymbolFunctionScope(ISymbolFunctionScope *i);
    virtual void visitActivityActionHandleTraversal(IActivityActionHandleTraversal *i) override;
    void py_visitActivityActionHandleTraversal(IActivityActionHandleTraversal *i);
    virtual void visitActivityActionTypeTraversal(IActivityActionTypeTraversal *i) override;
    void py_visitActivityActionTypeTraversal(IActivityActionTypeTraversal *i);
    virtual void visitActivitySequence(IActivitySequence *i) override;
    void py_visitActivitySequence(IActivitySequence *i);
    virtual void visitActivityParallel(IActivityParallel *i) override;
    void py_visitActivityParallel(IActivityParallel *i);
    virtual void visitActivitySchedule(IActivitySchedule *i) override;
    void py_visitActivitySchedule(IActivitySchedule *i);
    virtual void visitActivityRepeatCount(IActivityRepeatCount *i) override;
    void py_visitActivityRepeatCount(IActivityRepeatCount *i);
    virtual void visitActivityRepeatWhile(IActivityRepeatWhile *i) override;
    void py_visitActivityRepeatWhile(IActivityRepeatWhile *i);
    virtual void visitActivityForeach(IActivityForeach *i) override;
    void py_visitActivityForeach(IActivityForeach *i);
    virtual void visitActivitySelect(IActivitySelect *i) override;
    void py_visitActivitySelect(IActivitySelect *i);
    virtual void visitActivityIfElse(IActivityIfElse *i) override;
    void py_visitActivityIfElse(IActivityIfElse *i);
    virtual void visitActivityMatch(IActivityMatch *i) override;
    void py_visitActivityMatch(IActivityMatch *i);
    virtual void visitActivityReplicate(IActivityReplicate *i) override;
    void py_visitActivityReplicate(IActivityReplicate *i);
    virtual void visitActivitySuper(IActivitySuper *i) override;
    void py_visitActivitySuper(IActivitySuper *i);
    virtual void visitConstraintBlock(IConstraintBlock *i) override;
    void py_visitConstraintBlock(IConstraintBlock *i);
    virtual void visitConstraintStmtForeach(IConstraintStmtForeach *i) override;
    void py_visitConstraintStmtForeach(IConstraintStmtForeach *i);
    virtual void visitConstraintStmtForall(IConstraintStmtForall *i) override;
    void py_visitConstraintStmtForall(IConstraintStmtForall *i);
    virtual void visitConstraintStmtImplication(IConstraintStmtImplication *i) override;
    void py_visitConstraintStmtImplication(IConstraintStmtImplication *i);
    virtual void visitExprRefPathStaticFunc(IExprRefPathStaticFunc *i) override;
    void py_visitExprRefPathStaticFunc(IExprRefPathStaticFunc *i);
    virtual void visitTypeScope(ITypeScope *i) override;
    void py_visitTypeScope(ITypeScope *i);
    virtual void visitStruct(IStruct *i) override;
    void py_visitStruct(IStruct *i);
    virtual void visitAction(IAction *i) override;
    void py_visitAction(IAction *i);
    virtual void visitComponent(IComponent *i) override;
    void py_visitComponent(IComponent *i);
};

} // namespace zsp
} // namespace ast

