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

ctypedef IExecStmt *IExecStmtP
ctypedef IExpr *IExprP
ctypedef IRefExpr *IRefExprP
ctypedef ITemplateParamDeclList *ITemplateParamDeclListP
ctypedef ITemplateParamDecl *ITemplateParamDeclP
ctypedef IScopeChild *IScopeChildP
ctypedef ITemplateParamValueList *ITemplateParamValueListP
ctypedef ITemplateParamValue *ITemplateParamValueP
ctypedef ITemplateParamTypeValue *ITemplateParamTypeValueP
ctypedef ITemplateParamExprValue *ITemplateParamExprValueP
ctypedef IConstraintStmt *IConstraintStmtP
ctypedef IScope *IScopeP
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
ctypedef IExprNumber *IExprNumberP
ctypedef IExprAggregateLiteral *IExprAggregateLiteralP
ctypedef IExprOpenRangeList *IExprOpenRangeListP
ctypedef IExprOpenRangeValue *IExprOpenRangeValueP
ctypedef IExprRefPath *IExprRefPathP
ctypedef IExprRefPathElem *IExprRefPathElemP
ctypedef IExprRefPathStaticRooted *IExprRefPathStaticRootedP
ctypedef IExprStaticRefPath *IExprStaticRefPathP
ctypedef IExprString *IExprStringP
ctypedef IExprSubscript *IExprSubscriptP
ctypedef IExprUnary *IExprUnaryP
ctypedef IMethodParameterList *IMethodParameterListP
ctypedef ITypeIdentifier *ITypeIdentifierP
ctypedef ITypeIdentifierElem *ITypeIdentifierElemP
ctypedef IRefExprTypeScopeGlobal *IRefExprTypeScopeGlobalP
ctypedef IRefExprTypeScopeContext *IRefExprTypeScopeContextP
ctypedef IRefExprScopeIndex *IRefExprScopeIndexP
ctypedef ITemplateGenericTypeParamDecl *ITemplateGenericTypeParamDeclP
ctypedef ITemplateCategoryTypeParamDecl *ITemplateCategoryTypeParamDeclP
ctypedef ITemplateValueParamDecl *ITemplateValueParamDeclP
ctypedef IConstraintBlock *IConstraintBlockP
ctypedef IConstraintScope *IConstraintScopeP
ctypedef IConstraintStmtDefault *IConstraintStmtDefaultP
ctypedef IConstraintStmtDefaultDisable *IConstraintStmtDefaultDisableP
ctypedef IConstraintStmtExpr *IConstraintStmtExprP
ctypedef IConstraintStmtField *IConstraintStmtFieldP
ctypedef IConstraintStmtIf *IConstraintStmtIfP
ctypedef IConstraintStmtUnique *IConstraintStmtUniqueP
ctypedef IGlobalScope *IGlobalScopeP
ctypedef INamedScope *INamedScopeP
ctypedef IPackageScope *IPackageScopeP
ctypedef IDataTypeArray *IDataTypeArrayP
ctypedef IDataTypeBool *IDataTypeBoolP
ctypedef IDataTypeChandle *IDataTypeChandleP
ctypedef IDataTypeEnum *IDataTypeEnumP
ctypedef IDataTypeInt *IDataTypeIntP
ctypedef IDataTypeString *IDataTypeStringP
ctypedef IDataTypeUserDefined *IDataTypeUserDefinedP
ctypedef IExprRefPathContext *IExprRefPathContextP
ctypedef IExprRefPathStatic *IExprRefPathStaticP
ctypedef IExprSignedNumber *IExprSignedNumberP
ctypedef IExprUnsignedNumber *IExprUnsignedNumberP
ctypedef IConstraintStmtForall *IConstraintStmtForallP
ctypedef IConstraintStmtForeach *IConstraintStmtForeachP
ctypedef IConstraintStmtImplication *IConstraintStmtImplicationP
ctypedef ITypeScope *ITypeScopeP
ctypedef IExprRefPathStaticFunc *IExprRefPathStaticFuncP
ctypedef IExprRefPathSuper *IExprRefPathSuperP
ctypedef IAction *IActionP
ctypedef IComponent *IComponentP
ctypedef IStruct *IStructP
ctypedef IState *IStateP
ctypedef IStream *IStreamP
ctypedef IBuffer *IBufferP
ctypedef IResource *IResourceP
cdef extern from "pssp/ast/ExprBinOp.h" namespace "pssp::ast":
    cdef enum ExprBinOp:
        BinOp_LogOr "pssp::ast::ExprBinOp::BinOp_LogOr"
        BinOp_LogAnd "pssp::ast::ExprBinOp::BinOp_LogAnd"
        BinOp_BitOr "pssp::ast::ExprBinOp::BinOp_BitOr"
        BinOp_BitXor "pssp::ast::ExprBinOp::BinOp_BitXor"
        BinOp_BitAnd "pssp::ast::ExprBinOp::BinOp_BitAnd"
        BinOp_Lt "pssp::ast::ExprBinOp::BinOp_Lt"
        BinOp_Le "pssp::ast::ExprBinOp::BinOp_Le"
        BinOp_Gt "pssp::ast::ExprBinOp::BinOp_Gt"
        BinOp_Ge "pssp::ast::ExprBinOp::BinOp_Ge"
        BinOp_Exp "pssp::ast::ExprBinOp::BinOp_Exp"
        BinOp_Mul "pssp::ast::ExprBinOp::BinOp_Mul"
        BinOp_Div "pssp::ast::ExprBinOp::BinOp_Div"
        BinOp_Mod "pssp::ast::ExprBinOp::BinOp_Mod"
        BinOp_Add "pssp::ast::ExprBinOp::BinOp_Add"
        BinOp_Sub "pssp::ast::ExprBinOp::BinOp_Sub"
        BinOp_Shl "pssp::ast::ExprBinOp::BinOp_Shl"
        BinOp_Shr "pssp::ast::ExprBinOp::BinOp_Shr"
        BinOp_Eq "pssp::ast::ExprBinOp::BinOp_Eq"
        BinOp_Ne "pssp::ast::ExprBinOp::BinOp_Ne"
cdef extern from "pssp/ast/ExprUnaryOp.h" namespace "pssp::ast":
    cdef enum ExprUnaryOp:
        UnaryOp_Plus "pssp::ast::ExprUnaryOp::UnaryOp_Plus"
        UnaryOp_Minus "pssp::ast::ExprUnaryOp::UnaryOp_Minus"
        UnaryOp_LogNot "pssp::ast::ExprUnaryOp::UnaryOp_LogNot"
        UnaryOp_BitNeg "pssp::ast::ExprUnaryOp::UnaryOp_BitNeg"
        UnaryOp_BitAnd "pssp::ast::ExprUnaryOp::UnaryOp_BitAnd"
        UnaryOp_BitOr "pssp::ast::ExprUnaryOp::UnaryOp_BitOr"
        UnaryOp_BitXor "pssp::ast::ExprUnaryOp::UnaryOp_BitXor"
cdef extern from "pssp/ast/TypeCategory.h" namespace "pssp::ast":
    cdef enum TypeCategory:
        Action "pssp::ast::TypeCategory::Action"
        Component "pssp::ast::TypeCategory::Component"
        Buffer "pssp::ast::TypeCategory::Buffer"
        Resource "pssp::ast::TypeCategory::Resource"
        State "pssp::ast::TypeCategory::State"
        Stream "pssp::ast::TypeCategory::Stream"
cdef extern from "pssp/ast/IFactory.h" namespace "pssp::ast":
    cdef cppclass IFactory:
        IExecStmt *mkExecStmt(
                )
        IExpr *mkExpr(
                )
        IRefExpr *mkRefExpr(
                )
        ITemplateParamDeclList *mkTemplateParamDeclList(
                )
        ITemplateParamDecl *mkTemplateParamDecl(
                IExprId* name)
        IScopeChild *mkScopeChild(
                )
        ITemplateParamValueList *mkTemplateParamValueList(
                )
        ITemplateParamValue *mkTemplateParamValue(
                )
        ITemplateParamTypeValue *mkTemplateParamTypeValue(
                ITypeIdentifier* value)
        ITemplateParamExprValue *mkTemplateParamExprValue(
                IExpr* value)
        IConstraintStmt *mkConstraintStmt(
                )
        IScope *mkScope(
                )
        INamedScopeChild *mkNamedScopeChild(
                IExprId* name)
        IPackageImportStmt *mkPackageImportStmt(
                bool wildcard,
                IExprId* alias)
        IDataType *mkDataType(
                )
        IExecScope *mkExecScope(
                )
        IProceduralStmtDataDeclaration *mkProceduralStmtDataDeclaration(
                IDataType* datatype,
                IExprId* name)
        IExprBin *mkExprBin(
                IExpr* lhs,
                ExprBinOp op,
                IExpr* rhs)
        IExprBitSlice *mkExprBitSlice(
                IExpr* expr,
                IExpr* lhs,
                IExpr* rhs)
        IExprBool *mkExprBool(
                bool value)
        IExprCast *mkExprCast(
                IExpr* casting_type,
                IExpr* expr)
        IExprCompileHas *mkExprCompileHas(
                IExprRefPathStatic* ref)
        IExprCond *mkExprCond(
                IExpr* cond_e,
                IExpr* true_e,
                IExpr* false_e)
        IExprDomainOpenRangeList *mkExprDomainOpenRangeList(
                )
        IExprDomainOpenRangeValue *mkExprDomainOpenRangeValue(
                bool single,
                IExpr* lhs,
                IExpr* rhs)
        IExprHierarchicalId *mkExprHierarchicalId(
                )
        IExprId *mkExprId(
                std_string id,
                bool is_escaped)
        IExprIn *mkExprIn(
                IExpr* lhs,
                IExprOpenRangeList* rhs)
        IExprMemberPathElem *mkExprMemberPathElem(
                IExprId* id,
                IMethodParameterList* params,
                IExpr* subscript)
        IExprNumber *mkExprNumber(
                )
        IExprAggregateLiteral *mkExprAggregateLiteral(
                )
        IExprOpenRangeList *mkExprOpenRangeList(
                )
        IExprOpenRangeValue *mkExprOpenRangeValue(
                IExpr* lhs,
                IExpr* rhs)
        IExprRefPath *mkExprRefPath(
                )
        IExprRefPathElem *mkExprRefPathElem(
                )
        IExprRefPathStaticRooted *mkExprRefPathStaticRooted(
                IExprRefPathStatic* root,
                IExprRefPathContext* leaf)
        IExprStaticRefPath *mkExprStaticRefPath(
                bool is_global,
                IExprMemberPathElem* leaf)
        IExprString *mkExprString(
                std_string value,
                bool is_raw)
        IExprSubscript *mkExprSubscript(
                IExpr* expr,
                IExpr* subscript)
        IExprUnary *mkExprUnary(
                ExprUnaryOp op,
                IExpr* rhs)
        IMethodParameterList *mkMethodParameterList(
                )
        ITypeIdentifier *mkTypeIdentifier(
                )
        ITypeIdentifierElem *mkTypeIdentifierElem(
                IExprId* id)
        IRefExprTypeScopeGlobal *mkRefExprTypeScopeGlobal(
                int32_t fileid)
        IRefExprTypeScopeContext *mkRefExprTypeScopeContext(
                IRefExpr* base,
                int32_t offset)
        IRefExprScopeIndex *mkRefExprScopeIndex(
                IRefExpr* base,
                int32_t offset)
        ITemplateGenericTypeParamDecl *mkTemplateGenericTypeParamDecl(
                IExprId* name,
                ITypeIdentifier* dflt)
        ITemplateCategoryTypeParamDecl *mkTemplateCategoryTypeParamDecl(
                IExprId* name,
                TypeCategory category,
                ITypeIdentifier* restriction,
                ITypeIdentifier* dflt)
        ITemplateValueParamDecl *mkTemplateValueParamDecl(
                IExprId* name,
                IExpr* dflt)
        IConstraintBlock *mkConstraintBlock(
                std_string name,
                bool is_dynamic)
        IConstraintScope *mkConstraintScope(
                )
        IConstraintStmtDefault *mkConstraintStmtDefault(
                IExprHierarchicalId* hid,
                IExpr* expr)
        IConstraintStmtDefaultDisable *mkConstraintStmtDefaultDisable(
                IExprHierarchicalId* hid)
        IConstraintStmtExpr *mkConstraintStmtExpr(
                IExpr* expr)
        IConstraintStmtField *mkConstraintStmtField(
                IExprId* name,
                IDataType* type)
        IConstraintStmtIf *mkConstraintStmtIf(
                IExpr* cond,
                IConstraintScope* true_c,
                IConstraintScope* false_c)
        IConstraintStmtUnique *mkConstraintStmtUnique(
                )
        IGlobalScope *mkGlobalScope(
                int32_t fileid)
        INamedScope *mkNamedScope(
                IExprId* name)
        IPackageScope *mkPackageScope(
                )
        IDataTypeArray *mkDataTypeArray(
                IDataType* type,
                IExpr* size)
        IDataTypeBool *mkDataTypeBool(
                )
        IDataTypeChandle *mkDataTypeChandle(
                )
        IDataTypeEnum *mkDataTypeEnum(
                IDataTypeUserDefined* tid,
                IExprOpenRangeList* in_rangelist)
        IDataTypeInt *mkDataTypeInt(
                bool is_signed,
                IExpr* width_lhs,
                IExpr* width_rhs,
                IExprDomainOpenRangeList* in_range)
        IDataTypeString *mkDataTypeString(
                bool has_range)
        IDataTypeUserDefined *mkDataTypeUserDefined(
                bool is_global)
        IExprRefPathContext *mkExprRefPathContext(
                IExprHierarchicalId* hier_id)
        IExprRefPathStatic *mkExprRefPathStatic(
                bool is_global)
        IExprSignedNumber *mkExprSignedNumber(
                std_string image,
                uint32_t width,
                int64_t value)
        IExprUnsignedNumber *mkExprUnsignedNumber(
                std_string image,
                uint32_t width,
                uint64_t value)
        IConstraintStmtForall *mkConstraintStmtForall(
                IExprId* iterator_id,
                IDataTypeUserDefined* type_id,
                IExprRefPath* ref_path)
        IConstraintStmtForeach *mkConstraintStmtForeach(
                IExpr* expr)
        IConstraintStmtImplication *mkConstraintStmtImplication(
                IExpr* cond)
        ITypeScope *mkTypeScope(
                IExprId* name,
                ITypeIdentifier* super_t)
        IExprRefPathStaticFunc *mkExprRefPathStaticFunc(
                bool is_global,
                IMethodParameterList* params)
        IExprRefPathSuper *mkExprRefPathSuper(
                IExprHierarchicalId* hier_id)
        IAction *mkAction(
                IExprId* name,
                ITypeIdentifier* super_t,
                bool is_abstract)
        IComponent *mkComponent(
                IExprId* name,
                ITypeIdentifier* super_t)
        IStruct *mkStruct(
                IExprId* name,
                ITypeIdentifier* super_t)
        IState *mkState(
                IExprId* name,
                ITypeIdentifier* super_t)
        IStream *mkStream(
                IExprId* name,
                ITypeIdentifier* super_t)
        IBuffer *mkBuffer(
                IExprId* name,
                ITypeIdentifier* super_t)
        IResource *mkResource(
                IExprId* name,
                ITypeIdentifier* super_t)
cdef extern from "pssp/ast/IExecStmt.h" namespace "pssp::ast":
    cpdef cppclass IExecStmt:
        pass
        void accept(VisitorBase *v)

cdef extern from "pssp/ast/IExpr.h" namespace "pssp::ast":
    cpdef cppclass IExpr:
        pass
        void accept(VisitorBase *v)

cdef extern from "pssp/ast/IRefExpr.h" namespace "pssp::ast":
    cpdef cppclass IRefExpr:
        pass
        void accept(VisitorBase *v)

cdef extern from "pssp/ast/ITemplateParamDeclList.h" namespace "pssp::ast":
    cpdef cppclass ITemplateParamDeclList:
        std_vector[unique_ptr[ITemplateParamDecl]] &getParams();
        void accept(VisitorBase *v)

cdef extern from "pssp/ast/ITemplateParamDecl.h" namespace "pssp::ast":
    cpdef cppclass ITemplateParamDecl:
        IExprIdgetName()
        
        void setName(IExprIdv)
        void accept(VisitorBase *v)

cdef extern from "pssp/ast/IScopeChild.h" namespace "pssp::ast":
    cpdef cppclass IScopeChild:
        const std_string &getDocstring()
        
        void set_docstring(const std_string &v)
        IScope *getParent();
        
        void setParent(IScope *v)
        int32_t getIndex()
        
        void setIndex(int32_t v)
        void accept(VisitorBase *v)

cdef extern from "pssp/ast/ITemplateParamValueList.h" namespace "pssp::ast":
    cpdef cppclass ITemplateParamValueList:
        std_vector[unique_ptr[ITemplateParamValue]] &getValues();
        void accept(VisitorBase *v)

cdef extern from "pssp/ast/ITemplateParamValue.h" namespace "pssp::ast":
    cpdef cppclass ITemplateParamValue:
        pass
        void accept(VisitorBase *v)

cdef extern from "pssp/ast/ITemplateParamTypeValue.h" namespace "pssp::ast":
    cpdef cppclass ITemplateParamTypeValue:
        ITypeIdentifiergetValue()
        
        void setValue(ITypeIdentifierv)
        void accept(VisitorBase *v)

cdef extern from "pssp/ast/ITemplateParamExprValue.h" namespace "pssp::ast":
    cpdef cppclass ITemplateParamExprValue:
        IExprgetValue()
        
        void setValue(IExprv)
        void accept(VisitorBase *v)

cdef extern from "pssp/ast/IConstraintStmt.h" namespace "pssp::ast":
    cpdef cppclass IConstraintStmt(IScopeChild):
        pass

cdef extern from "pssp/ast/IScope.h" namespace "pssp::ast":
    cpdef cppclass IScope(IScopeChild):
        std_vector[unique_ptr[IScopeChild]] &getChildren();
        std_map[std_string,INamedScopeChild *] &getSymtab();

cdef extern from "pssp/ast/INamedScopeChild.h" namespace "pssp::ast":
    cpdef cppclass INamedScopeChild(IScopeChild):
        IExprIdgetName()
        
        void setName(IExprIdv)

cdef extern from "pssp/ast/IPackageImportStmt.h" namespace "pssp::ast":
    cpdef cppclass IPackageImportStmt(IScopeChild):
        std_vector[unique_ptr[IExprId]] &getPath();
        bool getWildcard()
        
        void setWildcard(bool v)
        IExprIdgetAlias()
        
        void setAlias(IExprIdv)

cdef extern from "pssp/ast/IDataType.h" namespace "pssp::ast":
    cpdef cppclass IDataType(IScopeChild):
        pass

cdef extern from "pssp/ast/IExecScope.h" namespace "pssp::ast":
    cpdef cppclass IExecScope(IExecStmt):
        std_vector[unique_ptr[IExecStmt]] &getChildren();

cdef extern from "pssp/ast/IProceduralStmtDataDeclaration.h" namespace "pssp::ast":
    cpdef cppclass IProceduralStmtDataDeclaration(IExecStmt):
        IDataTypegetDatatype()
        
        void setDatatype(IDataTypev)
        IExprIdgetName()
        
        void setName(IExprIdv)

cdef extern from "pssp/ast/IExprBin.h" namespace "pssp::ast":
    cpdef cppclass IExprBin(IExpr):
        IExprgetLhs()
        
        void setLhs(IExprv)
        IExprgetRhs()
        
        void setRhs(IExprv)

cdef extern from "pssp/ast/IExprBitSlice.h" namespace "pssp::ast":
    cpdef cppclass IExprBitSlice(IExpr):
        IExprgetExpr()
        
        void setExpr(IExprv)
        IExprgetLhs()
        
        void setLhs(IExprv)
        IExprgetRhs()
        
        void setRhs(IExprv)

cdef extern from "pssp/ast/IExprBool.h" namespace "pssp::ast":
    cpdef cppclass IExprBool(IExpr):
        bool getValue()
        
        void setValue(bool v)

cdef extern from "pssp/ast/IExprCast.h" namespace "pssp::ast":
    cpdef cppclass IExprCast(IExpr):
        IExprgetCasting_type()
        
        void setCasting_type(IExprv)
        IExprgetExpr()
        
        void setExpr(IExprv)

cdef extern from "pssp/ast/IExprCompileHas.h" namespace "pssp::ast":
    cpdef cppclass IExprCompileHas(IExpr):
        IExprRefPathStaticgetRef()
        
        void setRef(IExprRefPathStaticv)

cdef extern from "pssp/ast/IExprCond.h" namespace "pssp::ast":
    cpdef cppclass IExprCond(IExpr):
        IExprgetCond_e()
        
        void setCond_e(IExprv)
        IExprgetTrue_e()
        
        void setTrue_e(IExprv)
        IExprgetFalse_e()
        
        void setFalse_e(IExprv)

cdef extern from "pssp/ast/IExprDomainOpenRangeList.h" namespace "pssp::ast":
    cpdef cppclass IExprDomainOpenRangeList(IExpr):
        std_vector[unique_ptr[IExprDomainOpenRangeValue]] &getValues();

cdef extern from "pssp/ast/IExprDomainOpenRangeValue.h" namespace "pssp::ast":
    cpdef cppclass IExprDomainOpenRangeValue(IExpr):
        bool getSingle()
        
        void setSingle(bool v)
        IExprgetLhs()
        
        void setLhs(IExprv)
        IExprgetRhs()
        
        void setRhs(IExprv)

cdef extern from "pssp/ast/IExprHierarchicalId.h" namespace "pssp::ast":
    cpdef cppclass IExprHierarchicalId(IExpr):
        std_vector[unique_ptr[IExprMemberPathElem]] &getElems();

cdef extern from "pssp/ast/IExprId.h" namespace "pssp::ast":
    cpdef cppclass IExprId(IExpr):
        const std_string &getId()
        
        void set_id(const std_string &v)
        bool getIs_escaped()
        
        void setIs_escaped(bool v)

cdef extern from "pssp/ast/IExprIn.h" namespace "pssp::ast":
    cpdef cppclass IExprIn(IExpr):
        IExprgetLhs()
        
        void setLhs(IExprv)
        IExprOpenRangeListgetRhs()
        
        void setRhs(IExprOpenRangeListv)

cdef extern from "pssp/ast/IExprMemberPathElem.h" namespace "pssp::ast":
    cpdef cppclass IExprMemberPathElem(IExpr):
        IExprIdgetId()
        
        void setId(IExprIdv)
        IMethodParameterListgetParams()
        
        void setParams(IMethodParameterListv)
        IExprgetSubscript()
        
        void setSubscript(IExprv)
        int32_t getTarget()
        
        void setTarget(int32_t v)

cdef extern from "pssp/ast/IExprNumber.h" namespace "pssp::ast":
    cpdef cppclass IExprNumber(IExpr):
        pass

cdef extern from "pssp/ast/IExprAggregateLiteral.h" namespace "pssp::ast":
    cpdef cppclass IExprAggregateLiteral(IExpr):
        pass

cdef extern from "pssp/ast/IExprOpenRangeList.h" namespace "pssp::ast":
    cpdef cppclass IExprOpenRangeList(IExpr):
        std_vector[unique_ptr[IExprOpenRangeValue]] &getValues();

cdef extern from "pssp/ast/IExprOpenRangeValue.h" namespace "pssp::ast":
    cpdef cppclass IExprOpenRangeValue(IExpr):
        IExprgetLhs()
        
        void setLhs(IExprv)
        IExprgetRhs()
        
        void setRhs(IExprv)

cdef extern from "pssp/ast/IExprRefPath.h" namespace "pssp::ast":
    cpdef cppclass IExprRefPath(IExpr):
        pass

cdef extern from "pssp/ast/IExprRefPathElem.h" namespace "pssp::ast":
    cpdef cppclass IExprRefPathElem(IExpr):
        pass

cdef extern from "pssp/ast/IExprRefPathStaticRooted.h" namespace "pssp::ast":
    cpdef cppclass IExprRefPathStaticRooted(IExpr):
        IExprRefPathStaticgetRoot()
        
        void setRoot(IExprRefPathStaticv)
        IExprRefPathContextgetLeaf()
        
        void setLeaf(IExprRefPathContextv)

cdef extern from "pssp/ast/IExprStaticRefPath.h" namespace "pssp::ast":
    cpdef cppclass IExprStaticRefPath(IExpr):
        bool getIs_global()
        
        void setIs_global(bool v)
        std_vector[unique_ptr[ITypeIdentifierElem]] &getBase();
        IExprMemberPathElemgetLeaf()
        
        void setLeaf(IExprMemberPathElemv)

cdef extern from "pssp/ast/IExprString.h" namespace "pssp::ast":
    cpdef cppclass IExprString(IExpr):
        const std_string &getValue()
        
        void set_value(const std_string &v)
        bool getIs_raw()
        
        void setIs_raw(bool v)

cdef extern from "pssp/ast/IExprSubscript.h" namespace "pssp::ast":
    cpdef cppclass IExprSubscript(IExpr):
        IExprgetExpr()
        
        void setExpr(IExprv)
        IExprgetSubscript()
        
        void setSubscript(IExprv)

cdef extern from "pssp/ast/IExprUnary.h" namespace "pssp::ast":
    cpdef cppclass IExprUnary(IExpr):
        IExprgetRhs()
        
        void setRhs(IExprv)

cdef extern from "pssp/ast/IMethodParameterList.h" namespace "pssp::ast":
    cpdef cppclass IMethodParameterList(IExpr):
        pass

cdef extern from "pssp/ast/ITypeIdentifier.h" namespace "pssp::ast":
    cpdef cppclass ITypeIdentifier(IExpr):
        std_vector[unique_ptr[ITypeIdentifierElem]] &getElems();

cdef extern from "pssp/ast/ITypeIdentifierElem.h" namespace "pssp::ast":
    cpdef cppclass ITypeIdentifierElem(IExpr):
        IExprIdgetId()
        
        void setId(IExprIdv)
        std_vector[unique_ptr[ITemplateParamValue]] &getParams();

cdef extern from "pssp/ast/IRefExprTypeScopeGlobal.h" namespace "pssp::ast":
    cpdef cppclass IRefExprTypeScopeGlobal(IRefExpr):
        int32_t getFileid()
        
        void setFileid(int32_t v)

cdef extern from "pssp/ast/IRefExprTypeScopeContext.h" namespace "pssp::ast":
    cpdef cppclass IRefExprTypeScopeContext(IRefExpr):
        IRefExprgetBase()
        
        void setBase(IRefExprv)
        int32_t getOffset()
        
        void setOffset(int32_t v)

cdef extern from "pssp/ast/IRefExprScopeIndex.h" namespace "pssp::ast":
    cpdef cppclass IRefExprScopeIndex(IRefExpr):
        IRefExprgetBase()
        
        void setBase(IRefExprv)
        int32_t getOffset()
        
        void setOffset(int32_t v)

cdef extern from "pssp/ast/ITemplateGenericTypeParamDecl.h" namespace "pssp::ast":
    cpdef cppclass ITemplateGenericTypeParamDecl(ITemplateParamDecl):
        ITypeIdentifiergetDflt()
        
        void setDflt(ITypeIdentifierv)

cdef extern from "pssp/ast/ITemplateCategoryTypeParamDecl.h" namespace "pssp::ast":
    cpdef cppclass ITemplateCategoryTypeParamDecl(ITemplateParamDecl):
        ITypeIdentifiergetRestriction()
        
        void setRestriction(ITypeIdentifierv)
        ITypeIdentifiergetDflt()
        
        void setDflt(ITypeIdentifierv)

cdef extern from "pssp/ast/ITemplateValueParamDecl.h" namespace "pssp::ast":
    cpdef cppclass ITemplateValueParamDecl(ITemplateParamDecl):
        IExprgetDflt()
        
        void setDflt(IExprv)

cdef extern from "pssp/ast/IConstraintBlock.h" namespace "pssp::ast":
    cpdef cppclass IConstraintBlock(IConstraintStmt):
        const std_string &getName()
        
        void set_name(const std_string &v)
        bool getIs_dynamic()
        
        void setIs_dynamic(bool v)

cdef extern from "pssp/ast/IConstraintScope.h" namespace "pssp::ast":
    cpdef cppclass IConstraintScope(IConstraintStmt):
        pass

cdef extern from "pssp/ast/IConstraintStmtDefault.h" namespace "pssp::ast":
    cpdef cppclass IConstraintStmtDefault(IConstraintStmt):
        IExprHierarchicalIdgetHid()
        
        void setHid(IExprHierarchicalIdv)
        IExprgetExpr()
        
        void setExpr(IExprv)

cdef extern from "pssp/ast/IConstraintStmtDefaultDisable.h" namespace "pssp::ast":
    cpdef cppclass IConstraintStmtDefaultDisable(IConstraintStmt):
        IExprHierarchicalIdgetHid()
        
        void setHid(IExprHierarchicalIdv)

cdef extern from "pssp/ast/IConstraintStmtExpr.h" namespace "pssp::ast":
    cpdef cppclass IConstraintStmtExpr(IConstraintStmt):
        IExprgetExpr()
        
        void setExpr(IExprv)

cdef extern from "pssp/ast/IConstraintStmtField.h" namespace "pssp::ast":
    cpdef cppclass IConstraintStmtField(IConstraintStmt):
        IExprIdgetName()
        
        void setName(IExprIdv)
        IDataTypegetType()
        
        void setType(IDataTypev)

cdef extern from "pssp/ast/IConstraintStmtIf.h" namespace "pssp::ast":
    cpdef cppclass IConstraintStmtIf(IConstraintStmt):
        IExprgetCond()
        
        void setCond(IExprv)
        IConstraintScopegetTrue_c()
        
        void setTrue_c(IConstraintScopev)
        IConstraintScopegetFalse_c()
        
        void setFalse_c(IConstraintScopev)

cdef extern from "pssp/ast/IConstraintStmtUnique.h" namespace "pssp::ast":
    cpdef cppclass IConstraintStmtUnique(IConstraintStmt):
        std_vector[unique_ptr[IExprRefPathContext]] &getList();

cdef extern from "pssp/ast/IGlobalScope.h" namespace "pssp::ast":
    cpdef cppclass IGlobalScope(IScope):
        int32_t getFileid()
        
        void setFileid(int32_t v)

cdef extern from "pssp/ast/INamedScope.h" namespace "pssp::ast":
    cpdef cppclass INamedScope(IScope):
        IExprIdgetName()
        
        void setName(IExprIdv)

cdef extern from "pssp/ast/IPackageScope.h" namespace "pssp::ast":
    cpdef cppclass IPackageScope(IScope):
        std_vector[unique_ptr[IExprId]] &getId();
        IPackageScope *getSibling();
        
        void setSibling(IPackageScope *v)

cdef extern from "pssp/ast/IDataTypeArray.h" namespace "pssp::ast":
    cpdef cppclass IDataTypeArray(IDataType):
        IDataTypegetType()
        
        void setType(IDataTypev)
        IExprgetSize()
        
        void setSize(IExprv)

cdef extern from "pssp/ast/IDataTypeBool.h" namespace "pssp::ast":
    cpdef cppclass IDataTypeBool(IDataType):
        pass

cdef extern from "pssp/ast/IDataTypeChandle.h" namespace "pssp::ast":
    cpdef cppclass IDataTypeChandle(IDataType):
        pass

cdef extern from "pssp/ast/IDataTypeEnum.h" namespace "pssp::ast":
    cpdef cppclass IDataTypeEnum(IDataType):
        IDataTypeUserDefinedgetTid()
        
        void setTid(IDataTypeUserDefinedv)
        IExprOpenRangeListgetIn_rangelist()
        
        void setIn_rangelist(IExprOpenRangeListv)

cdef extern from "pssp/ast/IDataTypeInt.h" namespace "pssp::ast":
    cpdef cppclass IDataTypeInt(IDataType):
        bool getIs_signed()
        
        void setIs_signed(bool v)
        IExprgetWidth_lhs()
        
        void setWidth_lhs(IExprv)
        IExprgetWidth_rhs()
        
        void setWidth_rhs(IExprv)
        IExprDomainOpenRangeListgetIn_range()
        
        void setIn_range(IExprDomainOpenRangeListv)

cdef extern from "pssp/ast/IDataTypeString.h" namespace "pssp::ast":
    cpdef cppclass IDataTypeString(IDataType):
        bool getHas_range()
        
        void setHas_range(bool v)
        std_vector[std_string] &getIn_range();

cdef extern from "pssp/ast/IDataTypeUserDefined.h" namespace "pssp::ast":
    cpdef cppclass IDataTypeUserDefined(IDataType):
        bool getIs_global()
        
        void setIs_global(bool v)
        std_vector[unique_ptr[ITypeIdentifierElem]] &getElems();
        IScopeChild *getTarget_p();
        
        void setTarget_p(IScopeChild *v)

cdef extern from "pssp/ast/IExprRefPathContext.h" namespace "pssp::ast":
    cpdef cppclass IExprRefPathContext(IExprRefPath):
        IExprHierarchicalIdgetHier_id()
        
        void setHier_id(IExprHierarchicalIdv)

cdef extern from "pssp/ast/IExprRefPathStatic.h" namespace "pssp::ast":
    cpdef cppclass IExprRefPathStatic(IExprRefPath):
        bool getIs_global()
        
        void setIs_global(bool v)
        std_vector[unique_ptr[ITypeIdentifierElem]] &getBase();

cdef extern from "pssp/ast/IExprSignedNumber.h" namespace "pssp::ast":
    cpdef cppclass IExprSignedNumber(IExprNumber):
        const std_string &getImage()
        
        void set_image(const std_string &v)
        uint32_t getWidth()
        
        void setWidth(uint32_t v)
        int64_t getValue()
        
        void setValue(int64_t v)

cdef extern from "pssp/ast/IExprUnsignedNumber.h" namespace "pssp::ast":
    cpdef cppclass IExprUnsignedNumber(IExprNumber):
        const std_string &getImage()
        
        void set_image(const std_string &v)
        uint32_t getWidth()
        
        void setWidth(uint32_t v)
        uint64_t getValue()
        
        void setValue(uint64_t v)

cdef extern from "pssp/ast/IConstraintStmtForall.h" namespace "pssp::ast":
    cpdef cppclass IConstraintStmtForall(IConstraintScope):
        IExprIdgetIterator_id()
        
        void setIterator_id(IExprIdv)
        IDataTypeUserDefinedgetType_id()
        
        void setType_id(IDataTypeUserDefinedv)
        IExprRefPathgetRef_path()
        
        void setRef_path(IExprRefPathv)

cdef extern from "pssp/ast/IConstraintStmtForeach.h" namespace "pssp::ast":
    cpdef cppclass IConstraintStmtForeach(IConstraintScope):
        IConstraintStmtField *getIt();
        
        void setIt(IConstraintStmtField *v)
        IConstraintStmtField *getIdx();
        
        void setIdx(IConstraintStmtField *v)
        IExprgetExpr()
        
        void setExpr(IExprv)

cdef extern from "pssp/ast/IConstraintStmtImplication.h" namespace "pssp::ast":
    cpdef cppclass IConstraintStmtImplication(IConstraintScope):
        IExprgetCond()
        
        void setCond(IExprv)

cdef extern from "pssp/ast/ITypeScope.h" namespace "pssp::ast":
    cpdef cppclass ITypeScope(INamedScope):
        ITypeIdentifiergetSuper_t()
        
        void setSuper_t(ITypeIdentifierv)
        ITemplateParamDeclListgetParams()
        
        void setParams(ITemplateParamDeclListv)

cdef extern from "pssp/ast/IExprRefPathStaticFunc.h" namespace "pssp::ast":
    cpdef cppclass IExprRefPathStaticFunc(IExprRefPathStatic):
        IMethodParameterListgetParams()
        
        void setParams(IMethodParameterListv)

cdef extern from "pssp/ast/IExprRefPathSuper.h" namespace "pssp::ast":
    cpdef cppclass IExprRefPathSuper(IExprRefPathContext):
        pass

cdef extern from "pssp/ast/IAction.h" namespace "pssp::ast":
    cpdef cppclass IAction(ITypeScope):
        bool getIs_abstract()
        
        void setIs_abstract(bool v)

cdef extern from "pssp/ast/IComponent.h" namespace "pssp::ast":
    cpdef cppclass IComponent(ITypeScope):
        pass

cdef extern from "pssp/ast/IStruct.h" namespace "pssp::ast":
    cpdef cppclass IStruct(ITypeScope):
        pass

cdef extern from "pssp/ast/IState.h" namespace "pssp::ast":
    cpdef cppclass IState(IStruct):
        pass

cdef extern from "pssp/ast/IStream.h" namespace "pssp::ast":
    cpdef cppclass IStream(IStruct):
        pass

cdef extern from "pssp/ast/IBuffer.h" namespace "pssp::ast":
    cpdef cppclass IBuffer(IStruct):
        pass

cdef extern from "pssp/ast/IResource.h" namespace "pssp::ast":
    cpdef cppclass IResource(IStruct):
        pass

cdef extern from 'pssp/ast/impl/VisitorBase.h' namespace 'pssp::ast':
    cpdef cppclass VisitorBase:
        void visitExecStmt(IExecStmtP i)
        void visitExpr(IExprP i)
        void visitRefExpr(IRefExprP i)
        void visitTemplateParamDeclList(ITemplateParamDeclListP i)
        void visitTemplateParamDecl(ITemplateParamDeclP i)
        void visitScopeChild(IScopeChildP i)
        void visitTemplateParamValueList(ITemplateParamValueListP i)
        void visitTemplateParamValue(ITemplateParamValueP i)
        void visitTemplateParamTypeValue(ITemplateParamTypeValueP i)
        void visitTemplateParamExprValue(ITemplateParamExprValueP i)
        void visitConstraintStmt(IConstraintStmtP i)
        void visitScope(IScopeP i)
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
        void visitExprNumber(IExprNumberP i)
        void visitExprAggregateLiteral(IExprAggregateLiteralP i)
        void visitExprOpenRangeList(IExprOpenRangeListP i)
        void visitExprOpenRangeValue(IExprOpenRangeValueP i)
        void visitExprRefPath(IExprRefPathP i)
        void visitExprRefPathElem(IExprRefPathElemP i)
        void visitExprRefPathStaticRooted(IExprRefPathStaticRootedP i)
        void visitExprStaticRefPath(IExprStaticRefPathP i)
        void visitExprString(IExprStringP i)
        void visitExprSubscript(IExprSubscriptP i)
        void visitExprUnary(IExprUnaryP i)
        void visitMethodParameterList(IMethodParameterListP i)
        void visitTypeIdentifier(ITypeIdentifierP i)
        void visitTypeIdentifierElem(ITypeIdentifierElemP i)
        void visitRefExprTypeScopeGlobal(IRefExprTypeScopeGlobalP i)
        void visitRefExprTypeScopeContext(IRefExprTypeScopeContextP i)
        void visitRefExprScopeIndex(IRefExprScopeIndexP i)
        void visitTemplateGenericTypeParamDecl(ITemplateGenericTypeParamDeclP i)
        void visitTemplateCategoryTypeParamDecl(ITemplateCategoryTypeParamDeclP i)
        void visitTemplateValueParamDecl(ITemplateValueParamDeclP i)
        void visitConstraintBlock(IConstraintBlockP i)
        void visitConstraintScope(IConstraintScopeP i)
        void visitConstraintStmtDefault(IConstraintStmtDefaultP i)
        void visitConstraintStmtDefaultDisable(IConstraintStmtDefaultDisableP i)
        void visitConstraintStmtExpr(IConstraintStmtExprP i)
        void visitConstraintStmtField(IConstraintStmtFieldP i)
        void visitConstraintStmtIf(IConstraintStmtIfP i)
        void visitConstraintStmtUnique(IConstraintStmtUniqueP i)
        void visitGlobalScope(IGlobalScopeP i)
        void visitNamedScope(INamedScopeP i)
        void visitPackageScope(IPackageScopeP i)
        void visitDataTypeArray(IDataTypeArrayP i)
        void visitDataTypeBool(IDataTypeBoolP i)
        void visitDataTypeChandle(IDataTypeChandleP i)
        void visitDataTypeEnum(IDataTypeEnumP i)
        void visitDataTypeInt(IDataTypeIntP i)
        void visitDataTypeString(IDataTypeStringP i)
        void visitDataTypeUserDefined(IDataTypeUserDefinedP i)
        void visitExprRefPathContext(IExprRefPathContextP i)
        void visitExprRefPathStatic(IExprRefPathStaticP i)
        void visitExprSignedNumber(IExprSignedNumberP i)
        void visitExprUnsignedNumber(IExprUnsignedNumberP i)
        void visitConstraintStmtForall(IConstraintStmtForallP i)
        void visitConstraintStmtForeach(IConstraintStmtForeachP i)
        void visitConstraintStmtImplication(IConstraintStmtImplicationP i)
        void visitTypeScope(ITypeScopeP i)
        void visitExprRefPathStaticFunc(IExprRefPathStaticFuncP i)
        void visitExprRefPathSuper(IExprRefPathSuperP i)
        void visitAction(IActionP i)
        void visitComponent(IComponentP i)
        void visitStruct(IStructP i)
        void visitState(IStateP i)
        void visitStream(IStreamP i)
        void visitBuffer(IBufferP i)
        void visitResource(IResourceP i)
cdef extern from 'PyBaseVisitor.h' namespace 'pssp::ast':
    cpdef cppclass PyBaseVisitor(VisitorBase):
        PyBaseVisitor(cpy_ref.PyObject *)
        void py_visitExecStmt(IExecStmt *i)
        void py_visitExpr(IExpr *i)
        void py_visitRefExpr(IRefExpr *i)
        void py_visitTemplateParamDeclList(ITemplateParamDeclList *i)
        void py_visitTemplateParamDecl(ITemplateParamDecl *i)
        void py_visitScopeChild(IScopeChild *i)
        void py_visitTemplateParamValueList(ITemplateParamValueList *i)
        void py_visitTemplateParamValue(ITemplateParamValue *i)
        void py_visitTemplateParamTypeValue(ITemplateParamTypeValue *i)
        void py_visitTemplateParamExprValue(ITemplateParamExprValue *i)
        void py_visitConstraintStmt(IConstraintStmt *i)
        void py_visitScope(IScope *i)
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
        void py_visitExprNumber(IExprNumber *i)
        void py_visitExprAggregateLiteral(IExprAggregateLiteral *i)
        void py_visitExprOpenRangeList(IExprOpenRangeList *i)
        void py_visitExprOpenRangeValue(IExprOpenRangeValue *i)
        void py_visitExprRefPath(IExprRefPath *i)
        void py_visitExprRefPathElem(IExprRefPathElem *i)
        void py_visitExprRefPathStaticRooted(IExprRefPathStaticRooted *i)
        void py_visitExprStaticRefPath(IExprStaticRefPath *i)
        void py_visitExprString(IExprString *i)
        void py_visitExprSubscript(IExprSubscript *i)
        void py_visitExprUnary(IExprUnary *i)
        void py_visitMethodParameterList(IMethodParameterList *i)
        void py_visitTypeIdentifier(ITypeIdentifier *i)
        void py_visitTypeIdentifierElem(ITypeIdentifierElem *i)
        void py_visitRefExprTypeScopeGlobal(IRefExprTypeScopeGlobal *i)
        void py_visitRefExprTypeScopeContext(IRefExprTypeScopeContext *i)
        void py_visitRefExprScopeIndex(IRefExprScopeIndex *i)
        void py_visitTemplateGenericTypeParamDecl(ITemplateGenericTypeParamDecl *i)
        void py_visitTemplateCategoryTypeParamDecl(ITemplateCategoryTypeParamDecl *i)
        void py_visitTemplateValueParamDecl(ITemplateValueParamDecl *i)
        void py_visitConstraintBlock(IConstraintBlock *i)
        void py_visitConstraintScope(IConstraintScope *i)
        void py_visitConstraintStmtDefault(IConstraintStmtDefault *i)
        void py_visitConstraintStmtDefaultDisable(IConstraintStmtDefaultDisable *i)
        void py_visitConstraintStmtExpr(IConstraintStmtExpr *i)
        void py_visitConstraintStmtField(IConstraintStmtField *i)
        void py_visitConstraintStmtIf(IConstraintStmtIf *i)
        void py_visitConstraintStmtUnique(IConstraintStmtUnique *i)
        void py_visitGlobalScope(IGlobalScope *i)
        void py_visitNamedScope(INamedScope *i)
        void py_visitPackageScope(IPackageScope *i)
        void py_visitDataTypeArray(IDataTypeArray *i)
        void py_visitDataTypeBool(IDataTypeBool *i)
        void py_visitDataTypeChandle(IDataTypeChandle *i)
        void py_visitDataTypeEnum(IDataTypeEnum *i)
        void py_visitDataTypeInt(IDataTypeInt *i)
        void py_visitDataTypeString(IDataTypeString *i)
        void py_visitDataTypeUserDefined(IDataTypeUserDefined *i)
        void py_visitExprRefPathContext(IExprRefPathContext *i)
        void py_visitExprRefPathStatic(IExprRefPathStatic *i)
        void py_visitExprSignedNumber(IExprSignedNumber *i)
        void py_visitExprUnsignedNumber(IExprUnsignedNumber *i)
        void py_visitConstraintStmtForall(IConstraintStmtForall *i)
        void py_visitConstraintStmtForeach(IConstraintStmtForeach *i)
        void py_visitConstraintStmtImplication(IConstraintStmtImplication *i)
        void py_visitTypeScope(ITypeScope *i)
        void py_visitExprRefPathStaticFunc(IExprRefPathStaticFunc *i)
        void py_visitExprRefPathSuper(IExprRefPathSuper *i)
        void py_visitAction(IAction *i)
        void py_visitComponent(IComponent *i)
        void py_visitStruct(IStruct *i)
        void py_visitState(IState *i)
        void py_visitStream(IStream *i)
        void py_visitBuffer(IBuffer *i)
        void py_visitResource(IResource *i)
