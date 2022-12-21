# cython: language_level=3
from enum import IntEnum
from libcpp.cast cimport dynamic_cast
from libcpp.cast cimport static_cast
from libcpp.string cimport string as      std_string
from libcpp.map cimport map as            std_map
from libcpp.memory cimport unique_ptr, shared_ptr
from libcpp.vector cimport vector as std_vector
from libcpp.utility cimport pair as  std_pair
from libcpp cimport bool as          bool
cimport cpython.ref as cpy_ref

ctypedef char                 int8_t
ctypedef unsigned char        uint8_t
ctypedef short                int16_t
ctypedef unsigned short       uint16_t
ctypedef int                  int32_t
ctypedef unsigned int         uint32_t
ctypedef long long            int64_t
ctypedef unsigned long long   uint64_t

ctypedef ISymbolImportSpec *ISymbolImportSpecP
ctypedef IScopeChild *IScopeChildP
ctypedef IActivityJoinSpec *IActivityJoinSpecP
ctypedef ISymbolRefPath *ISymbolRefPathP
ctypedef IRefExpr *IRefExprP
ctypedef ITemplateParamDeclList *ITemplateParamDeclListP
ctypedef ITemplateParamDecl *ITemplateParamDeclP
ctypedef IActivitySelectBranch *IActivitySelectBranchP
ctypedef ITemplateParamValueList *ITemplateParamValueListP
ctypedef ITemplateParamValue *ITemplateParamValueP
ctypedef IActivityMatchChoice *IActivityMatchChoiceP
ctypedef ITemplateParamTypeValue *ITemplateParamTypeValueP
ctypedef ITemplateParamExprValue *ITemplateParamExprValueP
ctypedef IExecStmt *IExecStmtP
ctypedef IExpr *IExprP
ctypedef IActivityStmt *IActivityStmtP
ctypedef IActivitySchedulingConstraint *IActivitySchedulingConstraintP
ctypedef IActivityJoinSpecBranch *IActivityJoinSpecBranchP
ctypedef IActivityJoinSpecSelect *IActivityJoinSpecSelectP
ctypedef IActivityJoinSpecNone *IActivityJoinSpecNoneP
ctypedef IActivityJoinSpecFirst *IActivityJoinSpecFirstP
ctypedef IConstraintStmt *IConstraintStmtP
ctypedef IScope *IScopeP
ctypedef IScopeChildRef *IScopeChildRefP
ctypedef INamedScopeChild *INamedScopeChildP
ctypedef IPackageImportStmt *IPackageImportStmtP
ctypedef IDataType *IDataTypeP
ctypedef IExecScope *IExecScopeP
ctypedef IProceduralStmtDataDeclaration *IProceduralStmtDataDeclarationP
ctypedef IExprBin *IExprBinP
ctypedef IExprBitSlice *IExprBitSliceP
ctypedef IExprBool *IExprBoolP
ctypedef IExprCast *IExprCastP
ctypedef IExprCompileHas *IExprCompileHasP
ctypedef IExprCond *IExprCondP
ctypedef IExprDomainOpenRangeList *IExprDomainOpenRangeListP
ctypedef IExprDomainOpenRangeValue *IExprDomainOpenRangeValueP
ctypedef IExprHierarchicalId *IExprHierarchicalIdP
ctypedef IExprId *IExprIdP
ctypedef IExprIn *IExprInP
ctypedef IExprMemberPathElem *IExprMemberPathElemP
ctypedef IExprNull *IExprNullP
ctypedef IExprNumber *IExprNumberP
ctypedef IExprAggregateLiteral *IExprAggregateLiteralP
ctypedef IExprOpenRangeList *IExprOpenRangeListP
ctypedef IExprOpenRangeValue *IExprOpenRangeValueP
ctypedef IExprRefPath *IExprRefPathP
ctypedef IExprRefPathContext *IExprRefPathContextP
ctypedef IExprRefPathElem *IExprRefPathElemP
ctypedef IExprRefPathStaticRooted *IExprRefPathStaticRootedP
ctypedef IExprStaticRefPath *IExprStaticRefPathP
ctypedef IExprString *IExprStringP
ctypedef IExprSubscript *IExprSubscriptP
ctypedef IExprUnary *IExprUnaryP
ctypedef IMethodParameterList *IMethodParameterListP
ctypedef ITypeIdentifier *ITypeIdentifierP
ctypedef ITypeIdentifierElem *ITypeIdentifierElemP
ctypedef IExtendEnum *IExtendEnumP
ctypedef ISymbolScope *ISymbolScopeP
ctypedef IRefExprTypeScopeGlobal *IRefExprTypeScopeGlobalP
ctypedef IRefExprTypeScopeContext *IRefExprTypeScopeContextP
ctypedef IRefExprScopeIndex *IRefExprScopeIndexP
ctypedef ITemplateGenericTypeParamDecl *ITemplateGenericTypeParamDeclP
ctypedef ITemplateCategoryTypeParamDecl *ITemplateCategoryTypeParamDeclP
ctypedef ITemplateValueParamDecl *ITemplateValueParamDeclP
ctypedef IActivityBindStmt *IActivityBindStmtP
ctypedef IActivityConstraint *IActivityConstraintP
ctypedef IActivityLabeledStmt *IActivityLabeledStmtP
ctypedef IActivityLabeledScope *IActivityLabeledScopeP
ctypedef IConstraintScope *IConstraintScopeP
ctypedef IConstraintStmtExpr *IConstraintStmtExprP
ctypedef IConstraintStmtField *IConstraintStmtFieldP
ctypedef IConstraintStmtIf *IConstraintStmtIfP
ctypedef IConstraintStmtUnique *IConstraintStmtUniqueP
ctypedef IConstraintStmtDefault *IConstraintStmtDefaultP
ctypedef IConstraintStmtDefaultDisable *IConstraintStmtDefaultDisableP
ctypedef IGlobalScope *IGlobalScopeP
ctypedef INamedScope *INamedScopeP
ctypedef IPackageScope *IPackageScopeP
ctypedef IDataTypeArray *IDataTypeArrayP
ctypedef IDataTypeBool *IDataTypeBoolP
ctypedef IDataTypeChandle *IDataTypeChandleP
ctypedef IDataTypeEnum *IDataTypeEnumP
ctypedef IEnumItem *IEnumItemP
ctypedef IEnumDecl *IEnumDeclP
ctypedef IDataTypeInt *IDataTypeIntP
ctypedef IDataTypeRef *IDataTypeRefP
ctypedef IDataTypeString *IDataTypeStringP
ctypedef IDataTypeUserDefined *IDataTypeUserDefinedP
ctypedef IExprRefPathStatic *IExprRefPathStaticP
ctypedef IExprRefPathSuper *IExprRefPathSuperP
ctypedef IExprSignedNumber *IExprSignedNumberP
ctypedef IExprUnsignedNumber *IExprUnsignedNumberP
ctypedef IExtendType *IExtendTypeP
ctypedef IField *IFieldP
ctypedef IFieldRef *IFieldRefP
ctypedef IFieldClaim *IFieldClaimP
ctypedef ISymbolTypeScope *ISymbolTypeScopeP
ctypedef ISymbolFunctionScope *ISymbolFunctionScopeP
ctypedef IActivityActionHandleTraversal *IActivityActionHandleTraversalP
ctypedef IActivityActionTypeTraversal *IActivityActionTypeTraversalP
ctypedef IActivitySequence *IActivitySequenceP
ctypedef IActivityParallel *IActivityParallelP
ctypedef IActivitySchedule *IActivityScheduleP
ctypedef IActivityRepeatCount *IActivityRepeatCountP
ctypedef IActivityRepeatWhile *IActivityRepeatWhileP
ctypedef IActivityForeach *IActivityForeachP
ctypedef IActivitySelect *IActivitySelectP
ctypedef IActivityIfElse *IActivityIfElseP
ctypedef IActivityMatch *IActivityMatchP
ctypedef IActivityReplicate *IActivityReplicateP
ctypedef IActivitySuper *IActivitySuperP
ctypedef IConstraintBlock *IConstraintBlockP
ctypedef IConstraintStmtForeach *IConstraintStmtForeachP
ctypedef IConstraintStmtForall *IConstraintStmtForallP
ctypedef IConstraintStmtImplication *IConstraintStmtImplicationP
ctypedef IExprRefPathStaticFunc *IExprRefPathStaticFuncP
ctypedef ITypeScope *ITypeScopeP
ctypedef IStruct *IStructP
ctypedef IAction *IActionP
ctypedef IComponent *IComponentP
cdef extern from "zsp/ast/ExprBinOp.h" namespace "zsp::ast":
    cdef enum ExprBinOp:
        ExprBinOp_BinOp_LogOr "zsp::ast::ExprBinOp::BinOp_LogOr"
        ExprBinOp_BinOp_LogAnd "zsp::ast::ExprBinOp::BinOp_LogAnd"
        ExprBinOp_BinOp_BitOr "zsp::ast::ExprBinOp::BinOp_BitOr"
        ExprBinOp_BinOp_BitXor "zsp::ast::ExprBinOp::BinOp_BitXor"
        ExprBinOp_BinOp_BitAnd "zsp::ast::ExprBinOp::BinOp_BitAnd"
        ExprBinOp_BinOp_Lt "zsp::ast::ExprBinOp::BinOp_Lt"
        ExprBinOp_BinOp_Le "zsp::ast::ExprBinOp::BinOp_Le"
        ExprBinOp_BinOp_Gt "zsp::ast::ExprBinOp::BinOp_Gt"
        ExprBinOp_BinOp_Ge "zsp::ast::ExprBinOp::BinOp_Ge"
        ExprBinOp_BinOp_Exp "zsp::ast::ExprBinOp::BinOp_Exp"
        ExprBinOp_BinOp_Mul "zsp::ast::ExprBinOp::BinOp_Mul"
        ExprBinOp_BinOp_Div "zsp::ast::ExprBinOp::BinOp_Div"
        ExprBinOp_BinOp_Mod "zsp::ast::ExprBinOp::BinOp_Mod"
        ExprBinOp_BinOp_Add "zsp::ast::ExprBinOp::BinOp_Add"
        ExprBinOp_BinOp_Sub "zsp::ast::ExprBinOp::BinOp_Sub"
        ExprBinOp_BinOp_Shl "zsp::ast::ExprBinOp::BinOp_Shl"
        ExprBinOp_BinOp_Shr "zsp::ast::ExprBinOp::BinOp_Shr"
        ExprBinOp_BinOp_Eq "zsp::ast::ExprBinOp::BinOp_Eq"
        ExprBinOp_BinOp_Ne "zsp::ast::ExprBinOp::BinOp_Ne"
cdef extern from "zsp/ast/ExprUnaryOp.h" namespace "zsp::ast":
    cdef enum ExprUnaryOp:
        ExprUnaryOp_UnaryOp_Plus "zsp::ast::ExprUnaryOp::UnaryOp_Plus"
        ExprUnaryOp_UnaryOp_Minus "zsp::ast::ExprUnaryOp::UnaryOp_Minus"
        ExprUnaryOp_UnaryOp_LogNot "zsp::ast::ExprUnaryOp::UnaryOp_LogNot"
        ExprUnaryOp_UnaryOp_BitNeg "zsp::ast::ExprUnaryOp::UnaryOp_BitNeg"
        ExprUnaryOp_UnaryOp_BitAnd "zsp::ast::ExprUnaryOp::UnaryOp_BitAnd"
        ExprUnaryOp_UnaryOp_BitOr "zsp::ast::ExprUnaryOp::UnaryOp_BitOr"
        ExprUnaryOp_UnaryOp_BitXor "zsp::ast::ExprUnaryOp::UnaryOp_BitXor"
cdef extern from "zsp/ast/ExtendTargetE.h" namespace "zsp::ast":
    cdef enum ExtendTargetE:
        ExtendTargetE_Action "zsp::ast::ExtendTargetE::Action"
        ExtendTargetE_Buffer "zsp::ast::ExtendTargetE::Buffer"
        ExtendTargetE_Component "zsp::ast::ExtendTargetE::Component"
        ExtendTargetE_Enum "zsp::ast::ExtendTargetE::Enum"
        ExtendTargetE_Resource "zsp::ast::ExtendTargetE::Resource"
        ExtendTargetE_State "zsp::ast::ExtendTargetE::State"
        ExtendTargetE_Stream "zsp::ast::ExtendTargetE::Stream"
        ExtendTargetE_Struct "zsp::ast::ExtendTargetE::Struct"
cdef extern from "zsp/ast/StructKind.h" namespace "zsp::ast":
    cdef enum StructKind:
        StructKind_Buffer "zsp::ast::StructKind::Buffer"
        StructKind_Struct "zsp::ast::StructKind::Struct"
        StructKind_Resource "zsp::ast::StructKind::Resource"
        StructKind_Stream "zsp::ast::StructKind::Stream"
        StructKind_State "zsp::ast::StructKind::State"
cdef extern from "zsp/ast/TypeCategory.h" namespace "zsp::ast":
    cdef enum TypeCategory:
        TypeCategory_Action "zsp::ast::TypeCategory::Action"
        TypeCategory_Component "zsp::ast::TypeCategory::Component"
        TypeCategory_Buffer "zsp::ast::TypeCategory::Buffer"
        TypeCategory_Resource "zsp::ast::TypeCategory::Resource"
        TypeCategory_State "zsp::ast::TypeCategory::State"
        TypeCategory_Stream "zsp::ast::TypeCategory::Stream"
cdef extern from "zsp/ast/FieldAttr.h" namespace "zsp::ast":
    cdef enum FieldAttr:
        FieldAttr_Action "zsp::ast::FieldAttr::Action"
        FieldAttr_Builtin "zsp::ast::FieldAttr::Builtin"
        FieldAttr_Rand "zsp::ast::FieldAttr::Rand"
        FieldAttr_Const "zsp::ast::FieldAttr::Const"
        FieldAttr_Static "zsp::ast::FieldAttr::Static"
        FieldAttr_Private "zsp::ast::FieldAttr::Private"
        FieldAttr_Protected "zsp::ast::FieldAttr::Protected"
cdef extern from "zsp/ast/IFactory.h" namespace "zsp::ast":
    cdef cppclass IFactory:
        ISymbolImportSpec *mkSymbolImportSpec(
                )
        IScopeChild *mkScopeChild(
                )
        IActivityJoinSpec *mkActivityJoinSpec(
                )
        ISymbolRefPath *mkSymbolRefPath(
                )
        IRefExpr *mkRefExpr(
                )
        ITemplateParamDeclList *mkTemplateParamDeclList(
                )
        ITemplateParamDecl *mkTemplateParamDecl(
                IExprIdP name)
        IActivitySelectBranch *mkActivitySelectBranch(
                IExprP guard,
                IExprP weight,
                IScopeChildP body)
        ITemplateParamValueList *mkTemplateParamValueList(
                )
        ITemplateParamValue *mkTemplateParamValue(
                )
        IActivityMatchChoice *mkActivityMatchChoice(
                bool is_default,
                IExprOpenRangeListP cond,
                IScopeChildP body)
        ITemplateParamTypeValue *mkTemplateParamTypeValue(
                ITypeIdentifierP value)
        ITemplateParamExprValue *mkTemplateParamExprValue(
                IExprP value)
        IExecStmt *mkExecStmt(
                )
        IExpr *mkExpr(
                )
        IActivityStmt *mkActivityStmt(
                )
        IActivitySchedulingConstraint *mkActivitySchedulingConstraint(
                bool is_parallel)
        IActivityJoinSpecBranch *mkActivityJoinSpecBranch(
                )
        IActivityJoinSpecSelect *mkActivityJoinSpecSelect(
                IExprP count)
        IActivityJoinSpecNone *mkActivityJoinSpecNone(
                )
        IActivityJoinSpecFirst *mkActivityJoinSpecFirst(
                IExprP count)
        IConstraintStmt *mkConstraintStmt(
                )
        IScope *mkScope(
                )
        IScopeChildRef *mkScopeChildRef(
                IScopeChildP target)
        INamedScopeChild *mkNamedScopeChild(
                IExprIdP name)
        IPackageImportStmt *mkPackageImportStmt(
                bool wildcard,
                IExprIdP alias)
        IDataType *mkDataType(
                )
        IExecScope *mkExecScope(
                )
        IProceduralStmtDataDeclaration *mkProceduralStmtDataDeclaration(
                IDataTypeP datatype,
                IExprIdP name)
        IExprBin *mkExprBin(
                IExprP lhs,
                ExprBinOp op,
                IExprP rhs)
        IExprBitSlice *mkExprBitSlice(
                IExprP expr,
                IExprP lhs,
                IExprP rhs)
        IExprBool *mkExprBool(
                bool value)
        IExprCast *mkExprCast(
                IDataTypeP casting_type,
                IExprP expr)
        IExprCompileHas *mkExprCompileHas(
                IExprRefPathStaticP ref)
        IExprCond *mkExprCond(
                IExprP cond_e,
                IExprP true_e,
                IExprP false_e)
        IExprDomainOpenRangeList *mkExprDomainOpenRangeList(
                )
        IExprDomainOpenRangeValue *mkExprDomainOpenRangeValue(
                bool single,
                IExprP lhs,
                IExprP rhs)
        IExprHierarchicalId *mkExprHierarchicalId(
                )
        IExprId *mkExprId(
                std_string id,
                bool is_escaped)
        IExprIn *mkExprIn(
                IExprP lhs,
                IExprOpenRangeListP rhs)
        IExprMemberPathElem *mkExprMemberPathElem(
                IExprIdP id,
                IMethodParameterListP params,
                IExprP subscript)
        IExprNull *mkExprNull(
                )
        IExprNumber *mkExprNumber(
                )
        IExprAggregateLiteral *mkExprAggregateLiteral(
                )
        IExprOpenRangeList *mkExprOpenRangeList(
                )
        IExprOpenRangeValue *mkExprOpenRangeValue(
                IExprP lhs,
                IExprP rhs)
        IExprRefPath *mkExprRefPath(
                )
        IExprRefPathContext *mkExprRefPathContext(
                IExprHierarchicalIdP hier_id)
        IExprRefPathElem *mkExprRefPathElem(
                )
        IExprRefPathStaticRooted *mkExprRefPathStaticRooted(
                IExprRefPathStaticP root,
                IExprRefPathContextP leaf)
        IExprStaticRefPath *mkExprStaticRefPath(
                bool is_global,
                IExprMemberPathElemP leaf)
        IExprString *mkExprString(
                std_string value,
                bool is_raw)
        IExprSubscript *mkExprSubscript(
                IExprP expr,
                IExprP subscript)
        IExprUnary *mkExprUnary(
                ExprUnaryOp op,
                IExprP rhs)
        IMethodParameterList *mkMethodParameterList(
                )
        ITypeIdentifier *mkTypeIdentifier(
                )
        ITypeIdentifierElem *mkTypeIdentifierElem(
                IExprIdP id)
        IExtendEnum *mkExtendEnum(
                ITypeIdentifierP target)
        ISymbolScope *mkSymbolScope(
                int32_t id,
                std_string name)
        IRefExprTypeScopeGlobal *mkRefExprTypeScopeGlobal(
                int32_t fileid)
        IRefExprTypeScopeContext *mkRefExprTypeScopeContext(
                IRefExprP base,
                int32_t offset)
        IRefExprScopeIndex *mkRefExprScopeIndex(
                IRefExprP base,
                int32_t offset)
        ITemplateGenericTypeParamDecl *mkTemplateGenericTypeParamDecl(
                IExprIdP name,
                ITypeIdentifierP dflt)
        ITemplateCategoryTypeParamDecl *mkTemplateCategoryTypeParamDecl(
                IExprIdP name,
                TypeCategory category,
                ITypeIdentifierP restriction,
                ITypeIdentifierP dflt)
        ITemplateValueParamDecl *mkTemplateValueParamDecl(
                IExprIdP name,
                IExprP dflt)
        IActivityBindStmt *mkActivityBindStmt(
                IExprHierarchicalIdP lhs)
        IActivityConstraint *mkActivityConstraint(
                IConstraintStmtP constraint)
        IActivityLabeledStmt *mkActivityLabeledStmt(
                )
        IActivityLabeledScope *mkActivityLabeledScope(
                )
        IConstraintScope *mkConstraintScope(
                )
        IConstraintStmtExpr *mkConstraintStmtExpr(
                IExprP expr)
        IConstraintStmtField *mkConstraintStmtField(
                IExprIdP name,
                IDataTypeP type)
        IConstraintStmtIf *mkConstraintStmtIf(
                IExprP cond,
                IConstraintScopeP true_c,
                IConstraintScopeP false_c)
        IConstraintStmtUnique *mkConstraintStmtUnique(
                )
        IConstraintStmtDefault *mkConstraintStmtDefault(
                IExprHierarchicalIdP hid,
                IExprP expr)
        IConstraintStmtDefaultDisable *mkConstraintStmtDefaultDisable(
                IExprHierarchicalIdP hid)
        IGlobalScope *mkGlobalScope(
                int32_t fileid)
        INamedScope *mkNamedScope(
                IExprIdP name)
        IPackageScope *mkPackageScope(
                )
        IDataTypeArray *mkDataTypeArray(
                IDataTypeP type,
                IExprP size)
        IDataTypeBool *mkDataTypeBool(
                )
        IDataTypeChandle *mkDataTypeChandle(
                )
        IDataTypeEnum *mkDataTypeEnum(
                IDataTypeUserDefinedP tid,
                IExprOpenRangeListP in_rangelist)
        IEnumItem *mkEnumItem(
                IExprIdP name,
                IExprP value)
        IEnumDecl *mkEnumDecl(
                IExprIdP name)
        IDataTypeInt *mkDataTypeInt(
                bool is_signed,
                IExprP width,
                IExprDomainOpenRangeListP in_range)
        IDataTypeRef *mkDataTypeRef(
                IDataTypeUserDefinedP type)
        IDataTypeString *mkDataTypeString(
                bool has_range)
        IDataTypeUserDefined *mkDataTypeUserDefined(
                bool is_global,
                ITypeIdentifierP type_id)
        IExprRefPathStatic *mkExprRefPathStatic(
                bool is_global,
                IExprBitSliceP slice)
        IExprRefPathSuper *mkExprRefPathSuper(
                IExprHierarchicalIdP hier_id)
        IExprSignedNumber *mkExprSignedNumber(
                std_string image,
                int32_t width,
                int64_t value)
        IExprUnsignedNumber *mkExprUnsignedNumber(
                std_string image,
                int32_t width,
                uint64_t value)
        IExtendType *mkExtendType(
                ExtendTargetE kind,
                ITypeIdentifierP target)
        IField *mkField(
                IExprIdP name,
                IDataTypeP type,
                FieldAttr attr,
                IExprP array_dim,
                IExprP init)
        IFieldRef *mkFieldRef(
                IExprIdP name,
                IDataTypeUserDefinedP type,
                IExprP array_dim,
                bool is_input)
        IFieldClaim *mkFieldClaim(
                IExprIdP name,
                IDataTypeUserDefinedP type,
                IExprP array_dim,
                bool is_lock)
        ISymbolTypeScope *mkSymbolTypeScope(
                int32_t id,
                std_string name,
                ISymbolScopeP plist)
        ISymbolFunctionScope *mkSymbolFunctionScope(
                int32_t id,
                std_string name,
                ISymbolScopeP plist)
        IActivityActionHandleTraversal *mkActivityActionHandleTraversal(
                IExprRefPathContextP target,
                IConstraintStmtP with_c)
        IActivityActionTypeTraversal *mkActivityActionTypeTraversal(
                IDataTypeUserDefinedP target,
                IConstraintStmtP with_c)
        IActivitySequence *mkActivitySequence(
                )
        IActivityParallel *mkActivityParallel(
                IActivityJoinSpecP join_spec)
        IActivitySchedule *mkActivitySchedule(
                IActivityJoinSpecP join_spec)
        IActivityRepeatCount *mkActivityRepeatCount(
                IExprIdP loop_var,
                IExprP count,
                IScopeChildP body)
        IActivityRepeatWhile *mkActivityRepeatWhile(
                IExprP cond,
                IScopeChildP body)
        IActivityForeach *mkActivityForeach(
                IExprIdP it_id,
                IExprIdP idx_id,
                IExprRefPathContextP target,
                IScopeChildP body)
        IActivitySelect *mkActivitySelect(
                )
        IActivityIfElse *mkActivityIfElse(
                IExprP cond,
                IActivityStmtP true_s,
                IActivityStmtP false_s)
        IActivityMatch *mkActivityMatch(
                IExprP cond)
        IActivityReplicate *mkActivityReplicate(
                IExprIdP idx_id,
                IExprIdP it_label,
                IScopeChildP body)
        IActivitySuper *mkActivitySuper(
                )
        IConstraintBlock *mkConstraintBlock(
                std_string name,
                bool is_dynamic)
        IConstraintStmtForeach *mkConstraintStmtForeach(
                IExprP expr)
        IConstraintStmtForall *mkConstraintStmtForall(
                IExprIdP iterator_id,
                IDataTypeUserDefinedP type_id,
                IExprRefPathP ref_path)
        IConstraintStmtImplication *mkConstraintStmtImplication(
                IExprP cond)
        IExprRefPathStaticFunc *mkExprRefPathStaticFunc(
                bool is_global,
                IExprBitSliceP slice,
                IMethodParameterListP params)
        ITypeScope *mkTypeScope(
                IExprIdP name,
                ITypeIdentifierP super_t)
        IStruct *mkStruct(
                IExprIdP name,
                ITypeIdentifierP super_t,
                StructKind kind)
        IAction *mkAction(
                IExprIdP name,
                ITypeIdentifierP super_t,
                bool is_abstract)
        IComponent *mkComponent(
                IExprIdP name,
                ITypeIdentifierP super_t)
cdef extern from "zsp/ast/ISymbolImportSpec.h" namespace "zsp::ast":
    cpdef cppclass ISymbolImportSpec:
        std_vector[IPackageImportStmtP] &getImports();
        std_map[std_string,unique_ptr[ISymbolRefPath]] &getSymtab();
        void accept(VisitorBase *v)

cdef extern from "zsp/ast/IScopeChild.h" namespace "zsp::ast":
    cpdef cppclass IScopeChild:
        const std_string &getDocstring()
        
        void set_docstring(const std_string &v)
        IScopePgetParent();
        
        void setParent(IScopePv)
        int32_t getIndex()
        
        void setIndex(int32_t v)
        void accept(VisitorBase *v)

cdef extern from "zsp/ast/IActivityJoinSpec.h" namespace "zsp::ast":
    cpdef cppclass IActivityJoinSpec:
        pass
        void accept(VisitorBase *v)

cdef extern from "zsp/ast/ISymbolRefPath.h" namespace "zsp::ast":
    cpdef cppclass ISymbolRefPath:
        std_vector[int32_t] &getPath();
        void accept(VisitorBase *v)

cdef extern from "zsp/ast/IRefExpr.h" namespace "zsp::ast":
    cpdef cppclass IRefExpr:
        pass
        void accept(VisitorBase *v)

cdef extern from "zsp/ast/ITemplateParamDeclList.h" namespace "zsp::ast":
    cpdef cppclass ITemplateParamDeclList:
        std_vector[unique_ptr[ITemplateParamDecl]] &getParams();
        void accept(VisitorBase *v)

cdef extern from "zsp/ast/ITemplateParamDecl.h" namespace "zsp::ast":
    cpdef cppclass ITemplateParamDecl:
        IExprIdgetName()
        
        void setName(IExprIdv)
        void accept(VisitorBase *v)

cdef extern from "zsp/ast/IActivitySelectBranch.h" namespace "zsp::ast":
    cpdef cppclass IActivitySelectBranch:
        IExprgetGuard()
        
        void setGuard(IExprv)
        IExprgetWeight()
        
        void setWeight(IExprv)
        IScopeChildgetBody()
        
        void setBody(IScopeChildv)
        void accept(VisitorBase *v)

cdef extern from "zsp/ast/ITemplateParamValueList.h" namespace "zsp::ast":
    cpdef cppclass ITemplateParamValueList:
        std_vector[unique_ptr[ITemplateParamValue]] &getValues();
        void accept(VisitorBase *v)

cdef extern from "zsp/ast/ITemplateParamValue.h" namespace "zsp::ast":
    cpdef cppclass ITemplateParamValue:
        pass
        void accept(VisitorBase *v)

cdef extern from "zsp/ast/IActivityMatchChoice.h" namespace "zsp::ast":
    cpdef cppclass IActivityMatchChoice:
        bool getIs_default()
        
        void setIs_default(bool v)
        IExprOpenRangeListgetCond()
        
        void setCond(IExprOpenRangeListv)
        IScopeChildgetBody()
        
        void setBody(IScopeChildv)
        void accept(VisitorBase *v)

cdef extern from "zsp/ast/ITemplateParamTypeValue.h" namespace "zsp::ast":
    cpdef cppclass ITemplateParamTypeValue:
        ITypeIdentifiergetValue()
        
        void setValue(ITypeIdentifierv)
        void accept(VisitorBase *v)

cdef extern from "zsp/ast/ITemplateParamExprValue.h" namespace "zsp::ast":
    cpdef cppclass ITemplateParamExprValue:
        IExprgetValue()
        
        void setValue(IExprv)
        void accept(VisitorBase *v)

cdef extern from "zsp/ast/IExecStmt.h" namespace "zsp::ast":
    cpdef cppclass IExecStmt:
        pass
        void accept(VisitorBase *v)

cdef extern from "zsp/ast/IExpr.h" namespace "zsp::ast":
    cpdef cppclass IExpr:
        pass
        void accept(VisitorBase *v)

cdef extern from "zsp/ast/IActivityStmt.h" namespace "zsp::ast":
    cpdef cppclass IActivityStmt(IScopeChild):
        pass

cdef extern from "zsp/ast/IActivitySchedulingConstraint.h" namespace "zsp::ast":
    cpdef cppclass IActivitySchedulingConstraint(IScopeChild):
        bool getIs_parallel()
        
        void setIs_parallel(bool v)
        std_vector[unique_ptr[IExprHierarchicalId]] &getTargets();

cdef extern from "zsp/ast/IActivityJoinSpecBranch.h" namespace "zsp::ast":
    cpdef cppclass IActivityJoinSpecBranch(IActivityJoinSpec):
        std_vector[unique_ptr[IExprRefPathContext]] &getBranches();

cdef extern from "zsp/ast/IActivityJoinSpecSelect.h" namespace "zsp::ast":
    cpdef cppclass IActivityJoinSpecSelect(IActivityJoinSpec):
        IExprgetCount()
        
        void setCount(IExprv)

cdef extern from "zsp/ast/IActivityJoinSpecNone.h" namespace "zsp::ast":
    cpdef cppclass IActivityJoinSpecNone(IActivityJoinSpec):
        pass

cdef extern from "zsp/ast/IActivityJoinSpecFirst.h" namespace "zsp::ast":
    cpdef cppclass IActivityJoinSpecFirst(IActivityJoinSpec):
        IExprgetCount()
        
        void setCount(IExprv)

cdef extern from "zsp/ast/IConstraintStmt.h" namespace "zsp::ast":
    cpdef cppclass IConstraintStmt(IScopeChild):
        pass

cdef extern from "zsp/ast/IScope.h" namespace "zsp::ast":
    cpdef cppclass IScope(IScopeChild):
        std_vector[unique_ptr[IScopeChild]] &getChildren();
        std_map[std_string,INamedScopeChildP] &getSymtab();

cdef extern from "zsp/ast/IScopeChildRef.h" namespace "zsp::ast":
    cpdef cppclass IScopeChildRef(IScopeChild):
        IScopeChildPgetTarget();
        
        void setTarget(IScopeChildPv)

cdef extern from "zsp/ast/INamedScopeChild.h" namespace "zsp::ast":
    cpdef cppclass INamedScopeChild(IScopeChild):
        IExprIdgetName()
        
        void setName(IExprIdv)

cdef extern from "zsp/ast/IPackageImportStmt.h" namespace "zsp::ast":
    cpdef cppclass IPackageImportStmt(IScopeChild):
        bool getWildcard()
        
        void setWildcard(bool v)
        IExprIdgetAlias()
        
        void setAlias(IExprIdv)
        ITypeIdentifiergetPath()
        
        void setPath(ITypeIdentifierv)

cdef extern from "zsp/ast/IDataType.h" namespace "zsp::ast":
    cpdef cppclass IDataType(IScopeChild):
        pass

cdef extern from "zsp/ast/IExecScope.h" namespace "zsp::ast":
    cpdef cppclass IExecScope(IExecStmt):
        std_vector[unique_ptr[IExecStmt]] &getChildren();

cdef extern from "zsp/ast/IProceduralStmtDataDeclaration.h" namespace "zsp::ast":
    cpdef cppclass IProceduralStmtDataDeclaration(IExecStmt):
        IDataTypegetDatatype()
        
        void setDatatype(IDataTypev)
        IExprIdgetName()
        
        void setName(IExprIdv)

cdef extern from "zsp/ast/IExprBin.h" namespace "zsp::ast":
    cpdef cppclass IExprBin(IExpr):
        IExprgetLhs()
        
        void setLhs(IExprv)
        ExprBinOp getOp()
        
        void setOp(ExprBinOp v)
        IExprgetRhs()
        
        void setRhs(IExprv)

cdef extern from "zsp/ast/IExprBitSlice.h" namespace "zsp::ast":
    cpdef cppclass IExprBitSlice(IExpr):
        IExprgetExpr()
        
        void setExpr(IExprv)
        IExprgetLhs()
        
        void setLhs(IExprv)
        IExprgetRhs()
        
        void setRhs(IExprv)

cdef extern from "zsp/ast/IExprBool.h" namespace "zsp::ast":
    cpdef cppclass IExprBool(IExpr):
        bool getValue()
        
        void setValue(bool v)

cdef extern from "zsp/ast/IExprCast.h" namespace "zsp::ast":
    cpdef cppclass IExprCast(IExpr):
        IDataTypegetCasting_type()
        
        void setCasting_type(IDataTypev)
        IExprgetExpr()
        
        void setExpr(IExprv)

cdef extern from "zsp/ast/IExprCompileHas.h" namespace "zsp::ast":
    cpdef cppclass IExprCompileHas(IExpr):
        IExprRefPathStaticgetRef()
        
        void setRef(IExprRefPathStaticv)

cdef extern from "zsp/ast/IExprCond.h" namespace "zsp::ast":
    cpdef cppclass IExprCond(IExpr):
        IExprgetCond_e()
        
        void setCond_e(IExprv)
        IExprgetTrue_e()
        
        void setTrue_e(IExprv)
        IExprgetFalse_e()
        
        void setFalse_e(IExprv)

cdef extern from "zsp/ast/IExprDomainOpenRangeList.h" namespace "zsp::ast":
    cpdef cppclass IExprDomainOpenRangeList(IExpr):
        std_vector[unique_ptr[IExprDomainOpenRangeValue]] &getValues();

cdef extern from "zsp/ast/IExprDomainOpenRangeValue.h" namespace "zsp::ast":
    cpdef cppclass IExprDomainOpenRangeValue(IExpr):
        bool getSingle()
        
        void setSingle(bool v)
        IExprgetLhs()
        
        void setLhs(IExprv)
        IExprgetRhs()
        
        void setRhs(IExprv)

cdef extern from "zsp/ast/IExprHierarchicalId.h" namespace "zsp::ast":
    cpdef cppclass IExprHierarchicalId(IExpr):
        std_vector[unique_ptr[IExprMemberPathElem]] &getElems();

cdef extern from "zsp/ast/IExprId.h" namespace "zsp::ast":
    cpdef cppclass IExprId(IExpr):
        const std_string &getId()
        
        void set_id(const std_string &v)
        bool getIs_escaped()
        
        void setIs_escaped(bool v)

cdef extern from "zsp/ast/IExprIn.h" namespace "zsp::ast":
    cpdef cppclass IExprIn(IExpr):
        IExprgetLhs()
        
        void setLhs(IExprv)
        IExprOpenRangeListgetRhs()
        
        void setRhs(IExprOpenRangeListv)

cdef extern from "zsp/ast/IExprMemberPathElem.h" namespace "zsp::ast":
    cpdef cppclass IExprMemberPathElem(IExpr):
        IExprIdgetId()
        
        void setId(IExprIdv)
        IMethodParameterListgetParams()
        
        void setParams(IMethodParameterListv)
        IExprgetSubscript()
        
        void setSubscript(IExprv)
        int32_t getTarget()
        
        void setTarget(int32_t v)

cdef extern from "zsp/ast/IExprNull.h" namespace "zsp::ast":
    cpdef cppclass IExprNull(IExpr):
        pass

cdef extern from "zsp/ast/IExprNumber.h" namespace "zsp::ast":
    cpdef cppclass IExprNumber(IExpr):
        pass

cdef extern from "zsp/ast/IExprAggregateLiteral.h" namespace "zsp::ast":
    cpdef cppclass IExprAggregateLiteral(IExpr):
        pass

cdef extern from "zsp/ast/IExprOpenRangeList.h" namespace "zsp::ast":
    cpdef cppclass IExprOpenRangeList(IExpr):
        std_vector[unique_ptr[IExprOpenRangeValue]] &getValues();

cdef extern from "zsp/ast/IExprOpenRangeValue.h" namespace "zsp::ast":
    cpdef cppclass IExprOpenRangeValue(IExpr):
        IExprgetLhs()
        
        void setLhs(IExprv)
        IExprgetRhs()
        
        void setRhs(IExprv)

cdef extern from "zsp/ast/IExprRefPath.h" namespace "zsp::ast":
    cpdef cppclass IExprRefPath(IExpr):
        ISymbolRefPathgetTarget()
        
        void setTarget(ISymbolRefPathv)

cdef extern from "zsp/ast/IExprRefPathContext.h" namespace "zsp::ast":
    cpdef cppclass IExprRefPathContext(IExpr):
        IExprHierarchicalIdgetHier_id()
        
        void setHier_id(IExprHierarchicalIdv)
        ISymbolRefPathgetTarget()
        
        void setTarget(ISymbolRefPathv)

cdef extern from "zsp/ast/IExprRefPathElem.h" namespace "zsp::ast":
    cpdef cppclass IExprRefPathElem(IExpr):
        pass

cdef extern from "zsp/ast/IExprRefPathStaticRooted.h" namespace "zsp::ast":
    cpdef cppclass IExprRefPathStaticRooted(IExpr):
        IExprRefPathStaticgetRoot()
        
        void setRoot(IExprRefPathStaticv)
        IExprRefPathContextgetLeaf()
        
        void setLeaf(IExprRefPathContextv)
        ISymbolRefPathgetTarget()
        
        void setTarget(ISymbolRefPathv)

cdef extern from "zsp/ast/IExprStaticRefPath.h" namespace "zsp::ast":
    cpdef cppclass IExprStaticRefPath(IExpr):
        bool getIs_global()
        
        void setIs_global(bool v)
        std_vector[unique_ptr[ITypeIdentifierElem]] &getBase();
        IExprMemberPathElemgetLeaf()
        
        void setLeaf(IExprMemberPathElemv)

cdef extern from "zsp/ast/IExprString.h" namespace "zsp::ast":
    cpdef cppclass IExprString(IExpr):
        const std_string &getValue()
        
        void set_value(const std_string &v)
        bool getIs_raw()
        
        void setIs_raw(bool v)

cdef extern from "zsp/ast/IExprSubscript.h" namespace "zsp::ast":
    cpdef cppclass IExprSubscript(IExpr):
        IExprgetExpr()
        
        void setExpr(IExprv)
        IExprgetSubscript()
        
        void setSubscript(IExprv)

cdef extern from "zsp/ast/IExprUnary.h" namespace "zsp::ast":
    cpdef cppclass IExprUnary(IExpr):
        ExprUnaryOp getOp()
        
        void setOp(ExprUnaryOp v)
        IExprgetRhs()
        
        void setRhs(IExprv)

cdef extern from "zsp/ast/IMethodParameterList.h" namespace "zsp::ast":
    cpdef cppclass IMethodParameterList(IExpr):
        pass

cdef extern from "zsp/ast/ITypeIdentifier.h" namespace "zsp::ast":
    cpdef cppclass ITypeIdentifier(IExpr):
        std_vector[unique_ptr[ITypeIdentifierElem]] &getElems();
        ISymbolRefPathgetTarget()
        
        void setTarget(ISymbolRefPathv)

cdef extern from "zsp/ast/ITypeIdentifierElem.h" namespace "zsp::ast":
    cpdef cppclass ITypeIdentifierElem(IExpr):
        IExprIdgetId()
        
        void setId(IExprIdv)
        std_vector[unique_ptr[ITemplateParamValue]] &getParams();

cdef extern from "zsp/ast/IExtendEnum.h" namespace "zsp::ast":
    cpdef cppclass IExtendEnum(IScopeChild):
        ITypeIdentifiergetTarget()
        
        void setTarget(ITypeIdentifierv)
        std_vector[unique_ptr[IEnumItem]] &getItems();

cdef extern from "zsp/ast/ISymbolScope.h" namespace "zsp::ast":
    cpdef cppclass ISymbolScope(IScopeChild):
        int32_t getId()
        
        void setId(int32_t v)
        const std_string &getName()
        
        void set_name(const std_string &v)
        ISymbolScopePgetUpper();
        
        void setUpper(ISymbolScopePv)
        std_vector[IScopeChildP] &getChildren();
        std_map[std_string,int32_t] &getSymtab();
        IScopePgetTarget();
        
        void setTarget(IScopePv)
        std_vector[unique_ptr[IScopeChild]] &getOwned();
        ISymbolImportSpecgetImports()
        
        void setImports(ISymbolImportSpecv)

cdef extern from "zsp/ast/IRefExprTypeScopeGlobal.h" namespace "zsp::ast":
    cpdef cppclass IRefExprTypeScopeGlobal(IRefExpr):
        int32_t getFileid()
        
        void setFileid(int32_t v)

cdef extern from "zsp/ast/IRefExprTypeScopeContext.h" namespace "zsp::ast":
    cpdef cppclass IRefExprTypeScopeContext(IRefExpr):
        IRefExprgetBase()
        
        void setBase(IRefExprv)
        int32_t getOffset()
        
        void setOffset(int32_t v)

cdef extern from "zsp/ast/IRefExprScopeIndex.h" namespace "zsp::ast":
    cpdef cppclass IRefExprScopeIndex(IRefExpr):
        IRefExprgetBase()
        
        void setBase(IRefExprv)
        int32_t getOffset()
        
        void setOffset(int32_t v)

cdef extern from "zsp/ast/ITemplateGenericTypeParamDecl.h" namespace "zsp::ast":
    cpdef cppclass ITemplateGenericTypeParamDecl(ITemplateParamDecl):
        ITypeIdentifiergetDflt()
        
        void setDflt(ITypeIdentifierv)

cdef extern from "zsp/ast/ITemplateCategoryTypeParamDecl.h" namespace "zsp::ast":
    cpdef cppclass ITemplateCategoryTypeParamDecl(ITemplateParamDecl):
        TypeCategory getCategory()
        
        void setCategory(TypeCategory v)
        ITypeIdentifiergetRestriction()
        
        void setRestriction(ITypeIdentifierv)
        ITypeIdentifiergetDflt()
        
        void setDflt(ITypeIdentifierv)

cdef extern from "zsp/ast/ITemplateValueParamDecl.h" namespace "zsp::ast":
    cpdef cppclass ITemplateValueParamDecl(ITemplateParamDecl):
        IExprgetDflt()
        
        void setDflt(IExprv)

cdef extern from "zsp/ast/IActivityBindStmt.h" namespace "zsp::ast":
    cpdef cppclass IActivityBindStmt(IActivityStmt):
        IExprHierarchicalIdgetLhs()
        
        void setLhs(IExprHierarchicalIdv)
        std_vector[unique_ptr[IExprHierarchicalId]] &getRhs();

cdef extern from "zsp/ast/IActivityConstraint.h" namespace "zsp::ast":
    cpdef cppclass IActivityConstraint(IActivityStmt):
        IConstraintStmtgetConstraint()
        
        void setConstraint(IConstraintStmtv)

cdef extern from "zsp/ast/IActivityLabeledStmt.h" namespace "zsp::ast":
    cpdef cppclass IActivityLabeledStmt(IActivityStmt):
        IExprIdgetLabel()
        
        void setLabel(IExprIdv)

cdef extern from "zsp/ast/IActivityLabeledScope.h" namespace "zsp::ast":
    cpdef cppclass IActivityLabeledScope(IScope):
        IExprIdgetLabel()
        
        void setLabel(IExprIdv)

cdef extern from "zsp/ast/IConstraintScope.h" namespace "zsp::ast":
    cpdef cppclass IConstraintScope(IConstraintStmt):
        std_vector[unique_ptr[IConstraintStmt]] &getConstraints();

cdef extern from "zsp/ast/IConstraintStmtExpr.h" namespace "zsp::ast":
    cpdef cppclass IConstraintStmtExpr(IConstraintStmt):
        IExprgetExpr()
        
        void setExpr(IExprv)

cdef extern from "zsp/ast/IConstraintStmtField.h" namespace "zsp::ast":
    cpdef cppclass IConstraintStmtField(IConstraintStmt):
        IExprIdgetName()
        
        void setName(IExprIdv)
        IDataTypegetType()
        
        void setType(IDataTypev)

cdef extern from "zsp/ast/IConstraintStmtIf.h" namespace "zsp::ast":
    cpdef cppclass IConstraintStmtIf(IConstraintStmt):
        IExprgetCond()
        
        void setCond(IExprv)
        IConstraintScopegetTrue_c()
        
        void setTrue_c(IConstraintScopev)
        IConstraintScopegetFalse_c()
        
        void setFalse_c(IConstraintScopev)

cdef extern from "zsp/ast/IConstraintStmtUnique.h" namespace "zsp::ast":
    cpdef cppclass IConstraintStmtUnique(IConstraintStmt):
        std_vector[unique_ptr[IExprHierarchicalId]] &getList();

cdef extern from "zsp/ast/IConstraintStmtDefault.h" namespace "zsp::ast":
    cpdef cppclass IConstraintStmtDefault(IConstraintStmt):
        IExprHierarchicalIdgetHid()
        
        void setHid(IExprHierarchicalIdv)
        IExprgetExpr()
        
        void setExpr(IExprv)

cdef extern from "zsp/ast/IConstraintStmtDefaultDisable.h" namespace "zsp::ast":
    cpdef cppclass IConstraintStmtDefaultDisable(IConstraintStmt):
        IExprHierarchicalIdgetHid()
        
        void setHid(IExprHierarchicalIdv)

cdef extern from "zsp/ast/IGlobalScope.h" namespace "zsp::ast":
    cpdef cppclass IGlobalScope(IScope):
        int32_t getFileid()
        
        void setFileid(int32_t v)

cdef extern from "zsp/ast/INamedScope.h" namespace "zsp::ast":
    cpdef cppclass INamedScope(IScope):
        IExprIdgetName()
        
        void setName(IExprIdv)

cdef extern from "zsp/ast/IPackageScope.h" namespace "zsp::ast":
    cpdef cppclass IPackageScope(IScope):
        std_vector[unique_ptr[IExprId]] &getId();
        IPackageScopePgetSibling();
        
        void setSibling(IPackageScopePv)

cdef extern from "zsp/ast/IDataTypeArray.h" namespace "zsp::ast":
    cpdef cppclass IDataTypeArray(IDataType):
        IDataTypegetType()
        
        void setType(IDataTypev)
        IExprgetSize()
        
        void setSize(IExprv)

cdef extern from "zsp/ast/IDataTypeBool.h" namespace "zsp::ast":
    cpdef cppclass IDataTypeBool(IDataType):
        pass

cdef extern from "zsp/ast/IDataTypeChandle.h" namespace "zsp::ast":
    cpdef cppclass IDataTypeChandle(IDataType):
        pass

cdef extern from "zsp/ast/IDataTypeEnum.h" namespace "zsp::ast":
    cpdef cppclass IDataTypeEnum(IDataType):
        IDataTypeUserDefinedgetTid()
        
        void setTid(IDataTypeUserDefinedv)
        IExprOpenRangeListgetIn_rangelist()
        
        void setIn_rangelist(IExprOpenRangeListv)

cdef extern from "zsp/ast/IEnumItem.h" namespace "zsp::ast":
    cpdef cppclass IEnumItem(INamedScopeChild):
        IExprgetValue()
        
        void setValue(IExprv)

cdef extern from "zsp/ast/IEnumDecl.h" namespace "zsp::ast":
    cpdef cppclass IEnumDecl(INamedScopeChild):
        std_vector[unique_ptr[IEnumItem]] &getItems();

cdef extern from "zsp/ast/IDataTypeInt.h" namespace "zsp::ast":
    cpdef cppclass IDataTypeInt(IDataType):
        bool getIs_signed()
        
        void setIs_signed(bool v)
        IExprgetWidth()
        
        void setWidth(IExprv)
        IExprDomainOpenRangeListgetIn_range()
        
        void setIn_range(IExprDomainOpenRangeListv)

cdef extern from "zsp/ast/IDataTypeRef.h" namespace "zsp::ast":
    cpdef cppclass IDataTypeRef(IDataType):
        IDataTypeUserDefinedgetType()
        
        void setType(IDataTypeUserDefinedv)

cdef extern from "zsp/ast/IDataTypeString.h" namespace "zsp::ast":
    cpdef cppclass IDataTypeString(IDataType):
        bool getHas_range()
        
        void setHas_range(bool v)
        std_vector[std_string] &getIn_range();

cdef extern from "zsp/ast/IDataTypeUserDefined.h" namespace "zsp::ast":
    cpdef cppclass IDataTypeUserDefined(IDataType):
        bool getIs_global()
        
        void setIs_global(bool v)
        ITypeIdentifiergetType_id()
        
        void setType_id(ITypeIdentifierv)

cdef extern from "zsp/ast/IExprRefPathStatic.h" namespace "zsp::ast":
    cpdef cppclass IExprRefPathStatic(IExprRefPath):
        bool getIs_global()
        
        void setIs_global(bool v)
        std_vector[unique_ptr[ITypeIdentifierElem]] &getBase();
        IExprBitSlicegetSlice()
        
        void setSlice(IExprBitSlicev)

cdef extern from "zsp/ast/IExprRefPathSuper.h" namespace "zsp::ast":
    cpdef cppclass IExprRefPathSuper(IExprRefPathContext):
        pass

cdef extern from "zsp/ast/IExprSignedNumber.h" namespace "zsp::ast":
    cpdef cppclass IExprSignedNumber(IExprNumber):
        const std_string &getImage()
        
        void set_image(const std_string &v)
        int32_t getWidth()
        
        void setWidth(int32_t v)
        int64_t getValue()
        
        void setValue(int64_t v)

cdef extern from "zsp/ast/IExprUnsignedNumber.h" namespace "zsp::ast":
    cpdef cppclass IExprUnsignedNumber(IExprNumber):
        const std_string &getImage()
        
        void set_image(const std_string &v)
        int32_t getWidth()
        
        void setWidth(int32_t v)
        uint64_t getValue()
        
        void setValue(uint64_t v)

cdef extern from "zsp/ast/IExtendType.h" namespace "zsp::ast":
    cpdef cppclass IExtendType(IScope):
        ExtendTargetE getKind()
        
        void setKind(ExtendTargetE v)
        ITypeIdentifiergetTarget()
        
        void setTarget(ITypeIdentifierv)

cdef extern from "zsp/ast/IField.h" namespace "zsp::ast":
    cpdef cppclass IField(INamedScopeChild):
        IDataTypegetType()
        
        void setType(IDataTypev)
        FieldAttr getAttr()
        
        void setAttr(FieldAttr v)
        IExprgetArray_dim()
        
        void setArray_dim(IExprv)
        IExprgetInit()
        
        void setInit(IExprv)

cdef extern from "zsp/ast/IFieldRef.h" namespace "zsp::ast":
    cpdef cppclass IFieldRef(INamedScopeChild):
        IDataTypeUserDefinedgetType()
        
        void setType(IDataTypeUserDefinedv)
        IExprgetArray_dim()
        
        void setArray_dim(IExprv)
        bool getIs_input()
        
        void setIs_input(bool v)

cdef extern from "zsp/ast/IFieldClaim.h" namespace "zsp::ast":
    cpdef cppclass IFieldClaim(INamedScopeChild):
        IDataTypeUserDefinedgetType()
        
        void setType(IDataTypeUserDefinedv)
        IExprgetArray_dim()
        
        void setArray_dim(IExprv)
        bool getIs_lock()
        
        void setIs_lock(bool v)

cdef extern from "zsp/ast/ISymbolTypeScope.h" namespace "zsp::ast":
    cpdef cppclass ISymbolTypeScope(ISymbolScope):
        ISymbolScopegetPlist()
        
        void setPlist(ISymbolScopev)

cdef extern from "zsp/ast/ISymbolFunctionScope.h" namespace "zsp::ast":
    cpdef cppclass ISymbolFunctionScope(ISymbolScope):
        ISymbolScopegetPlist()
        
        void setPlist(ISymbolScopev)

cdef extern from "zsp/ast/IActivityActionHandleTraversal.h" namespace "zsp::ast":
    cpdef cppclass IActivityActionHandleTraversal(IActivityLabeledStmt):
        IExprRefPathContextgetTarget()
        
        void setTarget(IExprRefPathContextv)
        IConstraintStmtgetWith_c()
        
        void setWith_c(IConstraintStmtv)

cdef extern from "zsp/ast/IActivityActionTypeTraversal.h" namespace "zsp::ast":
    cpdef cppclass IActivityActionTypeTraversal(IActivityLabeledStmt):
        IDataTypeUserDefinedgetTarget()
        
        void setTarget(IDataTypeUserDefinedv)
        IConstraintStmtgetWith_c()
        
        void setWith_c(IConstraintStmtv)

cdef extern from "zsp/ast/IActivitySequence.h" namespace "zsp::ast":
    cpdef cppclass IActivitySequence(IActivityLabeledScope):
        pass

cdef extern from "zsp/ast/IActivityParallel.h" namespace "zsp::ast":
    cpdef cppclass IActivityParallel(IActivityLabeledScope):
        IActivityJoinSpecgetJoin_spec()
        
        void setJoin_spec(IActivityJoinSpecv)

cdef extern from "zsp/ast/IActivitySchedule.h" namespace "zsp::ast":
    cpdef cppclass IActivitySchedule(IActivityLabeledScope):
        IActivityJoinSpecgetJoin_spec()
        
        void setJoin_spec(IActivityJoinSpecv)

cdef extern from "zsp/ast/IActivityRepeatCount.h" namespace "zsp::ast":
    cpdef cppclass IActivityRepeatCount(IActivityLabeledStmt):
        IExprIdgetLoop_var()
        
        void setLoop_var(IExprIdv)
        IExprgetCount()
        
        void setCount(IExprv)
        IScopeChildgetBody()
        
        void setBody(IScopeChildv)

cdef extern from "zsp/ast/IActivityRepeatWhile.h" namespace "zsp::ast":
    cpdef cppclass IActivityRepeatWhile(IActivityLabeledStmt):
        IExprgetCond()
        
        void setCond(IExprv)
        IScopeChildgetBody()
        
        void setBody(IScopeChildv)

cdef extern from "zsp/ast/IActivityForeach.h" namespace "zsp::ast":
    cpdef cppclass IActivityForeach(IActivityLabeledStmt):
        IExprIdgetIt_id()
        
        void setIt_id(IExprIdv)
        IExprIdgetIdx_id()
        
        void setIdx_id(IExprIdv)
        IExprRefPathContextgetTarget()
        
        void setTarget(IExprRefPathContextv)
        IScopeChildgetBody()
        
        void setBody(IScopeChildv)

cdef extern from "zsp/ast/IActivitySelect.h" namespace "zsp::ast":
    cpdef cppclass IActivitySelect(IActivityLabeledStmt):
        std_vector[unique_ptr[IActivitySelectBranch]] &getBranches();

cdef extern from "zsp/ast/IActivityIfElse.h" namespace "zsp::ast":
    cpdef cppclass IActivityIfElse(IActivityLabeledStmt):
        IExprgetCond()
        
        void setCond(IExprv)
        IActivityStmtgetTrue_s()
        
        void setTrue_s(IActivityStmtv)
        IActivityStmtgetFalse_s()
        
        void setFalse_s(IActivityStmtv)

cdef extern from "zsp/ast/IActivityMatch.h" namespace "zsp::ast":
    cpdef cppclass IActivityMatch(IActivityLabeledStmt):
        IExprgetCond()
        
        void setCond(IExprv)
        std_vector[unique_ptr[IActivityMatchChoice]] &getChoices();

cdef extern from "zsp/ast/IActivityReplicate.h" namespace "zsp::ast":
    cpdef cppclass IActivityReplicate(IActivityLabeledStmt):
        IExprIdgetIdx_id()
        
        void setIdx_id(IExprIdv)
        IExprIdgetIt_label()
        
        void setIt_label(IExprIdv)
        IScopeChildgetBody()
        
        void setBody(IScopeChildv)

cdef extern from "zsp/ast/IActivitySuper.h" namespace "zsp::ast":
    cpdef cppclass IActivitySuper(IActivityLabeledStmt):
        pass

cdef extern from "zsp/ast/IConstraintBlock.h" namespace "zsp::ast":
    cpdef cppclass IConstraintBlock(IConstraintScope):
        const std_string &getName()
        
        void set_name(const std_string &v)
        bool getIs_dynamic()
        
        void setIs_dynamic(bool v)

cdef extern from "zsp/ast/IConstraintStmtForeach.h" namespace "zsp::ast":
    cpdef cppclass IConstraintStmtForeach(IConstraintScope):
        IConstraintStmtFieldPgetIt();
        
        void setIt(IConstraintStmtFieldPv)
        IConstraintStmtFieldPgetIdx();
        
        void setIdx(IConstraintStmtFieldPv)
        IExprgetExpr()
        
        void setExpr(IExprv)

cdef extern from "zsp/ast/IConstraintStmtForall.h" namespace "zsp::ast":
    cpdef cppclass IConstraintStmtForall(IConstraintScope):
        IExprIdgetIterator_id()
        
        void setIterator_id(IExprIdv)
        IDataTypeUserDefinedgetType_id()
        
        void setType_id(IDataTypeUserDefinedv)
        IExprRefPathgetRef_path()
        
        void setRef_path(IExprRefPathv)

cdef extern from "zsp/ast/IConstraintStmtImplication.h" namespace "zsp::ast":
    cpdef cppclass IConstraintStmtImplication(IConstraintScope):
        IExprgetCond()
        
        void setCond(IExprv)

cdef extern from "zsp/ast/IExprRefPathStaticFunc.h" namespace "zsp::ast":
    cpdef cppclass IExprRefPathStaticFunc(IExprRefPathStatic):
        IMethodParameterListgetParams()
        
        void setParams(IMethodParameterListv)

cdef extern from "zsp/ast/ITypeScope.h" namespace "zsp::ast":
    cpdef cppclass ITypeScope(INamedScope):
        ITypeIdentifiergetSuper_t()
        
        void setSuper_t(ITypeIdentifierv)
        ITemplateParamDeclListgetParams()
        
        void setParams(ITemplateParamDeclListv)

cdef extern from "zsp/ast/IStruct.h" namespace "zsp::ast":
    cpdef cppclass IStruct(ITypeScope):
        StructKind getKind()
        
        void setKind(StructKind v)

cdef extern from "zsp/ast/IAction.h" namespace "zsp::ast":
    cpdef cppclass IAction(ITypeScope):
        bool getIs_abstract()
        
        void setIs_abstract(bool v)

cdef extern from "zsp/ast/IComponent.h" namespace "zsp::ast":
    cpdef cppclass IComponent(ITypeScope):
        pass

cdef extern from 'zsp/ast/impl/VisitorBase.h' namespace 'zsp::ast':
    cpdef cppclass VisitorBase:
        void visitSymbolImportSpec(ISymbolImportSpecP i)
        void visitScopeChild(IScopeChildP i)
        void visitActivityJoinSpec(IActivityJoinSpecP i)
        void visitSymbolRefPath(ISymbolRefPathP i)
        void visitRefExpr(IRefExprP i)
        void visitTemplateParamDeclList(ITemplateParamDeclListP i)
        void visitTemplateParamDecl(ITemplateParamDeclP i)
        void visitActivitySelectBranch(IActivitySelectBranchP i)
        void visitTemplateParamValueList(ITemplateParamValueListP i)
        void visitTemplateParamValue(ITemplateParamValueP i)
        void visitActivityMatchChoice(IActivityMatchChoiceP i)
        void visitTemplateParamTypeValue(ITemplateParamTypeValueP i)
        void visitTemplateParamExprValue(ITemplateParamExprValueP i)
        void visitExecStmt(IExecStmtP i)
        void visitExpr(IExprP i)
        void visitActivityStmt(IActivityStmtP i)
        void visitActivitySchedulingConstraint(IActivitySchedulingConstraintP i)
        void visitActivityJoinSpecBranch(IActivityJoinSpecBranchP i)
        void visitActivityJoinSpecSelect(IActivityJoinSpecSelectP i)
        void visitActivityJoinSpecNone(IActivityJoinSpecNoneP i)
        void visitActivityJoinSpecFirst(IActivityJoinSpecFirstP i)
        void visitConstraintStmt(IConstraintStmtP i)
        void visitScope(IScopeP i)
        void visitScopeChildRef(IScopeChildRefP i)
        void visitNamedScopeChild(INamedScopeChildP i)
        void visitPackageImportStmt(IPackageImportStmtP i)
        void visitDataType(IDataTypeP i)
        void visitExecScope(IExecScopeP i)
        void visitProceduralStmtDataDeclaration(IProceduralStmtDataDeclarationP i)
        void visitExprBin(IExprBinP i)
        void visitExprBitSlice(IExprBitSliceP i)
        void visitExprBool(IExprBoolP i)
        void visitExprCast(IExprCastP i)
        void visitExprCompileHas(IExprCompileHasP i)
        void visitExprCond(IExprCondP i)
        void visitExprDomainOpenRangeList(IExprDomainOpenRangeListP i)
        void visitExprDomainOpenRangeValue(IExprDomainOpenRangeValueP i)
        void visitExprHierarchicalId(IExprHierarchicalIdP i)
        void visitExprId(IExprIdP i)
        void visitExprIn(IExprInP i)
        void visitExprMemberPathElem(IExprMemberPathElemP i)
        void visitExprNull(IExprNullP i)
        void visitExprNumber(IExprNumberP i)
        void visitExprAggregateLiteral(IExprAggregateLiteralP i)
        void visitExprOpenRangeList(IExprOpenRangeListP i)
        void visitExprOpenRangeValue(IExprOpenRangeValueP i)
        void visitExprRefPath(IExprRefPathP i)
        void visitExprRefPathContext(IExprRefPathContextP i)
        void visitExprRefPathElem(IExprRefPathElemP i)
        void visitExprRefPathStaticRooted(IExprRefPathStaticRootedP i)
        void visitExprStaticRefPath(IExprStaticRefPathP i)
        void visitExprString(IExprStringP i)
        void visitExprSubscript(IExprSubscriptP i)
        void visitExprUnary(IExprUnaryP i)
        void visitMethodParameterList(IMethodParameterListP i)
        void visitTypeIdentifier(ITypeIdentifierP i)
        void visitTypeIdentifierElem(ITypeIdentifierElemP i)
        void visitExtendEnum(IExtendEnumP i)
        void visitSymbolScope(ISymbolScopeP i)
        void visitRefExprTypeScopeGlobal(IRefExprTypeScopeGlobalP i)
        void visitRefExprTypeScopeContext(IRefExprTypeScopeContextP i)
        void visitRefExprScopeIndex(IRefExprScopeIndexP i)
        void visitTemplateGenericTypeParamDecl(ITemplateGenericTypeParamDeclP i)
        void visitTemplateCategoryTypeParamDecl(ITemplateCategoryTypeParamDeclP i)
        void visitTemplateValueParamDecl(ITemplateValueParamDeclP i)
        void visitActivityBindStmt(IActivityBindStmtP i)
        void visitActivityConstraint(IActivityConstraintP i)
        void visitActivityLabeledStmt(IActivityLabeledStmtP i)
        void visitActivityLabeledScope(IActivityLabeledScopeP i)
        void visitConstraintScope(IConstraintScopeP i)
        void visitConstraintStmtExpr(IConstraintStmtExprP i)
        void visitConstraintStmtField(IConstraintStmtFieldP i)
        void visitConstraintStmtIf(IConstraintStmtIfP i)
        void visitConstraintStmtUnique(IConstraintStmtUniqueP i)
        void visitConstraintStmtDefault(IConstraintStmtDefaultP i)
        void visitConstraintStmtDefaultDisable(IConstraintStmtDefaultDisableP i)
        void visitGlobalScope(IGlobalScopeP i)
        void visitNamedScope(INamedScopeP i)
        void visitPackageScope(IPackageScopeP i)
        void visitDataTypeArray(IDataTypeArrayP i)
        void visitDataTypeBool(IDataTypeBoolP i)
        void visitDataTypeChandle(IDataTypeChandleP i)
        void visitDataTypeEnum(IDataTypeEnumP i)
        void visitEnumItem(IEnumItemP i)
        void visitEnumDecl(IEnumDeclP i)
        void visitDataTypeInt(IDataTypeIntP i)
        void visitDataTypeRef(IDataTypeRefP i)
        void visitDataTypeString(IDataTypeStringP i)
        void visitDataTypeUserDefined(IDataTypeUserDefinedP i)
        void visitExprRefPathStatic(IExprRefPathStaticP i)
        void visitExprRefPathSuper(IExprRefPathSuperP i)
        void visitExprSignedNumber(IExprSignedNumberP i)
        void visitExprUnsignedNumber(IExprUnsignedNumberP i)
        void visitExtendType(IExtendTypeP i)
        void visitField(IFieldP i)
        void visitFieldRef(IFieldRefP i)
        void visitFieldClaim(IFieldClaimP i)
        void visitSymbolTypeScope(ISymbolTypeScopeP i)
        void visitSymbolFunctionScope(ISymbolFunctionScopeP i)
        void visitActivityActionHandleTraversal(IActivityActionHandleTraversalP i)
        void visitActivityActionTypeTraversal(IActivityActionTypeTraversalP i)
        void visitActivitySequence(IActivitySequenceP i)
        void visitActivityParallel(IActivityParallelP i)
        void visitActivitySchedule(IActivityScheduleP i)
        void visitActivityRepeatCount(IActivityRepeatCountP i)
        void visitActivityRepeatWhile(IActivityRepeatWhileP i)
        void visitActivityForeach(IActivityForeachP i)
        void visitActivitySelect(IActivitySelectP i)
        void visitActivityIfElse(IActivityIfElseP i)
        void visitActivityMatch(IActivityMatchP i)
        void visitActivityReplicate(IActivityReplicateP i)
        void visitActivitySuper(IActivitySuperP i)
        void visitConstraintBlock(IConstraintBlockP i)
        void visitConstraintStmtForeach(IConstraintStmtForeachP i)
        void visitConstraintStmtForall(IConstraintStmtForallP i)
        void visitConstraintStmtImplication(IConstraintStmtImplicationP i)
        void visitExprRefPathStaticFunc(IExprRefPathStaticFuncP i)
        void visitTypeScope(ITypeScopeP i)
        void visitStruct(IStructP i)
        void visitAction(IActionP i)
        void visitComponent(IComponentP i)
cdef extern from 'PyBaseVisitor.h' namespace 'zsp::ast':
    cpdef cppclass PyBaseVisitor(VisitorBase):
        PyBaseVisitor(cpy_ref.PyObject *)
        void py_visitSymbolImportSpec(ISymbolImportSpec *i)
        void py_visitScopeChild(IScopeChild *i)
        void py_visitActivityJoinSpec(IActivityJoinSpec *i)
        void py_visitSymbolRefPath(ISymbolRefPath *i)
        void py_visitRefExpr(IRefExpr *i)
        void py_visitTemplateParamDeclList(ITemplateParamDeclList *i)
        void py_visitTemplateParamDecl(ITemplateParamDecl *i)
        void py_visitActivitySelectBranch(IActivitySelectBranch *i)
        void py_visitTemplateParamValueList(ITemplateParamValueList *i)
        void py_visitTemplateParamValue(ITemplateParamValue *i)
        void py_visitActivityMatchChoice(IActivityMatchChoice *i)
        void py_visitTemplateParamTypeValue(ITemplateParamTypeValue *i)
        void py_visitTemplateParamExprValue(ITemplateParamExprValue *i)
        void py_visitExecStmt(IExecStmt *i)
        void py_visitExpr(IExpr *i)
        void py_visitActivityStmt(IActivityStmt *i)
        void py_visitActivitySchedulingConstraint(IActivitySchedulingConstraint *i)
        void py_visitActivityJoinSpecBranch(IActivityJoinSpecBranch *i)
        void py_visitActivityJoinSpecSelect(IActivityJoinSpecSelect *i)
        void py_visitActivityJoinSpecNone(IActivityJoinSpecNone *i)
        void py_visitActivityJoinSpecFirst(IActivityJoinSpecFirst *i)
        void py_visitConstraintStmt(IConstraintStmt *i)
        void py_visitScope(IScope *i)
        void py_visitScopeChildRef(IScopeChildRef *i)
        void py_visitNamedScopeChild(INamedScopeChild *i)
        void py_visitPackageImportStmt(IPackageImportStmt *i)
        void py_visitDataType(IDataType *i)
        void py_visitExecScope(IExecScope *i)
        void py_visitProceduralStmtDataDeclaration(IProceduralStmtDataDeclaration *i)
        void py_visitExprBin(IExprBin *i)
        void py_visitExprBitSlice(IExprBitSlice *i)
        void py_visitExprBool(IExprBool *i)
        void py_visitExprCast(IExprCast *i)
        void py_visitExprCompileHas(IExprCompileHas *i)
        void py_visitExprCond(IExprCond *i)
        void py_visitExprDomainOpenRangeList(IExprDomainOpenRangeList *i)
        void py_visitExprDomainOpenRangeValue(IExprDomainOpenRangeValue *i)
        void py_visitExprHierarchicalId(IExprHierarchicalId *i)
        void py_visitExprId(IExprId *i)
        void py_visitExprIn(IExprIn *i)
        void py_visitExprMemberPathElem(IExprMemberPathElem *i)
        void py_visitExprNull(IExprNull *i)
        void py_visitExprNumber(IExprNumber *i)
        void py_visitExprAggregateLiteral(IExprAggregateLiteral *i)
        void py_visitExprOpenRangeList(IExprOpenRangeList *i)
        void py_visitExprOpenRangeValue(IExprOpenRangeValue *i)
        void py_visitExprRefPath(IExprRefPath *i)
        void py_visitExprRefPathContext(IExprRefPathContext *i)
        void py_visitExprRefPathElem(IExprRefPathElem *i)
        void py_visitExprRefPathStaticRooted(IExprRefPathStaticRooted *i)
        void py_visitExprStaticRefPath(IExprStaticRefPath *i)
        void py_visitExprString(IExprString *i)
        void py_visitExprSubscript(IExprSubscript *i)
        void py_visitExprUnary(IExprUnary *i)
        void py_visitMethodParameterList(IMethodParameterList *i)
        void py_visitTypeIdentifier(ITypeIdentifier *i)
        void py_visitTypeIdentifierElem(ITypeIdentifierElem *i)
        void py_visitExtendEnum(IExtendEnum *i)
        void py_visitSymbolScope(ISymbolScope *i)
        void py_visitRefExprTypeScopeGlobal(IRefExprTypeScopeGlobal *i)
        void py_visitRefExprTypeScopeContext(IRefExprTypeScopeContext *i)
        void py_visitRefExprScopeIndex(IRefExprScopeIndex *i)
        void py_visitTemplateGenericTypeParamDecl(ITemplateGenericTypeParamDecl *i)
        void py_visitTemplateCategoryTypeParamDecl(ITemplateCategoryTypeParamDecl *i)
        void py_visitTemplateValueParamDecl(ITemplateValueParamDecl *i)
        void py_visitActivityBindStmt(IActivityBindStmt *i)
        void py_visitActivityConstraint(IActivityConstraint *i)
        void py_visitActivityLabeledStmt(IActivityLabeledStmt *i)
        void py_visitActivityLabeledScope(IActivityLabeledScope *i)
        void py_visitConstraintScope(IConstraintScope *i)
        void py_visitConstraintStmtExpr(IConstraintStmtExpr *i)
        void py_visitConstraintStmtField(IConstraintStmtField *i)
        void py_visitConstraintStmtIf(IConstraintStmtIf *i)
        void py_visitConstraintStmtUnique(IConstraintStmtUnique *i)
        void py_visitConstraintStmtDefault(IConstraintStmtDefault *i)
        void py_visitConstraintStmtDefaultDisable(IConstraintStmtDefaultDisable *i)
        void py_visitGlobalScope(IGlobalScope *i)
        void py_visitNamedScope(INamedScope *i)
        void py_visitPackageScope(IPackageScope *i)
        void py_visitDataTypeArray(IDataTypeArray *i)
        void py_visitDataTypeBool(IDataTypeBool *i)
        void py_visitDataTypeChandle(IDataTypeChandle *i)
        void py_visitDataTypeEnum(IDataTypeEnum *i)
        void py_visitEnumItem(IEnumItem *i)
        void py_visitEnumDecl(IEnumDecl *i)
        void py_visitDataTypeInt(IDataTypeInt *i)
        void py_visitDataTypeRef(IDataTypeRef *i)
        void py_visitDataTypeString(IDataTypeString *i)
        void py_visitDataTypeUserDefined(IDataTypeUserDefined *i)
        void py_visitExprRefPathStatic(IExprRefPathStatic *i)
        void py_visitExprRefPathSuper(IExprRefPathSuper *i)
        void py_visitExprSignedNumber(IExprSignedNumber *i)
        void py_visitExprUnsignedNumber(IExprUnsignedNumber *i)
        void py_visitExtendType(IExtendType *i)
        void py_visitField(IField *i)
        void py_visitFieldRef(IFieldRef *i)
        void py_visitFieldClaim(IFieldClaim *i)
        void py_visitSymbolTypeScope(ISymbolTypeScope *i)
        void py_visitSymbolFunctionScope(ISymbolFunctionScope *i)
        void py_visitActivityActionHandleTraversal(IActivityActionHandleTraversal *i)
        void py_visitActivityActionTypeTraversal(IActivityActionTypeTraversal *i)
        void py_visitActivitySequence(IActivitySequence *i)
        void py_visitActivityParallel(IActivityParallel *i)
        void py_visitActivitySchedule(IActivitySchedule *i)
        void py_visitActivityRepeatCount(IActivityRepeatCount *i)
        void py_visitActivityRepeatWhile(IActivityRepeatWhile *i)
        void py_visitActivityForeach(IActivityForeach *i)
        void py_visitActivitySelect(IActivitySelect *i)
        void py_visitActivityIfElse(IActivityIfElse *i)
        void py_visitActivityMatch(IActivityMatch *i)
        void py_visitActivityReplicate(IActivityReplicate *i)
        void py_visitActivitySuper(IActivitySuper *i)
        void py_visitConstraintBlock(IConstraintBlock *i)
        void py_visitConstraintStmtForeach(IConstraintStmtForeach *i)
        void py_visitConstraintStmtForall(IConstraintStmtForall *i)
        void py_visitConstraintStmtImplication(IConstraintStmtImplication *i)
        void py_visitExprRefPathStaticFunc(IExprRefPathStaticFunc *i)
        void py_visitTypeScope(ITypeScope *i)
        void py_visitStruct(IStruct *i)
        void py_visitAction(IAction *i)
        void py_visitComponent(IComponent *i)
