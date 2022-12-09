# cython: language_level=3
from pssparser cimport pssast_decl
from enum import IntEnum
class ExprBinOp(IntEnum):
    BinOp_LogOr = pssast_decl.ExprBinOp.BinOp_LogOr
    BinOp_LogAnd = pssast_decl.ExprBinOp.BinOp_LogAnd
    BinOp_BitOr = pssast_decl.ExprBinOp.BinOp_BitOr
    BinOp_BitXor = pssast_decl.ExprBinOp.BinOp_BitXor
    BinOp_BitAnd = pssast_decl.ExprBinOp.BinOp_BitAnd
    BinOp_Lt = pssast_decl.ExprBinOp.BinOp_Lt
    BinOp_Le = pssast_decl.ExprBinOp.BinOp_Le
    BinOp_Gt = pssast_decl.ExprBinOp.BinOp_Gt
    BinOp_Ge = pssast_decl.ExprBinOp.BinOp_Ge
    BinOp_Exp = pssast_decl.ExprBinOp.BinOp_Exp
    BinOp_Mul = pssast_decl.ExprBinOp.BinOp_Mul
    BinOp_Div = pssast_decl.ExprBinOp.BinOp_Div
    BinOp_Mod = pssast_decl.ExprBinOp.BinOp_Mod
    BinOp_Add = pssast_decl.ExprBinOp.BinOp_Add
    BinOp_Sub = pssast_decl.ExprBinOp.BinOp_Sub
    BinOp_Shl = pssast_decl.ExprBinOp.BinOp_Shl
    BinOp_Shr = pssast_decl.ExprBinOp.BinOp_Shr
    BinOp_Eq = pssast_decl.ExprBinOp.BinOp_Eq
    BinOp_Ne = pssast_decl.ExprBinOp.BinOp_Ne
class ExprUnaryOp(IntEnum):
    UnaryOp_Plus = pssast_decl.ExprUnaryOp.UnaryOp_Plus
    UnaryOp_Minus = pssast_decl.ExprUnaryOp.UnaryOp_Minus
    UnaryOp_LogNot = pssast_decl.ExprUnaryOp.UnaryOp_LogNot
    UnaryOp_BitNeg = pssast_decl.ExprUnaryOp.UnaryOp_BitNeg
    UnaryOp_BitAnd = pssast_decl.ExprUnaryOp.UnaryOp_BitAnd
    UnaryOp_BitOr = pssast_decl.ExprUnaryOp.UnaryOp_BitOr
    UnaryOp_BitXor = pssast_decl.ExprUnaryOp.UnaryOp_BitXor
class TypeCategory(IntEnum):
    Action = pssast_decl.TypeCategory.Action
    Component = pssast_decl.TypeCategory.Component
    Buffer = pssast_decl.TypeCategory.Buffer
    Resource = pssast_decl.TypeCategory.Resource
    State = pssast_decl.TypeCategory.State
    Stream = pssast_decl.TypeCategory.Stream
cdef class Factory(object):
    cpdef ExecStmt mkExecStmt(self):
        return ExecStmt.mk(self._hndl.mkExecStmt(
), True)
    cpdef Expr mkExpr(self):
        return Expr.mk(self._hndl.mkExpr(
), True)
    cpdef RefExpr mkRefExpr(self):
        return RefExpr.mk(self._hndl.mkRefExpr(
), True)
    cpdef TemplateParamDeclList mkTemplateParamDeclList(self):
        return TemplateParamDeclList.mk(self._hndl.mkTemplateParamDeclList(
), True)
    cpdef TemplateParamDecl mkTemplateParamDecl(self,
            ExprId name):
        return TemplateParamDecl.mk(self._hndl.mkTemplateParamDecl(
                name.asExprId()), True)
    cpdef ScopeChild mkScopeChild(self):
        return ScopeChild.mk(self._hndl.mkScopeChild(
), True)
    cpdef TemplateParamValueList mkTemplateParamValueList(self):
        return TemplateParamValueList.mk(self._hndl.mkTemplateParamValueList(
), True)
    cpdef TemplateParamValue mkTemplateParamValue(self):
        return TemplateParamValue.mk(self._hndl.mkTemplateParamValue(
), True)
    cpdef TemplateParamTypeValue mkTemplateParamTypeValue(self,
            TypeIdentifier value):
        return TemplateParamTypeValue.mk(self._hndl.mkTemplateParamTypeValue(
                value.asTypeIdentifier()), True)
    cpdef TemplateParamExprValue mkTemplateParamExprValue(self,
            Expr value):
        return TemplateParamExprValue.mk(self._hndl.mkTemplateParamExprValue(
                value.asExpr()), True)
    cpdef ConstraintStmt mkConstraintStmt(self):
        return ConstraintStmt.mk(self._hndl.mkConstraintStmt(
), True)
    cpdef Scope mkScope(self):
        return Scope.mk(self._hndl.mkScope(
), True)
    cpdef NamedScopeChild mkNamedScopeChild(self,
            ExprId name):
        return NamedScopeChild.mk(self._hndl.mkNamedScopeChild(
                name.asExprId()), True)
    cpdef PackageImportStmt mkPackageImportStmt(self,
            bool wildcard,
            ExprId alias):
        return PackageImportStmt.mk(self._hndl.mkPackageImportStmt(
                wildcard,
                alias.asExprId()), True)
    cpdef DataType mkDataType(self):
        return DataType.mk(self._hndl.mkDataType(
), True)
    cpdef ExecScope mkExecScope(self):
        return ExecScope.mk(self._hndl.mkExecScope(
), True)
    cpdef ProceduralStmtDataDeclaration mkProceduralStmtDataDeclaration(self,
            DataType datatype,
            ExprId name):
        return ProceduralStmtDataDeclaration.mk(self._hndl.mkProceduralStmtDataDeclaration(
                datatype.asDataType(),
                name.asExprId()), True)
    cpdef ExprBin mkExprBin(self,
            Expr lhs,
             op,
            Expr rhs):
        cdef int op_i = int(op)
        return ExprBin.mk(self._hndl.mkExprBin(
                lhs.asExpr(),
                <pssast_decl.ExprBinOp>(op_i),
                rhs.asExpr()), True)
    cpdef ExprBitSlice mkExprBitSlice(self,
            Expr expr,
            Expr lhs,
            Expr rhs):
        return ExprBitSlice.mk(self._hndl.mkExprBitSlice(
                expr.asExpr(),
                lhs.asExpr(),
                rhs.asExpr()), True)
    cpdef ExprBool mkExprBool(self,
            bool value):
        return ExprBool.mk(self._hndl.mkExprBool(
                value), True)
    cpdef ExprCast mkExprCast(self,
            Expr casting_type,
            Expr expr):
        return ExprCast.mk(self._hndl.mkExprCast(
                casting_type.asExpr(),
                expr.asExpr()), True)
    cpdef ExprCompileHas mkExprCompileHas(self,
            ExprRefPathStatic ref):
        return ExprCompileHas.mk(self._hndl.mkExprCompileHas(
                ref.asExprRefPathStatic()), True)
    cpdef ExprCond mkExprCond(self,
            Expr cond_e,
            Expr true_e,
            Expr false_e):
        return ExprCond.mk(self._hndl.mkExprCond(
                cond_e.asExpr(),
                true_e.asExpr(),
                false_e.asExpr()), True)
    cpdef ExprDomainOpenRangeList mkExprDomainOpenRangeList(self):
        return ExprDomainOpenRangeList.mk(self._hndl.mkExprDomainOpenRangeList(
), True)
    cpdef ExprDomainOpenRangeValue mkExprDomainOpenRangeValue(self,
            bool single,
            Expr lhs,
            Expr rhs):
        return ExprDomainOpenRangeValue.mk(self._hndl.mkExprDomainOpenRangeValue(
                single,
                lhs.asExpr(),
                rhs.asExpr()), True)
    cpdef ExprHierarchicalId mkExprHierarchicalId(self):
        return ExprHierarchicalId.mk(self._hndl.mkExprHierarchicalId(
), True)
    cpdef ExprId mkExprId(self,
            std_string id,
            bool is_escaped):
        return ExprId.mk(self._hndl.mkExprId(
                id,
                is_escaped), True)
    cpdef ExprIn mkExprIn(self,
            Expr lhs,
            ExprOpenRangeList rhs):
        return ExprIn.mk(self._hndl.mkExprIn(
                lhs.asExpr(),
                rhs.asExprOpenRangeList()), True)
    cpdef ExprMemberPathElem mkExprMemberPathElem(self,
            ExprId id,
            MethodParameterList params,
            Expr subscript):
        return ExprMemberPathElem.mk(self._hndl.mkExprMemberPathElem(
                id.asExprId(),
                params.asMethodParameterList(),
                subscript.asExpr()), True)
    cpdef ExprNumber mkExprNumber(self):
        return ExprNumber.mk(self._hndl.mkExprNumber(
), True)
    cpdef ExprAggregateLiteral mkExprAggregateLiteral(self):
        return ExprAggregateLiteral.mk(self._hndl.mkExprAggregateLiteral(
), True)
    cpdef ExprOpenRangeList mkExprOpenRangeList(self):
        return ExprOpenRangeList.mk(self._hndl.mkExprOpenRangeList(
), True)
    cpdef ExprOpenRangeValue mkExprOpenRangeValue(self,
            Expr lhs,
            Expr rhs):
        return ExprOpenRangeValue.mk(self._hndl.mkExprOpenRangeValue(
                lhs.asExpr(),
                rhs.asExpr()), True)
    cpdef ExprRefPath mkExprRefPath(self):
        return ExprRefPath.mk(self._hndl.mkExprRefPath(
), True)
    cpdef ExprRefPathElem mkExprRefPathElem(self):
        return ExprRefPathElem.mk(self._hndl.mkExprRefPathElem(
), True)
    cpdef ExprRefPathStaticRooted mkExprRefPathStaticRooted(self,
            ExprRefPathStatic root,
            ExprRefPathContext leaf):
        return ExprRefPathStaticRooted.mk(self._hndl.mkExprRefPathStaticRooted(
                root.asExprRefPathStatic(),
                leaf.asExprRefPathContext()), True)
    cpdef ExprStaticRefPath mkExprStaticRefPath(self,
            bool is_global,
            ExprMemberPathElem leaf):
        return ExprStaticRefPath.mk(self._hndl.mkExprStaticRefPath(
                is_global,
                leaf.asExprMemberPathElem()), True)
    cpdef ExprString mkExprString(self,
            std_string value,
            bool is_raw):
        return ExprString.mk(self._hndl.mkExprString(
                value,
                is_raw), True)
    cpdef ExprSubscript mkExprSubscript(self,
            Expr expr,
            Expr subscript):
        return ExprSubscript.mk(self._hndl.mkExprSubscript(
                expr.asExpr(),
                subscript.asExpr()), True)
    cpdef ExprUnary mkExprUnary(self,
             op,
            Expr rhs):
        cdef int op_i = int(op)
        return ExprUnary.mk(self._hndl.mkExprUnary(
                <pssast_decl.ExprUnaryOp>(op_i),
                rhs.asExpr()), True)
    cpdef MethodParameterList mkMethodParameterList(self):
        return MethodParameterList.mk(self._hndl.mkMethodParameterList(
), True)
    cpdef TypeIdentifier mkTypeIdentifier(self):
        return TypeIdentifier.mk(self._hndl.mkTypeIdentifier(
), True)
    cpdef TypeIdentifierElem mkTypeIdentifierElem(self,
            ExprId id):
        return TypeIdentifierElem.mk(self._hndl.mkTypeIdentifierElem(
                id.asExprId()), True)
    cpdef RefExprTypeScopeGlobal mkRefExprTypeScopeGlobal(self,
            int32_t fileid):
        return RefExprTypeScopeGlobal.mk(self._hndl.mkRefExprTypeScopeGlobal(
                fileid), True)
    cpdef RefExprTypeScopeContext mkRefExprTypeScopeContext(self,
            RefExpr base,
            int32_t offset):
        return RefExprTypeScopeContext.mk(self._hndl.mkRefExprTypeScopeContext(
                base.asRefExpr(),
                offset), True)
    cpdef RefExprScopeIndex mkRefExprScopeIndex(self,
            RefExpr base,
            int32_t offset):
        return RefExprScopeIndex.mk(self._hndl.mkRefExprScopeIndex(
                base.asRefExpr(),
                offset), True)
    cpdef TemplateGenericTypeParamDecl mkTemplateGenericTypeParamDecl(self,
            ExprId name,
            TypeIdentifier dflt):
        return TemplateGenericTypeParamDecl.mk(self._hndl.mkTemplateGenericTypeParamDecl(
                name.asExprId(),
                dflt.asTypeIdentifier()), True)
    cpdef TemplateCategoryTypeParamDecl mkTemplateCategoryTypeParamDecl(self,
            ExprId name,
             category,
            TypeIdentifier restriction,
            TypeIdentifier dflt):
        cdef int category_i = int(category)
        return TemplateCategoryTypeParamDecl.mk(self._hndl.mkTemplateCategoryTypeParamDecl(
                name.asExprId(),
                <pssast_decl.TypeCategory>(category_i),
                restriction.asTypeIdentifier(),
                dflt.asTypeIdentifier()), True)
    cpdef TemplateValueParamDecl mkTemplateValueParamDecl(self,
            ExprId name,
            Expr dflt):
        return TemplateValueParamDecl.mk(self._hndl.mkTemplateValueParamDecl(
                name.asExprId(),
                dflt.asExpr()), True)
    cpdef ConstraintBlock mkConstraintBlock(self,
            std_string name,
            bool is_dynamic):
        return ConstraintBlock.mk(self._hndl.mkConstraintBlock(
                name,
                is_dynamic), True)
    cpdef ConstraintScope mkConstraintScope(self):
        return ConstraintScope.mk(self._hndl.mkConstraintScope(
), True)
    cpdef ConstraintStmtDefault mkConstraintStmtDefault(self,
            ExprHierarchicalId hid,
            Expr expr):
        return ConstraintStmtDefault.mk(self._hndl.mkConstraintStmtDefault(
                hid.asExprHierarchicalId(),
                expr.asExpr()), True)
    cpdef ConstraintStmtDefaultDisable mkConstraintStmtDefaultDisable(self,
            ExprHierarchicalId hid):
        return ConstraintStmtDefaultDisable.mk(self._hndl.mkConstraintStmtDefaultDisable(
                hid.asExprHierarchicalId()), True)
    cpdef ConstraintStmtExpr mkConstraintStmtExpr(self,
            Expr expr):
        return ConstraintStmtExpr.mk(self._hndl.mkConstraintStmtExpr(
                expr.asExpr()), True)
    cpdef ConstraintStmtField mkConstraintStmtField(self,
            ExprId name,
            DataType type):
        return ConstraintStmtField.mk(self._hndl.mkConstraintStmtField(
                name.asExprId(),
                type.asDataType()), True)
    cpdef ConstraintStmtIf mkConstraintStmtIf(self,
            Expr cond,
            ConstraintScope true_c,
            ConstraintScope false_c):
        return ConstraintStmtIf.mk(self._hndl.mkConstraintStmtIf(
                cond.asExpr(),
                true_c.asConstraintScope(),
                false_c.asConstraintScope()), True)
    cpdef ConstraintStmtUnique mkConstraintStmtUnique(self):
        return ConstraintStmtUnique.mk(self._hndl.mkConstraintStmtUnique(
), True)
    cpdef GlobalScope mkGlobalScope(self,
            int32_t fileid):
        return GlobalScope.mk(self._hndl.mkGlobalScope(
                fileid), True)
    cpdef NamedScope mkNamedScope(self,
            ExprId name):
        return NamedScope.mk(self._hndl.mkNamedScope(
                name.asExprId()), True)
    cpdef PackageScope mkPackageScope(self):
        return PackageScope.mk(self._hndl.mkPackageScope(
), True)
    cpdef DataTypeArray mkDataTypeArray(self,
            DataType type,
            Expr size):
        return DataTypeArray.mk(self._hndl.mkDataTypeArray(
                type.asDataType(),
                size.asExpr()), True)
    cpdef DataTypeBool mkDataTypeBool(self):
        return DataTypeBool.mk(self._hndl.mkDataTypeBool(
), True)
    cpdef DataTypeChandle mkDataTypeChandle(self):
        return DataTypeChandle.mk(self._hndl.mkDataTypeChandle(
), True)
    cpdef DataTypeEnum mkDataTypeEnum(self,
            DataTypeUserDefined tid,
            ExprOpenRangeList in_rangelist):
        return DataTypeEnum.mk(self._hndl.mkDataTypeEnum(
                tid.asDataTypeUserDefined(),
                in_rangelist.asExprOpenRangeList()), True)
    cpdef DataTypeInt mkDataTypeInt(self,
            bool is_signed,
            Expr width_lhs,
            Expr width_rhs,
            ExprDomainOpenRangeList in_range):
        return DataTypeInt.mk(self._hndl.mkDataTypeInt(
                is_signed,
                width_lhs.asExpr(),
                width_rhs.asExpr(),
                in_range.asExprDomainOpenRangeList()), True)
    cpdef DataTypeString mkDataTypeString(self,
            bool has_range):
        return DataTypeString.mk(self._hndl.mkDataTypeString(
                has_range), True)
    cpdef DataTypeUserDefined mkDataTypeUserDefined(self,
            bool is_global):
        return DataTypeUserDefined.mk(self._hndl.mkDataTypeUserDefined(
                is_global), True)
    cpdef ExprRefPathContext mkExprRefPathContext(self,
            ExprHierarchicalId hier_id):
        return ExprRefPathContext.mk(self._hndl.mkExprRefPathContext(
                hier_id.asExprHierarchicalId()), True)
    cpdef ExprRefPathStatic mkExprRefPathStatic(self,
            bool is_global):
        return ExprRefPathStatic.mk(self._hndl.mkExprRefPathStatic(
                is_global), True)
    cpdef ExprSignedNumber mkExprSignedNumber(self,
            std_string image,
            uint32_t width,
            int64_t value):
        return ExprSignedNumber.mk(self._hndl.mkExprSignedNumber(
                image,
                width,
                value), True)
    cpdef ExprUnsignedNumber mkExprUnsignedNumber(self,
            std_string image,
            uint32_t width,
            uint64_t value):
        return ExprUnsignedNumber.mk(self._hndl.mkExprUnsignedNumber(
                image,
                width,
                value), True)
    cpdef ConstraintStmtForall mkConstraintStmtForall(self,
            ExprId iterator_id,
            DataTypeUserDefined type_id,
            ExprRefPath ref_path):
        return ConstraintStmtForall.mk(self._hndl.mkConstraintStmtForall(
                iterator_id.asExprId(),
                type_id.asDataTypeUserDefined(),
                ref_path.asExprRefPath()), True)
    cpdef ConstraintStmtForeach mkConstraintStmtForeach(self,
            Expr expr):
        return ConstraintStmtForeach.mk(self._hndl.mkConstraintStmtForeach(
                expr.asExpr()), True)
    cpdef ConstraintStmtImplication mkConstraintStmtImplication(self,
            Expr cond):
        return ConstraintStmtImplication.mk(self._hndl.mkConstraintStmtImplication(
                cond.asExpr()), True)
    cpdef TypeScope mkTypeScope(self,
            ExprId name,
            TypeIdentifier super_t):
        return TypeScope.mk(self._hndl.mkTypeScope(
                name.asExprId(),
                super_t.asTypeIdentifier()), True)
    cpdef ExprRefPathStaticFunc mkExprRefPathStaticFunc(self,
            bool is_global,
            MethodParameterList params):
        return ExprRefPathStaticFunc.mk(self._hndl.mkExprRefPathStaticFunc(
                is_global,
                params.asMethodParameterList()), True)
    cpdef ExprRefPathSuper mkExprRefPathSuper(self,
            ExprHierarchicalId hier_id):
        return ExprRefPathSuper.mk(self._hndl.mkExprRefPathSuper(
                hier_id.asExprHierarchicalId()), True)
    cpdef Action mkAction(self,
            ExprId name,
            TypeIdentifier super_t,
            bool is_abstract):
        return Action.mk(self._hndl.mkAction(
                name.asExprId(),
                super_t.asTypeIdentifier(),
                is_abstract), True)
    cpdef Component mkComponent(self,
            ExprId name,
            TypeIdentifier super_t):
        return Component.mk(self._hndl.mkComponent(
                name.asExprId(),
                super_t.asTypeIdentifier()), True)
    cpdef Struct mkStruct(self,
            ExprId name,
            TypeIdentifier super_t):
        return Struct.mk(self._hndl.mkStruct(
                name.asExprId(),
                super_t.asTypeIdentifier()), True)
    cpdef State mkState(self,
            ExprId name,
            TypeIdentifier super_t):
        return State.mk(self._hndl.mkState(
                name.asExprId(),
                super_t.asTypeIdentifier()), True)
    cpdef Stream mkStream(self,
            ExprId name,
            TypeIdentifier super_t):
        return Stream.mk(self._hndl.mkStream(
                name.asExprId(),
                super_t.asTypeIdentifier()), True)
    cpdef Buffer mkBuffer(self,
            ExprId name,
            TypeIdentifier super_t):
        return Buffer.mk(self._hndl.mkBuffer(
                name.asExprId(),
                super_t.asTypeIdentifier()), True)
    cpdef Resource mkResource(self,
            ExprId name,
            TypeIdentifier super_t):
        return Resource.mk(self._hndl.mkResource(
                name.asExprId(),
                super_t.asTypeIdentifier()), True)
    @staticmethod
    cdef mk(pssast_decl.IFactory *hndl):
        ret = Factory()
        ret._hndl = hndl
        return ret
cdef class ExecStmt(object):
    
    def __dealloc__(self):
        if self._owned and self._hndl != NULL:
            del self._hndl
    
    cpdef void accept(self, VisitorBase v):
        self._hndl.accept(v._hndl)
    
    cdef pssast_decl.IExecStmt *asExecStmt(self):
        return dynamic_cast[pssast_decl.IExecStmtP](self._hndl)
    @staticmethod
    cdef ExecStmt mk(pssast_decl.IExecStmt *hndl, bool owned):
        '''Creates a Python wrapper around native class'''
        ret = ExecStmt()
        ret._hndl = hndl
        ret._owned = owned
        return ret
    

cdef class Expr(object):
    
    def __dealloc__(self):
        if self._owned and self._hndl != NULL:
            del self._hndl
    
    cpdef void accept(self, VisitorBase v):
        self._hndl.accept(v._hndl)
    
    cdef pssast_decl.IExpr *asExpr(self):
        return dynamic_cast[pssast_decl.IExprP](self._hndl)
    @staticmethod
    cdef Expr mk(pssast_decl.IExpr *hndl, bool owned):
        '''Creates a Python wrapper around native class'''
        ret = Expr()
        ret._hndl = hndl
        ret._owned = owned
        return ret
    

cdef class RefExpr(object):
    
    def __dealloc__(self):
        if self._owned and self._hndl != NULL:
            del self._hndl
    
    cpdef void accept(self, VisitorBase v):
        self._hndl.accept(v._hndl)
    
    cdef pssast_decl.IRefExpr *asRefExpr(self):
        return dynamic_cast[pssast_decl.IRefExprP](self._hndl)
    @staticmethod
    cdef RefExpr mk(pssast_decl.IRefExpr *hndl, bool owned):
        '''Creates a Python wrapper around native class'''
        ret = RefExpr()
        ret._hndl = hndl
        ret._owned = owned
        return ret
    

cdef class TemplateParamDeclList(object):
    
    def __dealloc__(self):
        if self._owned and self._hndl != NULL:
            del self._hndl
    
    cpdef void accept(self, VisitorBase v):
        self._hndl.accept(v._hndl)
    
    cdef pssast_decl.ITemplateParamDeclList *asTemplateParamDeclList(self):
        return dynamic_cast[pssast_decl.ITemplateParamDeclListP](self._hndl)
    @staticmethod
    cdef TemplateParamDeclList mk(pssast_decl.ITemplateParamDeclList *hndl, bool owned):
        '''Creates a Python wrapper around native class'''
        ret = TemplateParamDeclList()
        ret._hndl = hndl
        ret._owned = owned
        return ret
    

cdef class TemplateParamDecl(object):
    
    def __dealloc__(self):
        if self._owned and self._hndl != NULL:
            del self._hndl
    
    cpdef void accept(self, VisitorBase v):
        self._hndl.accept(v._hndl)
    
    cdef pssast_decl.ITemplateParamDecl *asTemplateParamDecl(self):
        return dynamic_cast[pssast_decl.ITemplateParamDeclP](self._hndl)
    @staticmethod
    cdef TemplateParamDecl mk(pssast_decl.ITemplateParamDecl *hndl, bool owned):
        '''Creates a Python wrapper around native class'''
        ret = TemplateParamDecl()
        ret._hndl = hndl
        ret._owned = owned
        return ret
    

cdef class ScopeChild(object):
    
    def __dealloc__(self):
        if self._owned and self._hndl != NULL:
            del self._hndl
    
    cpdef void accept(self, VisitorBase v):
        self._hndl.accept(v._hndl)
    
    cdef pssast_decl.IScopeChild *asScopeChild(self):
        return dynamic_cast[pssast_decl.IScopeChildP](self._hndl)
    @staticmethod
    cdef ScopeChild mk(pssast_decl.IScopeChild *hndl, bool owned):
        '''Creates a Python wrapper around native class'''
        ret = ScopeChild()
        ret._hndl = hndl
        ret._owned = owned
        return ret
    
    cpdef std_string getDocstring(self):
        return dynamic_cast[pssast_decl.IScopeChildP](self._hndl).getDocstring()
    cpdef int32_t getIndex(self):
        return dynamic_cast[pssast_decl.IScopeChildP](self._hndl).getIndex()

cdef class TemplateParamValueList(object):
    
    def __dealloc__(self):
        if self._owned and self._hndl != NULL:
            del self._hndl
    
    cpdef void accept(self, VisitorBase v):
        self._hndl.accept(v._hndl)
    
    cdef pssast_decl.ITemplateParamValueList *asTemplateParamValueList(self):
        return dynamic_cast[pssast_decl.ITemplateParamValueListP](self._hndl)
    @staticmethod
    cdef TemplateParamValueList mk(pssast_decl.ITemplateParamValueList *hndl, bool owned):
        '''Creates a Python wrapper around native class'''
        ret = TemplateParamValueList()
        ret._hndl = hndl
        ret._owned = owned
        return ret
    

cdef class TemplateParamValue(object):
    
    def __dealloc__(self):
        if self._owned and self._hndl != NULL:
            del self._hndl
    
    cpdef void accept(self, VisitorBase v):
        self._hndl.accept(v._hndl)
    
    cdef pssast_decl.ITemplateParamValue *asTemplateParamValue(self):
        return dynamic_cast[pssast_decl.ITemplateParamValueP](self._hndl)
    @staticmethod
    cdef TemplateParamValue mk(pssast_decl.ITemplateParamValue *hndl, bool owned):
        '''Creates a Python wrapper around native class'''
        ret = TemplateParamValue()
        ret._hndl = hndl
        ret._owned = owned
        return ret
    

cdef class TemplateParamTypeValue(object):
    
    def __dealloc__(self):
        if self._owned and self._hndl != NULL:
            del self._hndl
    
    cpdef void accept(self, VisitorBase v):
        self._hndl.accept(v._hndl)
    
    cdef pssast_decl.ITemplateParamTypeValue *asTemplateParamTypeValue(self):
        return dynamic_cast[pssast_decl.ITemplateParamTypeValueP](self._hndl)
    @staticmethod
    cdef TemplateParamTypeValue mk(pssast_decl.ITemplateParamTypeValue *hndl, bool owned):
        '''Creates a Python wrapper around native class'''
        ret = TemplateParamTypeValue()
        ret._hndl = hndl
        ret._owned = owned
        return ret
    

cdef class TemplateParamExprValue(object):
    
    def __dealloc__(self):
        if self._owned and self._hndl != NULL:
            del self._hndl
    
    cpdef void accept(self, VisitorBase v):
        self._hndl.accept(v._hndl)
    
    cdef pssast_decl.ITemplateParamExprValue *asTemplateParamExprValue(self):
        return dynamic_cast[pssast_decl.ITemplateParamExprValueP](self._hndl)
    @staticmethod
    cdef TemplateParamExprValue mk(pssast_decl.ITemplateParamExprValue *hndl, bool owned):
        '''Creates a Python wrapper around native class'''
        ret = TemplateParamExprValue()
        ret._hndl = hndl
        ret._owned = owned
        return ret
    

cdef class ConstraintStmt(ScopeChild):
    
    cdef pssast_decl.IConstraintStmt *asConstraintStmt(self):
        return dynamic_cast[pssast_decl.IConstraintStmtP](self._hndl)
    @staticmethod
    cdef ConstraintStmt mk(pssast_decl.IConstraintStmt *hndl, bool owned):
        '''Creates a Python wrapper around native class'''
        ret = ConstraintStmt()
        ret._hndl = hndl
        ret._owned = owned
        return ret
    

cdef class Scope(ScopeChild):
    
    cdef pssast_decl.IScope *asScope(self):
        return dynamic_cast[pssast_decl.IScopeP](self._hndl)
    @staticmethod
    cdef Scope mk(pssast_decl.IScope *hndl, bool owned):
        '''Creates a Python wrapper around native class'''
        ret = Scope()
        ret._hndl = hndl
        ret._owned = owned
        return ret
    

cdef class NamedScopeChild(ScopeChild):
    
    cdef pssast_decl.INamedScopeChild *asNamedScopeChild(self):
        return dynamic_cast[pssast_decl.INamedScopeChildP](self._hndl)
    @staticmethod
    cdef NamedScopeChild mk(pssast_decl.INamedScopeChild *hndl, bool owned):
        '''Creates a Python wrapper around native class'''
        ret = NamedScopeChild()
        ret._hndl = hndl
        ret._owned = owned
        return ret
    

cdef class PackageImportStmt(ScopeChild):
    
    cdef pssast_decl.IPackageImportStmt *asPackageImportStmt(self):
        return dynamic_cast[pssast_decl.IPackageImportStmtP](self._hndl)
    @staticmethod
    cdef PackageImportStmt mk(pssast_decl.IPackageImportStmt *hndl, bool owned):
        '''Creates a Python wrapper around native class'''
        ret = PackageImportStmt()
        ret._hndl = hndl
        ret._owned = owned
        return ret
    
    cpdef bool getWildcard(self):
        return dynamic_cast[pssast_decl.IPackageImportStmtP](self._hndl).getWildcard()

cdef class DataType(ScopeChild):
    
    cdef pssast_decl.IDataType *asDataType(self):
        return dynamic_cast[pssast_decl.IDataTypeP](self._hndl)
    @staticmethod
    cdef DataType mk(pssast_decl.IDataType *hndl, bool owned):
        '''Creates a Python wrapper around native class'''
        ret = DataType()
        ret._hndl = hndl
        ret._owned = owned
        return ret
    

cdef class ExecScope(ExecStmt):
    
    cdef pssast_decl.IExecScope *asExecScope(self):
        return dynamic_cast[pssast_decl.IExecScopeP](self._hndl)
    @staticmethod
    cdef ExecScope mk(pssast_decl.IExecScope *hndl, bool owned):
        '''Creates a Python wrapper around native class'''
        ret = ExecScope()
        ret._hndl = hndl
        ret._owned = owned
        return ret
    

cdef class ProceduralStmtDataDeclaration(ExecStmt):
    
    cdef pssast_decl.IProceduralStmtDataDeclaration *asProceduralStmtDataDeclaration(self):
        return dynamic_cast[pssast_decl.IProceduralStmtDataDeclarationP](self._hndl)
    @staticmethod
    cdef ProceduralStmtDataDeclaration mk(pssast_decl.IProceduralStmtDataDeclaration *hndl, bool owned):
        '''Creates a Python wrapper around native class'''
        ret = ProceduralStmtDataDeclaration()
        ret._hndl = hndl
        ret._owned = owned
        return ret
    

cdef class ExprBin(Expr):
    
    cdef pssast_decl.IExprBin *asExprBin(self):
        return dynamic_cast[pssast_decl.IExprBinP](self._hndl)
    @staticmethod
    cdef ExprBin mk(pssast_decl.IExprBin *hndl, bool owned):
        '''Creates a Python wrapper around native class'''
        ret = ExprBin()
        ret._hndl = hndl
        ret._owned = owned
        return ret
    

cdef class ExprBitSlice(Expr):
    
    cdef pssast_decl.IExprBitSlice *asExprBitSlice(self):
        return dynamic_cast[pssast_decl.IExprBitSliceP](self._hndl)
    @staticmethod
    cdef ExprBitSlice mk(pssast_decl.IExprBitSlice *hndl, bool owned):
        '''Creates a Python wrapper around native class'''
        ret = ExprBitSlice()
        ret._hndl = hndl
        ret._owned = owned
        return ret
    

cdef class ExprBool(Expr):
    
    cdef pssast_decl.IExprBool *asExprBool(self):
        return dynamic_cast[pssast_decl.IExprBoolP](self._hndl)
    @staticmethod
    cdef ExprBool mk(pssast_decl.IExprBool *hndl, bool owned):
        '''Creates a Python wrapper around native class'''
        ret = ExprBool()
        ret._hndl = hndl
        ret._owned = owned
        return ret
    
    cpdef bool getValue(self):
        return dynamic_cast[pssast_decl.IExprBoolP](self._hndl).getValue()

cdef class ExprCast(Expr):
    
    cdef pssast_decl.IExprCast *asExprCast(self):
        return dynamic_cast[pssast_decl.IExprCastP](self._hndl)
    @staticmethod
    cdef ExprCast mk(pssast_decl.IExprCast *hndl, bool owned):
        '''Creates a Python wrapper around native class'''
        ret = ExprCast()
        ret._hndl = hndl
        ret._owned = owned
        return ret
    

cdef class ExprCompileHas(Expr):
    
    cdef pssast_decl.IExprCompileHas *asExprCompileHas(self):
        return dynamic_cast[pssast_decl.IExprCompileHasP](self._hndl)
    @staticmethod
    cdef ExprCompileHas mk(pssast_decl.IExprCompileHas *hndl, bool owned):
        '''Creates a Python wrapper around native class'''
        ret = ExprCompileHas()
        ret._hndl = hndl
        ret._owned = owned
        return ret
    

cdef class ExprCond(Expr):
    
    cdef pssast_decl.IExprCond *asExprCond(self):
        return dynamic_cast[pssast_decl.IExprCondP](self._hndl)
    @staticmethod
    cdef ExprCond mk(pssast_decl.IExprCond *hndl, bool owned):
        '''Creates a Python wrapper around native class'''
        ret = ExprCond()
        ret._hndl = hndl
        ret._owned = owned
        return ret
    

cdef class ExprDomainOpenRangeList(Expr):
    
    cdef pssast_decl.IExprDomainOpenRangeList *asExprDomainOpenRangeList(self):
        return dynamic_cast[pssast_decl.IExprDomainOpenRangeListP](self._hndl)
    @staticmethod
    cdef ExprDomainOpenRangeList mk(pssast_decl.IExprDomainOpenRangeList *hndl, bool owned):
        '''Creates a Python wrapper around native class'''
        ret = ExprDomainOpenRangeList()
        ret._hndl = hndl
        ret._owned = owned
        return ret
    

cdef class ExprDomainOpenRangeValue(Expr):
    
    cdef pssast_decl.IExprDomainOpenRangeValue *asExprDomainOpenRangeValue(self):
        return dynamic_cast[pssast_decl.IExprDomainOpenRangeValueP](self._hndl)
    @staticmethod
    cdef ExprDomainOpenRangeValue mk(pssast_decl.IExprDomainOpenRangeValue *hndl, bool owned):
        '''Creates a Python wrapper around native class'''
        ret = ExprDomainOpenRangeValue()
        ret._hndl = hndl
        ret._owned = owned
        return ret
    
    cpdef bool getSingle(self):
        return dynamic_cast[pssast_decl.IExprDomainOpenRangeValueP](self._hndl).getSingle()

cdef class ExprHierarchicalId(Expr):
    
    cdef pssast_decl.IExprHierarchicalId *asExprHierarchicalId(self):
        return dynamic_cast[pssast_decl.IExprHierarchicalIdP](self._hndl)
    @staticmethod
    cdef ExprHierarchicalId mk(pssast_decl.IExprHierarchicalId *hndl, bool owned):
        '''Creates a Python wrapper around native class'''
        ret = ExprHierarchicalId()
        ret._hndl = hndl
        ret._owned = owned
        return ret
    

cdef class ExprId(Expr):
    
    cdef pssast_decl.IExprId *asExprId(self):
        return dynamic_cast[pssast_decl.IExprIdP](self._hndl)
    @staticmethod
    cdef ExprId mk(pssast_decl.IExprId *hndl, bool owned):
        '''Creates a Python wrapper around native class'''
        ret = ExprId()
        ret._hndl = hndl
        ret._owned = owned
        return ret
    
    cpdef std_string getId(self):
        return dynamic_cast[pssast_decl.IExprIdP](self._hndl).getId()
    cpdef bool getIs_escaped(self):
        return dynamic_cast[pssast_decl.IExprIdP](self._hndl).getIs_escaped()

cdef class ExprIn(Expr):
    
    cdef pssast_decl.IExprIn *asExprIn(self):
        return dynamic_cast[pssast_decl.IExprInP](self._hndl)
    @staticmethod
    cdef ExprIn mk(pssast_decl.IExprIn *hndl, bool owned):
        '''Creates a Python wrapper around native class'''
        ret = ExprIn()
        ret._hndl = hndl
        ret._owned = owned
        return ret
    

cdef class ExprMemberPathElem(Expr):
    
    cdef pssast_decl.IExprMemberPathElem *asExprMemberPathElem(self):
        return dynamic_cast[pssast_decl.IExprMemberPathElemP](self._hndl)
    @staticmethod
    cdef ExprMemberPathElem mk(pssast_decl.IExprMemberPathElem *hndl, bool owned):
        '''Creates a Python wrapper around native class'''
        ret = ExprMemberPathElem()
        ret._hndl = hndl
        ret._owned = owned
        return ret
    
    cpdef int32_t getTarget(self):
        return dynamic_cast[pssast_decl.IExprMemberPathElemP](self._hndl).getTarget()

cdef class ExprNumber(Expr):
    
    cdef pssast_decl.IExprNumber *asExprNumber(self):
        return dynamic_cast[pssast_decl.IExprNumberP](self._hndl)
    @staticmethod
    cdef ExprNumber mk(pssast_decl.IExprNumber *hndl, bool owned):
        '''Creates a Python wrapper around native class'''
        ret = ExprNumber()
        ret._hndl = hndl
        ret._owned = owned
        return ret
    

cdef class ExprAggregateLiteral(Expr):
    
    cdef pssast_decl.IExprAggregateLiteral *asExprAggregateLiteral(self):
        return dynamic_cast[pssast_decl.IExprAggregateLiteralP](self._hndl)
    @staticmethod
    cdef ExprAggregateLiteral mk(pssast_decl.IExprAggregateLiteral *hndl, bool owned):
        '''Creates a Python wrapper around native class'''
        ret = ExprAggregateLiteral()
        ret._hndl = hndl
        ret._owned = owned
        return ret
    

cdef class ExprOpenRangeList(Expr):
    
    cdef pssast_decl.IExprOpenRangeList *asExprOpenRangeList(self):
        return dynamic_cast[pssast_decl.IExprOpenRangeListP](self._hndl)
    @staticmethod
    cdef ExprOpenRangeList mk(pssast_decl.IExprOpenRangeList *hndl, bool owned):
        '''Creates a Python wrapper around native class'''
        ret = ExprOpenRangeList()
        ret._hndl = hndl
        ret._owned = owned
        return ret
    

cdef class ExprOpenRangeValue(Expr):
    
    cdef pssast_decl.IExprOpenRangeValue *asExprOpenRangeValue(self):
        return dynamic_cast[pssast_decl.IExprOpenRangeValueP](self._hndl)
    @staticmethod
    cdef ExprOpenRangeValue mk(pssast_decl.IExprOpenRangeValue *hndl, bool owned):
        '''Creates a Python wrapper around native class'''
        ret = ExprOpenRangeValue()
        ret._hndl = hndl
        ret._owned = owned
        return ret
    

cdef class ExprRefPath(Expr):
    
    cdef pssast_decl.IExprRefPath *asExprRefPath(self):
        return dynamic_cast[pssast_decl.IExprRefPathP](self._hndl)
    @staticmethod
    cdef ExprRefPath mk(pssast_decl.IExprRefPath *hndl, bool owned):
        '''Creates a Python wrapper around native class'''
        ret = ExprRefPath()
        ret._hndl = hndl
        ret._owned = owned
        return ret
    

cdef class ExprRefPathElem(Expr):
    
    cdef pssast_decl.IExprRefPathElem *asExprRefPathElem(self):
        return dynamic_cast[pssast_decl.IExprRefPathElemP](self._hndl)
    @staticmethod
    cdef ExprRefPathElem mk(pssast_decl.IExprRefPathElem *hndl, bool owned):
        '''Creates a Python wrapper around native class'''
        ret = ExprRefPathElem()
        ret._hndl = hndl
        ret._owned = owned
        return ret
    

cdef class ExprRefPathStaticRooted(Expr):
    
    cdef pssast_decl.IExprRefPathStaticRooted *asExprRefPathStaticRooted(self):
        return dynamic_cast[pssast_decl.IExprRefPathStaticRootedP](self._hndl)
    @staticmethod
    cdef ExprRefPathStaticRooted mk(pssast_decl.IExprRefPathStaticRooted *hndl, bool owned):
        '''Creates a Python wrapper around native class'''
        ret = ExprRefPathStaticRooted()
        ret._hndl = hndl
        ret._owned = owned
        return ret
    

cdef class ExprStaticRefPath(Expr):
    
    cdef pssast_decl.IExprStaticRefPath *asExprStaticRefPath(self):
        return dynamic_cast[pssast_decl.IExprStaticRefPathP](self._hndl)
    @staticmethod
    cdef ExprStaticRefPath mk(pssast_decl.IExprStaticRefPath *hndl, bool owned):
        '''Creates a Python wrapper around native class'''
        ret = ExprStaticRefPath()
        ret._hndl = hndl
        ret._owned = owned
        return ret
    
    cpdef bool getIs_global(self):
        return dynamic_cast[pssast_decl.IExprStaticRefPathP](self._hndl).getIs_global()

cdef class ExprString(Expr):
    
    cdef pssast_decl.IExprString *asExprString(self):
        return dynamic_cast[pssast_decl.IExprStringP](self._hndl)
    @staticmethod
    cdef ExprString mk(pssast_decl.IExprString *hndl, bool owned):
        '''Creates a Python wrapper around native class'''
        ret = ExprString()
        ret._hndl = hndl
        ret._owned = owned
        return ret
    
    cpdef std_string getValue(self):
        return dynamic_cast[pssast_decl.IExprStringP](self._hndl).getValue()
    cpdef bool getIs_raw(self):
        return dynamic_cast[pssast_decl.IExprStringP](self._hndl).getIs_raw()

cdef class ExprSubscript(Expr):
    
    cdef pssast_decl.IExprSubscript *asExprSubscript(self):
        return dynamic_cast[pssast_decl.IExprSubscriptP](self._hndl)
    @staticmethod
    cdef ExprSubscript mk(pssast_decl.IExprSubscript *hndl, bool owned):
        '''Creates a Python wrapper around native class'''
        ret = ExprSubscript()
        ret._hndl = hndl
        ret._owned = owned
        return ret
    

cdef class ExprUnary(Expr):
    
    cdef pssast_decl.IExprUnary *asExprUnary(self):
        return dynamic_cast[pssast_decl.IExprUnaryP](self._hndl)
    @staticmethod
    cdef ExprUnary mk(pssast_decl.IExprUnary *hndl, bool owned):
        '''Creates a Python wrapper around native class'''
        ret = ExprUnary()
        ret._hndl = hndl
        ret._owned = owned
        return ret
    

cdef class MethodParameterList(Expr):
    
    cdef pssast_decl.IMethodParameterList *asMethodParameterList(self):
        return dynamic_cast[pssast_decl.IMethodParameterListP](self._hndl)
    @staticmethod
    cdef MethodParameterList mk(pssast_decl.IMethodParameterList *hndl, bool owned):
        '''Creates a Python wrapper around native class'''
        ret = MethodParameterList()
        ret._hndl = hndl
        ret._owned = owned
        return ret
    

cdef class TypeIdentifier(Expr):
    
    cdef pssast_decl.ITypeIdentifier *asTypeIdentifier(self):
        return dynamic_cast[pssast_decl.ITypeIdentifierP](self._hndl)
    @staticmethod
    cdef TypeIdentifier mk(pssast_decl.ITypeIdentifier *hndl, bool owned):
        '''Creates a Python wrapper around native class'''
        ret = TypeIdentifier()
        ret._hndl = hndl
        ret._owned = owned
        return ret
    

cdef class TypeIdentifierElem(Expr):
    
    cdef pssast_decl.ITypeIdentifierElem *asTypeIdentifierElem(self):
        return dynamic_cast[pssast_decl.ITypeIdentifierElemP](self._hndl)
    @staticmethod
    cdef TypeIdentifierElem mk(pssast_decl.ITypeIdentifierElem *hndl, bool owned):
        '''Creates a Python wrapper around native class'''
        ret = TypeIdentifierElem()
        ret._hndl = hndl
        ret._owned = owned
        return ret
    

cdef class RefExprTypeScopeGlobal(RefExpr):
    
    cdef pssast_decl.IRefExprTypeScopeGlobal *asRefExprTypeScopeGlobal(self):
        return dynamic_cast[pssast_decl.IRefExprTypeScopeGlobalP](self._hndl)
    @staticmethod
    cdef RefExprTypeScopeGlobal mk(pssast_decl.IRefExprTypeScopeGlobal *hndl, bool owned):
        '''Creates a Python wrapper around native class'''
        ret = RefExprTypeScopeGlobal()
        ret._hndl = hndl
        ret._owned = owned
        return ret
    
    cpdef int32_t getFileid(self):
        return dynamic_cast[pssast_decl.IRefExprTypeScopeGlobalP](self._hndl).getFileid()

cdef class RefExprTypeScopeContext(RefExpr):
    
    cdef pssast_decl.IRefExprTypeScopeContext *asRefExprTypeScopeContext(self):
        return dynamic_cast[pssast_decl.IRefExprTypeScopeContextP](self._hndl)
    @staticmethod
    cdef RefExprTypeScopeContext mk(pssast_decl.IRefExprTypeScopeContext *hndl, bool owned):
        '''Creates a Python wrapper around native class'''
        ret = RefExprTypeScopeContext()
        ret._hndl = hndl
        ret._owned = owned
        return ret
    
    cpdef int32_t getOffset(self):
        return dynamic_cast[pssast_decl.IRefExprTypeScopeContextP](self._hndl).getOffset()

cdef class RefExprScopeIndex(RefExpr):
    
    cdef pssast_decl.IRefExprScopeIndex *asRefExprScopeIndex(self):
        return dynamic_cast[pssast_decl.IRefExprScopeIndexP](self._hndl)
    @staticmethod
    cdef RefExprScopeIndex mk(pssast_decl.IRefExprScopeIndex *hndl, bool owned):
        '''Creates a Python wrapper around native class'''
        ret = RefExprScopeIndex()
        ret._hndl = hndl
        ret._owned = owned
        return ret
    
    cpdef int32_t getOffset(self):
        return dynamic_cast[pssast_decl.IRefExprScopeIndexP](self._hndl).getOffset()

cdef class TemplateGenericTypeParamDecl(TemplateParamDecl):
    
    cdef pssast_decl.ITemplateGenericTypeParamDecl *asTemplateGenericTypeParamDecl(self):
        return dynamic_cast[pssast_decl.ITemplateGenericTypeParamDeclP](self._hndl)
    @staticmethod
    cdef TemplateGenericTypeParamDecl mk(pssast_decl.ITemplateGenericTypeParamDecl *hndl, bool owned):
        '''Creates a Python wrapper around native class'''
        ret = TemplateGenericTypeParamDecl()
        ret._hndl = hndl
        ret._owned = owned
        return ret
    

cdef class TemplateCategoryTypeParamDecl(TemplateParamDecl):
    
    cdef pssast_decl.ITemplateCategoryTypeParamDecl *asTemplateCategoryTypeParamDecl(self):
        return dynamic_cast[pssast_decl.ITemplateCategoryTypeParamDeclP](self._hndl)
    @staticmethod
    cdef TemplateCategoryTypeParamDecl mk(pssast_decl.ITemplateCategoryTypeParamDecl *hndl, bool owned):
        '''Creates a Python wrapper around native class'''
        ret = TemplateCategoryTypeParamDecl()
        ret._hndl = hndl
        ret._owned = owned
        return ret
    

cdef class TemplateValueParamDecl(TemplateParamDecl):
    
    cdef pssast_decl.ITemplateValueParamDecl *asTemplateValueParamDecl(self):
        return dynamic_cast[pssast_decl.ITemplateValueParamDeclP](self._hndl)
    @staticmethod
    cdef TemplateValueParamDecl mk(pssast_decl.ITemplateValueParamDecl *hndl, bool owned):
        '''Creates a Python wrapper around native class'''
        ret = TemplateValueParamDecl()
        ret._hndl = hndl
        ret._owned = owned
        return ret
    

cdef class ConstraintBlock(ConstraintStmt):
    
    cdef pssast_decl.IConstraintBlock *asConstraintBlock(self):
        return dynamic_cast[pssast_decl.IConstraintBlockP](self._hndl)
    @staticmethod
    cdef ConstraintBlock mk(pssast_decl.IConstraintBlock *hndl, bool owned):
        '''Creates a Python wrapper around native class'''
        ret = ConstraintBlock()
        ret._hndl = hndl
        ret._owned = owned
        return ret
    
    cpdef std_string getName(self):
        return dynamic_cast[pssast_decl.IConstraintBlockP](self._hndl).getName()
    cpdef bool getIs_dynamic(self):
        return dynamic_cast[pssast_decl.IConstraintBlockP](self._hndl).getIs_dynamic()

cdef class ConstraintScope(ConstraintStmt):
    
    cdef pssast_decl.IConstraintScope *asConstraintScope(self):
        return dynamic_cast[pssast_decl.IConstraintScopeP](self._hndl)
    @staticmethod
    cdef ConstraintScope mk(pssast_decl.IConstraintScope *hndl, bool owned):
        '''Creates a Python wrapper around native class'''
        ret = ConstraintScope()
        ret._hndl = hndl
        ret._owned = owned
        return ret
    

cdef class ConstraintStmtDefault(ConstraintStmt):
    
    cdef pssast_decl.IConstraintStmtDefault *asConstraintStmtDefault(self):
        return dynamic_cast[pssast_decl.IConstraintStmtDefaultP](self._hndl)
    @staticmethod
    cdef ConstraintStmtDefault mk(pssast_decl.IConstraintStmtDefault *hndl, bool owned):
        '''Creates a Python wrapper around native class'''
        ret = ConstraintStmtDefault()
        ret._hndl = hndl
        ret._owned = owned
        return ret
    

cdef class ConstraintStmtDefaultDisable(ConstraintStmt):
    
    cdef pssast_decl.IConstraintStmtDefaultDisable *asConstraintStmtDefaultDisable(self):
        return dynamic_cast[pssast_decl.IConstraintStmtDefaultDisableP](self._hndl)
    @staticmethod
    cdef ConstraintStmtDefaultDisable mk(pssast_decl.IConstraintStmtDefaultDisable *hndl, bool owned):
        '''Creates a Python wrapper around native class'''
        ret = ConstraintStmtDefaultDisable()
        ret._hndl = hndl
        ret._owned = owned
        return ret
    

cdef class ConstraintStmtExpr(ConstraintStmt):
    
    cdef pssast_decl.IConstraintStmtExpr *asConstraintStmtExpr(self):
        return dynamic_cast[pssast_decl.IConstraintStmtExprP](self._hndl)
    @staticmethod
    cdef ConstraintStmtExpr mk(pssast_decl.IConstraintStmtExpr *hndl, bool owned):
        '''Creates a Python wrapper around native class'''
        ret = ConstraintStmtExpr()
        ret._hndl = hndl
        ret._owned = owned
        return ret
    

cdef class ConstraintStmtField(ConstraintStmt):
    
    cdef pssast_decl.IConstraintStmtField *asConstraintStmtField(self):
        return dynamic_cast[pssast_decl.IConstraintStmtFieldP](self._hndl)
    @staticmethod
    cdef ConstraintStmtField mk(pssast_decl.IConstraintStmtField *hndl, bool owned):
        '''Creates a Python wrapper around native class'''
        ret = ConstraintStmtField()
        ret._hndl = hndl
        ret._owned = owned
        return ret
    

cdef class ConstraintStmtIf(ConstraintStmt):
    
    cdef pssast_decl.IConstraintStmtIf *asConstraintStmtIf(self):
        return dynamic_cast[pssast_decl.IConstraintStmtIfP](self._hndl)
    @staticmethod
    cdef ConstraintStmtIf mk(pssast_decl.IConstraintStmtIf *hndl, bool owned):
        '''Creates a Python wrapper around native class'''
        ret = ConstraintStmtIf()
        ret._hndl = hndl
        ret._owned = owned
        return ret
    

cdef class ConstraintStmtUnique(ConstraintStmt):
    
    cdef pssast_decl.IConstraintStmtUnique *asConstraintStmtUnique(self):
        return dynamic_cast[pssast_decl.IConstraintStmtUniqueP](self._hndl)
    @staticmethod
    cdef ConstraintStmtUnique mk(pssast_decl.IConstraintStmtUnique *hndl, bool owned):
        '''Creates a Python wrapper around native class'''
        ret = ConstraintStmtUnique()
        ret._hndl = hndl
        ret._owned = owned
        return ret
    

cdef class GlobalScope(Scope):
    
    cdef pssast_decl.IGlobalScope *asGlobalScope(self):
        return dynamic_cast[pssast_decl.IGlobalScopeP](self._hndl)
    @staticmethod
    cdef GlobalScope mk(pssast_decl.IGlobalScope *hndl, bool owned):
        '''Creates a Python wrapper around native class'''
        ret = GlobalScope()
        ret._hndl = hndl
        ret._owned = owned
        return ret
    
    cpdef int32_t getFileid(self):
        return dynamic_cast[pssast_decl.IGlobalScopeP](self._hndl).getFileid()

cdef class NamedScope(Scope):
    
    cdef pssast_decl.INamedScope *asNamedScope(self):
        return dynamic_cast[pssast_decl.INamedScopeP](self._hndl)
    @staticmethod
    cdef NamedScope mk(pssast_decl.INamedScope *hndl, bool owned):
        '''Creates a Python wrapper around native class'''
        ret = NamedScope()
        ret._hndl = hndl
        ret._owned = owned
        return ret
    

cdef class PackageScope(Scope):
    
    cdef pssast_decl.IPackageScope *asPackageScope(self):
        return dynamic_cast[pssast_decl.IPackageScopeP](self._hndl)
    @staticmethod
    cdef PackageScope mk(pssast_decl.IPackageScope *hndl, bool owned):
        '''Creates a Python wrapper around native class'''
        ret = PackageScope()
        ret._hndl = hndl
        ret._owned = owned
        return ret
    

cdef class DataTypeArray(DataType):
    
    cdef pssast_decl.IDataTypeArray *asDataTypeArray(self):
        return dynamic_cast[pssast_decl.IDataTypeArrayP](self._hndl)
    @staticmethod
    cdef DataTypeArray mk(pssast_decl.IDataTypeArray *hndl, bool owned):
        '''Creates a Python wrapper around native class'''
        ret = DataTypeArray()
        ret._hndl = hndl
        ret._owned = owned
        return ret
    

cdef class DataTypeBool(DataType):
    
    cdef pssast_decl.IDataTypeBool *asDataTypeBool(self):
        return dynamic_cast[pssast_decl.IDataTypeBoolP](self._hndl)
    @staticmethod
    cdef DataTypeBool mk(pssast_decl.IDataTypeBool *hndl, bool owned):
        '''Creates a Python wrapper around native class'''
        ret = DataTypeBool()
        ret._hndl = hndl
        ret._owned = owned
        return ret
    

cdef class DataTypeChandle(DataType):
    
    cdef pssast_decl.IDataTypeChandle *asDataTypeChandle(self):
        return dynamic_cast[pssast_decl.IDataTypeChandleP](self._hndl)
    @staticmethod
    cdef DataTypeChandle mk(pssast_decl.IDataTypeChandle *hndl, bool owned):
        '''Creates a Python wrapper around native class'''
        ret = DataTypeChandle()
        ret._hndl = hndl
        ret._owned = owned
        return ret
    

cdef class DataTypeEnum(DataType):
    
    cdef pssast_decl.IDataTypeEnum *asDataTypeEnum(self):
        return dynamic_cast[pssast_decl.IDataTypeEnumP](self._hndl)
    @staticmethod
    cdef DataTypeEnum mk(pssast_decl.IDataTypeEnum *hndl, bool owned):
        '''Creates a Python wrapper around native class'''
        ret = DataTypeEnum()
        ret._hndl = hndl
        ret._owned = owned
        return ret
    

cdef class DataTypeInt(DataType):
    
    cdef pssast_decl.IDataTypeInt *asDataTypeInt(self):
        return dynamic_cast[pssast_decl.IDataTypeIntP](self._hndl)
    @staticmethod
    cdef DataTypeInt mk(pssast_decl.IDataTypeInt *hndl, bool owned):
        '''Creates a Python wrapper around native class'''
        ret = DataTypeInt()
        ret._hndl = hndl
        ret._owned = owned
        return ret
    
    cpdef bool getIs_signed(self):
        return dynamic_cast[pssast_decl.IDataTypeIntP](self._hndl).getIs_signed()

cdef class DataTypeString(DataType):
    
    cdef pssast_decl.IDataTypeString *asDataTypeString(self):
        return dynamic_cast[pssast_decl.IDataTypeStringP](self._hndl)
    @staticmethod
    cdef DataTypeString mk(pssast_decl.IDataTypeString *hndl, bool owned):
        '''Creates a Python wrapper around native class'''
        ret = DataTypeString()
        ret._hndl = hndl
        ret._owned = owned
        return ret
    
    cpdef bool getHas_range(self):
        return dynamic_cast[pssast_decl.IDataTypeStringP](self._hndl).getHas_range()

cdef class DataTypeUserDefined(DataType):
    
    cdef pssast_decl.IDataTypeUserDefined *asDataTypeUserDefined(self):
        return dynamic_cast[pssast_decl.IDataTypeUserDefinedP](self._hndl)
    @staticmethod
    cdef DataTypeUserDefined mk(pssast_decl.IDataTypeUserDefined *hndl, bool owned):
        '''Creates a Python wrapper around native class'''
        ret = DataTypeUserDefined()
        ret._hndl = hndl
        ret._owned = owned
        return ret
    
    cpdef bool getIs_global(self):
        return dynamic_cast[pssast_decl.IDataTypeUserDefinedP](self._hndl).getIs_global()

cdef class ExprRefPathContext(ExprRefPath):
    
    cdef pssast_decl.IExprRefPathContext *asExprRefPathContext(self):
        return dynamic_cast[pssast_decl.IExprRefPathContextP](self._hndl)
    @staticmethod
    cdef ExprRefPathContext mk(pssast_decl.IExprRefPathContext *hndl, bool owned):
        '''Creates a Python wrapper around native class'''
        ret = ExprRefPathContext()
        ret._hndl = hndl
        ret._owned = owned
        return ret
    

cdef class ExprRefPathStatic(ExprRefPath):
    
    cdef pssast_decl.IExprRefPathStatic *asExprRefPathStatic(self):
        return dynamic_cast[pssast_decl.IExprRefPathStaticP](self._hndl)
    @staticmethod
    cdef ExprRefPathStatic mk(pssast_decl.IExprRefPathStatic *hndl, bool owned):
        '''Creates a Python wrapper around native class'''
        ret = ExprRefPathStatic()
        ret._hndl = hndl
        ret._owned = owned
        return ret
    
    cpdef bool getIs_global(self):
        return dynamic_cast[pssast_decl.IExprRefPathStaticP](self._hndl).getIs_global()

cdef class ExprSignedNumber(ExprNumber):
    
    cdef pssast_decl.IExprSignedNumber *asExprSignedNumber(self):
        return dynamic_cast[pssast_decl.IExprSignedNumberP](self._hndl)
    @staticmethod
    cdef ExprSignedNumber mk(pssast_decl.IExprSignedNumber *hndl, bool owned):
        '''Creates a Python wrapper around native class'''
        ret = ExprSignedNumber()
        ret._hndl = hndl
        ret._owned = owned
        return ret
    
    cpdef std_string getImage(self):
        return dynamic_cast[pssast_decl.IExprSignedNumberP](self._hndl).getImage()
    cpdef uint32_t getWidth(self):
        return dynamic_cast[pssast_decl.IExprSignedNumberP](self._hndl).getWidth()
    cpdef int64_t getValue(self):
        return dynamic_cast[pssast_decl.IExprSignedNumberP](self._hndl).getValue()

cdef class ExprUnsignedNumber(ExprNumber):
    
    cdef pssast_decl.IExprUnsignedNumber *asExprUnsignedNumber(self):
        return dynamic_cast[pssast_decl.IExprUnsignedNumberP](self._hndl)
    @staticmethod
    cdef ExprUnsignedNumber mk(pssast_decl.IExprUnsignedNumber *hndl, bool owned):
        '''Creates a Python wrapper around native class'''
        ret = ExprUnsignedNumber()
        ret._hndl = hndl
        ret._owned = owned
        return ret
    
    cpdef std_string getImage(self):
        return dynamic_cast[pssast_decl.IExprUnsignedNumberP](self._hndl).getImage()
    cpdef uint32_t getWidth(self):
        return dynamic_cast[pssast_decl.IExprUnsignedNumberP](self._hndl).getWidth()
    cpdef uint64_t getValue(self):
        return dynamic_cast[pssast_decl.IExprUnsignedNumberP](self._hndl).getValue()

cdef class ConstraintStmtForall(ConstraintScope):
    
    cdef pssast_decl.IConstraintStmtForall *asConstraintStmtForall(self):
        return dynamic_cast[pssast_decl.IConstraintStmtForallP](self._hndl)
    @staticmethod
    cdef ConstraintStmtForall mk(pssast_decl.IConstraintStmtForall *hndl, bool owned):
        '''Creates a Python wrapper around native class'''
        ret = ConstraintStmtForall()
        ret._hndl = hndl
        ret._owned = owned
        return ret
    

cdef class ConstraintStmtForeach(ConstraintScope):
    
    cdef pssast_decl.IConstraintStmtForeach *asConstraintStmtForeach(self):
        return dynamic_cast[pssast_decl.IConstraintStmtForeachP](self._hndl)
    @staticmethod
    cdef ConstraintStmtForeach mk(pssast_decl.IConstraintStmtForeach *hndl, bool owned):
        '''Creates a Python wrapper around native class'''
        ret = ConstraintStmtForeach()
        ret._hndl = hndl
        ret._owned = owned
        return ret
    

cdef class ConstraintStmtImplication(ConstraintScope):
    
    cdef pssast_decl.IConstraintStmtImplication *asConstraintStmtImplication(self):
        return dynamic_cast[pssast_decl.IConstraintStmtImplicationP](self._hndl)
    @staticmethod
    cdef ConstraintStmtImplication mk(pssast_decl.IConstraintStmtImplication *hndl, bool owned):
        '''Creates a Python wrapper around native class'''
        ret = ConstraintStmtImplication()
        ret._hndl = hndl
        ret._owned = owned
        return ret
    

cdef class TypeScope(NamedScope):
    
    cdef pssast_decl.ITypeScope *asTypeScope(self):
        return dynamic_cast[pssast_decl.ITypeScopeP](self._hndl)
    @staticmethod
    cdef TypeScope mk(pssast_decl.ITypeScope *hndl, bool owned):
        '''Creates a Python wrapper around native class'''
        ret = TypeScope()
        ret._hndl = hndl
        ret._owned = owned
        return ret
    

cdef class ExprRefPathStaticFunc(ExprRefPathStatic):
    
    cdef pssast_decl.IExprRefPathStaticFunc *asExprRefPathStaticFunc(self):
        return dynamic_cast[pssast_decl.IExprRefPathStaticFuncP](self._hndl)
    @staticmethod
    cdef ExprRefPathStaticFunc mk(pssast_decl.IExprRefPathStaticFunc *hndl, bool owned):
        '''Creates a Python wrapper around native class'''
        ret = ExprRefPathStaticFunc()
        ret._hndl = hndl
        ret._owned = owned
        return ret
    

cdef class ExprRefPathSuper(ExprRefPathContext):
    
    cdef pssast_decl.IExprRefPathSuper *asExprRefPathSuper(self):
        return dynamic_cast[pssast_decl.IExprRefPathSuperP](self._hndl)
    @staticmethod
    cdef ExprRefPathSuper mk(pssast_decl.IExprRefPathSuper *hndl, bool owned):
        '''Creates a Python wrapper around native class'''
        ret = ExprRefPathSuper()
        ret._hndl = hndl
        ret._owned = owned
        return ret
    

cdef class Action(TypeScope):
    
    cdef pssast_decl.IAction *asAction(self):
        return dynamic_cast[pssast_decl.IActionP](self._hndl)
    @staticmethod
    cdef Action mk(pssast_decl.IAction *hndl, bool owned):
        '''Creates a Python wrapper around native class'''
        ret = Action()
        ret._hndl = hndl
        ret._owned = owned
        return ret
    
    cpdef bool getIs_abstract(self):
        return dynamic_cast[pssast_decl.IActionP](self._hndl).getIs_abstract()

cdef class Component(TypeScope):
    
    cdef pssast_decl.IComponent *asComponent(self):
        return dynamic_cast[pssast_decl.IComponentP](self._hndl)
    @staticmethod
    cdef Component mk(pssast_decl.IComponent *hndl, bool owned):
        '''Creates a Python wrapper around native class'''
        ret = Component()
        ret._hndl = hndl
        ret._owned = owned
        return ret
    

cdef class Struct(TypeScope):
    
    cdef pssast_decl.IStruct *asStruct(self):
        return dynamic_cast[pssast_decl.IStructP](self._hndl)
    @staticmethod
    cdef Struct mk(pssast_decl.IStruct *hndl, bool owned):
        '''Creates a Python wrapper around native class'''
        ret = Struct()
        ret._hndl = hndl
        ret._owned = owned
        return ret
    

cdef class State(Struct):
    
    cdef pssast_decl.IState *asState(self):
        return dynamic_cast[pssast_decl.IStateP](self._hndl)
    @staticmethod
    cdef State mk(pssast_decl.IState *hndl, bool owned):
        '''Creates a Python wrapper around native class'''
        ret = State()
        ret._hndl = hndl
        ret._owned = owned
        return ret
    

cdef class Stream(Struct):
    
    cdef pssast_decl.IStream *asStream(self):
        return dynamic_cast[pssast_decl.IStreamP](self._hndl)
    @staticmethod
    cdef Stream mk(pssast_decl.IStream *hndl, bool owned):
        '''Creates a Python wrapper around native class'''
        ret = Stream()
        ret._hndl = hndl
        ret._owned = owned
        return ret
    

cdef class Buffer(Struct):
    
    cdef pssast_decl.IBuffer *asBuffer(self):
        return dynamic_cast[pssast_decl.IBufferP](self._hndl)
    @staticmethod
    cdef Buffer mk(pssast_decl.IBuffer *hndl, bool owned):
        '''Creates a Python wrapper around native class'''
        ret = Buffer()
        ret._hndl = hndl
        ret._owned = owned
        return ret
    

cdef class Resource(Struct):
    
    cdef pssast_decl.IResource *asResource(self):
        return dynamic_cast[pssast_decl.IResourceP](self._hndl)
    @staticmethod
    cdef Resource mk(pssast_decl.IResource *hndl, bool owned):
        '''Creates a Python wrapper around native class'''
        ret = Resource()
        ret._hndl = hndl
        ret._owned = owned
        return ret
    

cdef class VisitorBase(object):
    def __cinit__(self):
        self._hndl = new pssast_decl.PyBaseVisitor(<cpy_ref.PyObject*>self)
    cpdef void visitExecStmt(self, ExecStmt i):
        self._hndl.py_visitExecStmt(dynamic_cast[pssast_decl.IExecStmtP](i._hndl));
    cpdef void visitExpr(self, Expr i):
        self._hndl.py_visitExpr(dynamic_cast[pssast_decl.IExprP](i._hndl));
    cpdef void visitRefExpr(self, RefExpr i):
        self._hndl.py_visitRefExpr(dynamic_cast[pssast_decl.IRefExprP](i._hndl));
    cpdef void visitTemplateParamDeclList(self, TemplateParamDeclList i):
        self._hndl.py_visitTemplateParamDeclList(dynamic_cast[pssast_decl.ITemplateParamDeclListP](i._hndl));
    cpdef void visitTemplateParamDecl(self, TemplateParamDecl i):
        self._hndl.py_visitTemplateParamDecl(dynamic_cast[pssast_decl.ITemplateParamDeclP](i._hndl));
    cpdef void visitScopeChild(self, ScopeChild i):
        self._hndl.py_visitScopeChild(dynamic_cast[pssast_decl.IScopeChildP](i._hndl));
    cpdef void visitTemplateParamValueList(self, TemplateParamValueList i):
        self._hndl.py_visitTemplateParamValueList(dynamic_cast[pssast_decl.ITemplateParamValueListP](i._hndl));
    cpdef void visitTemplateParamValue(self, TemplateParamValue i):
        self._hndl.py_visitTemplateParamValue(dynamic_cast[pssast_decl.ITemplateParamValueP](i._hndl));
    cpdef void visitTemplateParamTypeValue(self, TemplateParamTypeValue i):
        self._hndl.py_visitTemplateParamTypeValue(dynamic_cast[pssast_decl.ITemplateParamTypeValueP](i._hndl));
    cpdef void visitTemplateParamExprValue(self, TemplateParamExprValue i):
        self._hndl.py_visitTemplateParamExprValue(dynamic_cast[pssast_decl.ITemplateParamExprValueP](i._hndl));
    cpdef void visitConstraintStmt(self, ConstraintStmt i):
        self._hndl.py_visitConstraintStmt(dynamic_cast[pssast_decl.IConstraintStmtP](i._hndl));
    cpdef void visitScope(self, Scope i):
        self._hndl.py_visitScope(dynamic_cast[pssast_decl.IScopeP](i._hndl));
    cpdef void visitNamedScopeChild(self, NamedScopeChild i):
        self._hndl.py_visitNamedScopeChild(dynamic_cast[pssast_decl.INamedScopeChildP](i._hndl));
    cpdef void visitPackageImportStmt(self, PackageImportStmt i):
        self._hndl.py_visitPackageImportStmt(dynamic_cast[pssast_decl.IPackageImportStmtP](i._hndl));
    cpdef void visitDataType(self, DataType i):
        self._hndl.py_visitDataType(dynamic_cast[pssast_decl.IDataTypeP](i._hndl));
    cpdef void visitExecScope(self, ExecScope i):
        self._hndl.py_visitExecScope(dynamic_cast[pssast_decl.IExecScopeP](i._hndl));
    cpdef void visitProceduralStmtDataDeclaration(self, ProceduralStmtDataDeclaration i):
        self._hndl.py_visitProceduralStmtDataDeclaration(dynamic_cast[pssast_decl.IProceduralStmtDataDeclarationP](i._hndl));
    cpdef void visitExprBin(self, ExprBin i):
        self._hndl.py_visitExprBin(dynamic_cast[pssast_decl.IExprBinP](i._hndl));
    cpdef void visitExprBitSlice(self, ExprBitSlice i):
        self._hndl.py_visitExprBitSlice(dynamic_cast[pssast_decl.IExprBitSliceP](i._hndl));
    cpdef void visitExprBool(self, ExprBool i):
        self._hndl.py_visitExprBool(dynamic_cast[pssast_decl.IExprBoolP](i._hndl));
    cpdef void visitExprCast(self, ExprCast i):
        self._hndl.py_visitExprCast(dynamic_cast[pssast_decl.IExprCastP](i._hndl));
    cpdef void visitExprCompileHas(self, ExprCompileHas i):
        self._hndl.py_visitExprCompileHas(dynamic_cast[pssast_decl.IExprCompileHasP](i._hndl));
    cpdef void visitExprCond(self, ExprCond i):
        self._hndl.py_visitExprCond(dynamic_cast[pssast_decl.IExprCondP](i._hndl));
    cpdef void visitExprDomainOpenRangeList(self, ExprDomainOpenRangeList i):
        self._hndl.py_visitExprDomainOpenRangeList(dynamic_cast[pssast_decl.IExprDomainOpenRangeListP](i._hndl));
    cpdef void visitExprDomainOpenRangeValue(self, ExprDomainOpenRangeValue i):
        self._hndl.py_visitExprDomainOpenRangeValue(dynamic_cast[pssast_decl.IExprDomainOpenRangeValueP](i._hndl));
    cpdef void visitExprHierarchicalId(self, ExprHierarchicalId i):
        self._hndl.py_visitExprHierarchicalId(dynamic_cast[pssast_decl.IExprHierarchicalIdP](i._hndl));
    cpdef void visitExprId(self, ExprId i):
        self._hndl.py_visitExprId(dynamic_cast[pssast_decl.IExprIdP](i._hndl));
    cpdef void visitExprIn(self, ExprIn i):
        self._hndl.py_visitExprIn(dynamic_cast[pssast_decl.IExprInP](i._hndl));
    cpdef void visitExprMemberPathElem(self, ExprMemberPathElem i):
        self._hndl.py_visitExprMemberPathElem(dynamic_cast[pssast_decl.IExprMemberPathElemP](i._hndl));
    cpdef void visitExprNumber(self, ExprNumber i):
        self._hndl.py_visitExprNumber(dynamic_cast[pssast_decl.IExprNumberP](i._hndl));
    cpdef void visitExprAggregateLiteral(self, ExprAggregateLiteral i):
        self._hndl.py_visitExprAggregateLiteral(dynamic_cast[pssast_decl.IExprAggregateLiteralP](i._hndl));
    cpdef void visitExprOpenRangeList(self, ExprOpenRangeList i):
        self._hndl.py_visitExprOpenRangeList(dynamic_cast[pssast_decl.IExprOpenRangeListP](i._hndl));
    cpdef void visitExprOpenRangeValue(self, ExprOpenRangeValue i):
        self._hndl.py_visitExprOpenRangeValue(dynamic_cast[pssast_decl.IExprOpenRangeValueP](i._hndl));
    cpdef void visitExprRefPath(self, ExprRefPath i):
        self._hndl.py_visitExprRefPath(dynamic_cast[pssast_decl.IExprRefPathP](i._hndl));
    cpdef void visitExprRefPathElem(self, ExprRefPathElem i):
        self._hndl.py_visitExprRefPathElem(dynamic_cast[pssast_decl.IExprRefPathElemP](i._hndl));
    cpdef void visitExprRefPathStaticRooted(self, ExprRefPathStaticRooted i):
        self._hndl.py_visitExprRefPathStaticRooted(dynamic_cast[pssast_decl.IExprRefPathStaticRootedP](i._hndl));
    cpdef void visitExprStaticRefPath(self, ExprStaticRefPath i):
        self._hndl.py_visitExprStaticRefPath(dynamic_cast[pssast_decl.IExprStaticRefPathP](i._hndl));
    cpdef void visitExprString(self, ExprString i):
        self._hndl.py_visitExprString(dynamic_cast[pssast_decl.IExprStringP](i._hndl));
    cpdef void visitExprSubscript(self, ExprSubscript i):
        self._hndl.py_visitExprSubscript(dynamic_cast[pssast_decl.IExprSubscriptP](i._hndl));
    cpdef void visitExprUnary(self, ExprUnary i):
        self._hndl.py_visitExprUnary(dynamic_cast[pssast_decl.IExprUnaryP](i._hndl));
    cpdef void visitMethodParameterList(self, MethodParameterList i):
        self._hndl.py_visitMethodParameterList(dynamic_cast[pssast_decl.IMethodParameterListP](i._hndl));
    cpdef void visitTypeIdentifier(self, TypeIdentifier i):
        self._hndl.py_visitTypeIdentifier(dynamic_cast[pssast_decl.ITypeIdentifierP](i._hndl));
    cpdef void visitTypeIdentifierElem(self, TypeIdentifierElem i):
        self._hndl.py_visitTypeIdentifierElem(dynamic_cast[pssast_decl.ITypeIdentifierElemP](i._hndl));
    cpdef void visitRefExprTypeScopeGlobal(self, RefExprTypeScopeGlobal i):
        self._hndl.py_visitRefExprTypeScopeGlobal(dynamic_cast[pssast_decl.IRefExprTypeScopeGlobalP](i._hndl));
    cpdef void visitRefExprTypeScopeContext(self, RefExprTypeScopeContext i):
        self._hndl.py_visitRefExprTypeScopeContext(dynamic_cast[pssast_decl.IRefExprTypeScopeContextP](i._hndl));
    cpdef void visitRefExprScopeIndex(self, RefExprScopeIndex i):
        self._hndl.py_visitRefExprScopeIndex(dynamic_cast[pssast_decl.IRefExprScopeIndexP](i._hndl));
    cpdef void visitTemplateGenericTypeParamDecl(self, TemplateGenericTypeParamDecl i):
        self._hndl.py_visitTemplateGenericTypeParamDecl(dynamic_cast[pssast_decl.ITemplateGenericTypeParamDeclP](i._hndl));
    cpdef void visitTemplateCategoryTypeParamDecl(self, TemplateCategoryTypeParamDecl i):
        self._hndl.py_visitTemplateCategoryTypeParamDecl(dynamic_cast[pssast_decl.ITemplateCategoryTypeParamDeclP](i._hndl));
    cpdef void visitTemplateValueParamDecl(self, TemplateValueParamDecl i):
        self._hndl.py_visitTemplateValueParamDecl(dynamic_cast[pssast_decl.ITemplateValueParamDeclP](i._hndl));
    cpdef void visitConstraintBlock(self, ConstraintBlock i):
        self._hndl.py_visitConstraintBlock(dynamic_cast[pssast_decl.IConstraintBlockP](i._hndl));
    cpdef void visitConstraintScope(self, ConstraintScope i):
        self._hndl.py_visitConstraintScope(dynamic_cast[pssast_decl.IConstraintScopeP](i._hndl));
    cpdef void visitConstraintStmtDefault(self, ConstraintStmtDefault i):
        self._hndl.py_visitConstraintStmtDefault(dynamic_cast[pssast_decl.IConstraintStmtDefaultP](i._hndl));
    cpdef void visitConstraintStmtDefaultDisable(self, ConstraintStmtDefaultDisable i):
        self._hndl.py_visitConstraintStmtDefaultDisable(dynamic_cast[pssast_decl.IConstraintStmtDefaultDisableP](i._hndl));
    cpdef void visitConstraintStmtExpr(self, ConstraintStmtExpr i):
        self._hndl.py_visitConstraintStmtExpr(dynamic_cast[pssast_decl.IConstraintStmtExprP](i._hndl));
    cpdef void visitConstraintStmtField(self, ConstraintStmtField i):
        self._hndl.py_visitConstraintStmtField(dynamic_cast[pssast_decl.IConstraintStmtFieldP](i._hndl));
    cpdef void visitConstraintStmtIf(self, ConstraintStmtIf i):
        self._hndl.py_visitConstraintStmtIf(dynamic_cast[pssast_decl.IConstraintStmtIfP](i._hndl));
    cpdef void visitConstraintStmtUnique(self, ConstraintStmtUnique i):
        self._hndl.py_visitConstraintStmtUnique(dynamic_cast[pssast_decl.IConstraintStmtUniqueP](i._hndl));
    cpdef void visitGlobalScope(self, GlobalScope i):
        self._hndl.py_visitGlobalScope(dynamic_cast[pssast_decl.IGlobalScopeP](i._hndl));
    cpdef void visitNamedScope(self, NamedScope i):
        self._hndl.py_visitNamedScope(dynamic_cast[pssast_decl.INamedScopeP](i._hndl));
    cpdef void visitPackageScope(self, PackageScope i):
        self._hndl.py_visitPackageScope(dynamic_cast[pssast_decl.IPackageScopeP](i._hndl));
    cpdef void visitDataTypeArray(self, DataTypeArray i):
        self._hndl.py_visitDataTypeArray(dynamic_cast[pssast_decl.IDataTypeArrayP](i._hndl));
    cpdef void visitDataTypeBool(self, DataTypeBool i):
        self._hndl.py_visitDataTypeBool(dynamic_cast[pssast_decl.IDataTypeBoolP](i._hndl));
    cpdef void visitDataTypeChandle(self, DataTypeChandle i):
        self._hndl.py_visitDataTypeChandle(dynamic_cast[pssast_decl.IDataTypeChandleP](i._hndl));
    cpdef void visitDataTypeEnum(self, DataTypeEnum i):
        self._hndl.py_visitDataTypeEnum(dynamic_cast[pssast_decl.IDataTypeEnumP](i._hndl));
    cpdef void visitDataTypeInt(self, DataTypeInt i):
        self._hndl.py_visitDataTypeInt(dynamic_cast[pssast_decl.IDataTypeIntP](i._hndl));
    cpdef void visitDataTypeString(self, DataTypeString i):
        self._hndl.py_visitDataTypeString(dynamic_cast[pssast_decl.IDataTypeStringP](i._hndl));
    cpdef void visitDataTypeUserDefined(self, DataTypeUserDefined i):
        self._hndl.py_visitDataTypeUserDefined(dynamic_cast[pssast_decl.IDataTypeUserDefinedP](i._hndl));
    cpdef void visitExprRefPathContext(self, ExprRefPathContext i):
        self._hndl.py_visitExprRefPathContext(dynamic_cast[pssast_decl.IExprRefPathContextP](i._hndl));
    cpdef void visitExprRefPathStatic(self, ExprRefPathStatic i):
        self._hndl.py_visitExprRefPathStatic(dynamic_cast[pssast_decl.IExprRefPathStaticP](i._hndl));
    cpdef void visitExprSignedNumber(self, ExprSignedNumber i):
        self._hndl.py_visitExprSignedNumber(dynamic_cast[pssast_decl.IExprSignedNumberP](i._hndl));
    cpdef void visitExprUnsignedNumber(self, ExprUnsignedNumber i):
        self._hndl.py_visitExprUnsignedNumber(dynamic_cast[pssast_decl.IExprUnsignedNumberP](i._hndl));
    cpdef void visitConstraintStmtForall(self, ConstraintStmtForall i):
        self._hndl.py_visitConstraintStmtForall(dynamic_cast[pssast_decl.IConstraintStmtForallP](i._hndl));
    cpdef void visitConstraintStmtForeach(self, ConstraintStmtForeach i):
        self._hndl.py_visitConstraintStmtForeach(dynamic_cast[pssast_decl.IConstraintStmtForeachP](i._hndl));
    cpdef void visitConstraintStmtImplication(self, ConstraintStmtImplication i):
        self._hndl.py_visitConstraintStmtImplication(dynamic_cast[pssast_decl.IConstraintStmtImplicationP](i._hndl));
    cpdef void visitTypeScope(self, TypeScope i):
        self._hndl.py_visitTypeScope(dynamic_cast[pssast_decl.ITypeScopeP](i._hndl));
    cpdef void visitExprRefPathStaticFunc(self, ExprRefPathStaticFunc i):
        self._hndl.py_visitExprRefPathStaticFunc(dynamic_cast[pssast_decl.IExprRefPathStaticFuncP](i._hndl));
    cpdef void visitExprRefPathSuper(self, ExprRefPathSuper i):
        self._hndl.py_visitExprRefPathSuper(dynamic_cast[pssast_decl.IExprRefPathSuperP](i._hndl));
    cpdef void visitAction(self, Action i):
        self._hndl.py_visitAction(dynamic_cast[pssast_decl.IActionP](i._hndl));
    cpdef void visitComponent(self, Component i):
        self._hndl.py_visitComponent(dynamic_cast[pssast_decl.IComponentP](i._hndl));
    cpdef void visitStruct(self, Struct i):
        self._hndl.py_visitStruct(dynamic_cast[pssast_decl.IStructP](i._hndl));
    cpdef void visitState(self, State i):
        self._hndl.py_visitState(dynamic_cast[pssast_decl.IStateP](i._hndl));
    cpdef void visitStream(self, Stream i):
        self._hndl.py_visitStream(dynamic_cast[pssast_decl.IStreamP](i._hndl));
    cpdef void visitBuffer(self, Buffer i):
        self._hndl.py_visitBuffer(dynamic_cast[pssast_decl.IBufferP](i._hndl));
    cpdef void visitResource(self, Resource i):
        self._hndl.py_visitResource(dynamic_cast[pssast_decl.IResourceP](i._hndl));
cdef public api pssast_call_visitExecStmt(object self, pssast_decl.IExecStmt *i) with gil:
    self.visitExecStmt(ExecStmt.mk(i, False))
cdef public api pssast_call_visitExpr(object self, pssast_decl.IExpr *i) with gil:
    self.visitExpr(Expr.mk(i, False))
cdef public api pssast_call_visitRefExpr(object self, pssast_decl.IRefExpr *i) with gil:
    self.visitRefExpr(RefExpr.mk(i, False))
cdef public api pssast_call_visitTemplateParamDeclList(object self, pssast_decl.ITemplateParamDeclList *i) with gil:
    self.visitTemplateParamDeclList(TemplateParamDeclList.mk(i, False))
cdef public api pssast_call_visitTemplateParamDecl(object self, pssast_decl.ITemplateParamDecl *i) with gil:
    self.visitTemplateParamDecl(TemplateParamDecl.mk(i, False))
cdef public api pssast_call_visitScopeChild(object self, pssast_decl.IScopeChild *i) with gil:
    self.visitScopeChild(ScopeChild.mk(i, False))
cdef public api pssast_call_visitTemplateParamValueList(object self, pssast_decl.ITemplateParamValueList *i) with gil:
    self.visitTemplateParamValueList(TemplateParamValueList.mk(i, False))
cdef public api pssast_call_visitTemplateParamValue(object self, pssast_decl.ITemplateParamValue *i) with gil:
    self.visitTemplateParamValue(TemplateParamValue.mk(i, False))
cdef public api pssast_call_visitTemplateParamTypeValue(object self, pssast_decl.ITemplateParamTypeValue *i) with gil:
    self.visitTemplateParamTypeValue(TemplateParamTypeValue.mk(i, False))
cdef public api pssast_call_visitTemplateParamExprValue(object self, pssast_decl.ITemplateParamExprValue *i) with gil:
    self.visitTemplateParamExprValue(TemplateParamExprValue.mk(i, False))
cdef public api pssast_call_visitConstraintStmt(object self, pssast_decl.IConstraintStmt *i) with gil:
    self.visitConstraintStmt(ConstraintStmt.mk(i, False))
cdef public api pssast_call_visitScope(object self, pssast_decl.IScope *i) with gil:
    self.visitScope(Scope.mk(i, False))
cdef public api pssast_call_visitNamedScopeChild(object self, pssast_decl.INamedScopeChild *i) with gil:
    self.visitNamedScopeChild(NamedScopeChild.mk(i, False))
cdef public api pssast_call_visitPackageImportStmt(object self, pssast_decl.IPackageImportStmt *i) with gil:
    self.visitPackageImportStmt(PackageImportStmt.mk(i, False))
cdef public api pssast_call_visitDataType(object self, pssast_decl.IDataType *i) with gil:
    self.visitDataType(DataType.mk(i, False))
cdef public api pssast_call_visitExecScope(object self, pssast_decl.IExecScope *i) with gil:
    self.visitExecScope(ExecScope.mk(i, False))
cdef public api pssast_call_visitProceduralStmtDataDeclaration(object self, pssast_decl.IProceduralStmtDataDeclaration *i) with gil:
    self.visitProceduralStmtDataDeclaration(ProceduralStmtDataDeclaration.mk(i, False))
cdef public api pssast_call_visitExprBin(object self, pssast_decl.IExprBin *i) with gil:
    self.visitExprBin(ExprBin.mk(i, False))
cdef public api pssast_call_visitExprBitSlice(object self, pssast_decl.IExprBitSlice *i) with gil:
    self.visitExprBitSlice(ExprBitSlice.mk(i, False))
cdef public api pssast_call_visitExprBool(object self, pssast_decl.IExprBool *i) with gil:
    self.visitExprBool(ExprBool.mk(i, False))
cdef public api pssast_call_visitExprCast(object self, pssast_decl.IExprCast *i) with gil:
    self.visitExprCast(ExprCast.mk(i, False))
cdef public api pssast_call_visitExprCompileHas(object self, pssast_decl.IExprCompileHas *i) with gil:
    self.visitExprCompileHas(ExprCompileHas.mk(i, False))
cdef public api pssast_call_visitExprCond(object self, pssast_decl.IExprCond *i) with gil:
    self.visitExprCond(ExprCond.mk(i, False))
cdef public api pssast_call_visitExprDomainOpenRangeList(object self, pssast_decl.IExprDomainOpenRangeList *i) with gil:
    self.visitExprDomainOpenRangeList(ExprDomainOpenRangeList.mk(i, False))
cdef public api pssast_call_visitExprDomainOpenRangeValue(object self, pssast_decl.IExprDomainOpenRangeValue *i) with gil:
    self.visitExprDomainOpenRangeValue(ExprDomainOpenRangeValue.mk(i, False))
cdef public api pssast_call_visitExprHierarchicalId(object self, pssast_decl.IExprHierarchicalId *i) with gil:
    self.visitExprHierarchicalId(ExprHierarchicalId.mk(i, False))
cdef public api pssast_call_visitExprId(object self, pssast_decl.IExprId *i) with gil:
    self.visitExprId(ExprId.mk(i, False))
cdef public api pssast_call_visitExprIn(object self, pssast_decl.IExprIn *i) with gil:
    self.visitExprIn(ExprIn.mk(i, False))
cdef public api pssast_call_visitExprMemberPathElem(object self, pssast_decl.IExprMemberPathElem *i) with gil:
    self.visitExprMemberPathElem(ExprMemberPathElem.mk(i, False))
cdef public api pssast_call_visitExprNumber(object self, pssast_decl.IExprNumber *i) with gil:
    self.visitExprNumber(ExprNumber.mk(i, False))
cdef public api pssast_call_visitExprAggregateLiteral(object self, pssast_decl.IExprAggregateLiteral *i) with gil:
    self.visitExprAggregateLiteral(ExprAggregateLiteral.mk(i, False))
cdef public api pssast_call_visitExprOpenRangeList(object self, pssast_decl.IExprOpenRangeList *i) with gil:
    self.visitExprOpenRangeList(ExprOpenRangeList.mk(i, False))
cdef public api pssast_call_visitExprOpenRangeValue(object self, pssast_decl.IExprOpenRangeValue *i) with gil:
    self.visitExprOpenRangeValue(ExprOpenRangeValue.mk(i, False))
cdef public api pssast_call_visitExprRefPath(object self, pssast_decl.IExprRefPath *i) with gil:
    self.visitExprRefPath(ExprRefPath.mk(i, False))
cdef public api pssast_call_visitExprRefPathElem(object self, pssast_decl.IExprRefPathElem *i) with gil:
    self.visitExprRefPathElem(ExprRefPathElem.mk(i, False))
cdef public api pssast_call_visitExprRefPathStaticRooted(object self, pssast_decl.IExprRefPathStaticRooted *i) with gil:
    self.visitExprRefPathStaticRooted(ExprRefPathStaticRooted.mk(i, False))
cdef public api pssast_call_visitExprStaticRefPath(object self, pssast_decl.IExprStaticRefPath *i) with gil:
    self.visitExprStaticRefPath(ExprStaticRefPath.mk(i, False))
cdef public api pssast_call_visitExprString(object self, pssast_decl.IExprString *i) with gil:
    self.visitExprString(ExprString.mk(i, False))
cdef public api pssast_call_visitExprSubscript(object self, pssast_decl.IExprSubscript *i) with gil:
    self.visitExprSubscript(ExprSubscript.mk(i, False))
cdef public api pssast_call_visitExprUnary(object self, pssast_decl.IExprUnary *i) with gil:
    self.visitExprUnary(ExprUnary.mk(i, False))
cdef public api pssast_call_visitMethodParameterList(object self, pssast_decl.IMethodParameterList *i) with gil:
    self.visitMethodParameterList(MethodParameterList.mk(i, False))
cdef public api pssast_call_visitTypeIdentifier(object self, pssast_decl.ITypeIdentifier *i) with gil:
    self.visitTypeIdentifier(TypeIdentifier.mk(i, False))
cdef public api pssast_call_visitTypeIdentifierElem(object self, pssast_decl.ITypeIdentifierElem *i) with gil:
    self.visitTypeIdentifierElem(TypeIdentifierElem.mk(i, False))
cdef public api pssast_call_visitRefExprTypeScopeGlobal(object self, pssast_decl.IRefExprTypeScopeGlobal *i) with gil:
    self.visitRefExprTypeScopeGlobal(RefExprTypeScopeGlobal.mk(i, False))
cdef public api pssast_call_visitRefExprTypeScopeContext(object self, pssast_decl.IRefExprTypeScopeContext *i) with gil:
    self.visitRefExprTypeScopeContext(RefExprTypeScopeContext.mk(i, False))
cdef public api pssast_call_visitRefExprScopeIndex(object self, pssast_decl.IRefExprScopeIndex *i) with gil:
    self.visitRefExprScopeIndex(RefExprScopeIndex.mk(i, False))
cdef public api pssast_call_visitTemplateGenericTypeParamDecl(object self, pssast_decl.ITemplateGenericTypeParamDecl *i) with gil:
    self.visitTemplateGenericTypeParamDecl(TemplateGenericTypeParamDecl.mk(i, False))
cdef public api pssast_call_visitTemplateCategoryTypeParamDecl(object self, pssast_decl.ITemplateCategoryTypeParamDecl *i) with gil:
    self.visitTemplateCategoryTypeParamDecl(TemplateCategoryTypeParamDecl.mk(i, False))
cdef public api pssast_call_visitTemplateValueParamDecl(object self, pssast_decl.ITemplateValueParamDecl *i) with gil:
    self.visitTemplateValueParamDecl(TemplateValueParamDecl.mk(i, False))
cdef public api pssast_call_visitConstraintBlock(object self, pssast_decl.IConstraintBlock *i) with gil:
    self.visitConstraintBlock(ConstraintBlock.mk(i, False))
cdef public api pssast_call_visitConstraintScope(object self, pssast_decl.IConstraintScope *i) with gil:
    self.visitConstraintScope(ConstraintScope.mk(i, False))
cdef public api pssast_call_visitConstraintStmtDefault(object self, pssast_decl.IConstraintStmtDefault *i) with gil:
    self.visitConstraintStmtDefault(ConstraintStmtDefault.mk(i, False))
cdef public api pssast_call_visitConstraintStmtDefaultDisable(object self, pssast_decl.IConstraintStmtDefaultDisable *i) with gil:
    self.visitConstraintStmtDefaultDisable(ConstraintStmtDefaultDisable.mk(i, False))
cdef public api pssast_call_visitConstraintStmtExpr(object self, pssast_decl.IConstraintStmtExpr *i) with gil:
    self.visitConstraintStmtExpr(ConstraintStmtExpr.mk(i, False))
cdef public api pssast_call_visitConstraintStmtField(object self, pssast_decl.IConstraintStmtField *i) with gil:
    self.visitConstraintStmtField(ConstraintStmtField.mk(i, False))
cdef public api pssast_call_visitConstraintStmtIf(object self, pssast_decl.IConstraintStmtIf *i) with gil:
    self.visitConstraintStmtIf(ConstraintStmtIf.mk(i, False))
cdef public api pssast_call_visitConstraintStmtUnique(object self, pssast_decl.IConstraintStmtUnique *i) with gil:
    self.visitConstraintStmtUnique(ConstraintStmtUnique.mk(i, False))
cdef public api pssast_call_visitGlobalScope(object self, pssast_decl.IGlobalScope *i) with gil:
    self.visitGlobalScope(GlobalScope.mk(i, False))
cdef public api pssast_call_visitNamedScope(object self, pssast_decl.INamedScope *i) with gil:
    self.visitNamedScope(NamedScope.mk(i, False))
cdef public api pssast_call_visitPackageScope(object self, pssast_decl.IPackageScope *i) with gil:
    self.visitPackageScope(PackageScope.mk(i, False))
cdef public api pssast_call_visitDataTypeArray(object self, pssast_decl.IDataTypeArray *i) with gil:
    self.visitDataTypeArray(DataTypeArray.mk(i, False))
cdef public api pssast_call_visitDataTypeBool(object self, pssast_decl.IDataTypeBool *i) with gil:
    self.visitDataTypeBool(DataTypeBool.mk(i, False))
cdef public api pssast_call_visitDataTypeChandle(object self, pssast_decl.IDataTypeChandle *i) with gil:
    self.visitDataTypeChandle(DataTypeChandle.mk(i, False))
cdef public api pssast_call_visitDataTypeEnum(object self, pssast_decl.IDataTypeEnum *i) with gil:
    self.visitDataTypeEnum(DataTypeEnum.mk(i, False))
cdef public api pssast_call_visitDataTypeInt(object self, pssast_decl.IDataTypeInt *i) with gil:
    self.visitDataTypeInt(DataTypeInt.mk(i, False))
cdef public api pssast_call_visitDataTypeString(object self, pssast_decl.IDataTypeString *i) with gil:
    self.visitDataTypeString(DataTypeString.mk(i, False))
cdef public api pssast_call_visitDataTypeUserDefined(object self, pssast_decl.IDataTypeUserDefined *i) with gil:
    self.visitDataTypeUserDefined(DataTypeUserDefined.mk(i, False))
cdef public api pssast_call_visitExprRefPathContext(object self, pssast_decl.IExprRefPathContext *i) with gil:
    self.visitExprRefPathContext(ExprRefPathContext.mk(i, False))
cdef public api pssast_call_visitExprRefPathStatic(object self, pssast_decl.IExprRefPathStatic *i) with gil:
    self.visitExprRefPathStatic(ExprRefPathStatic.mk(i, False))
cdef public api pssast_call_visitExprSignedNumber(object self, pssast_decl.IExprSignedNumber *i) with gil:
    self.visitExprSignedNumber(ExprSignedNumber.mk(i, False))
cdef public api pssast_call_visitExprUnsignedNumber(object self, pssast_decl.IExprUnsignedNumber *i) with gil:
    self.visitExprUnsignedNumber(ExprUnsignedNumber.mk(i, False))
cdef public api pssast_call_visitConstraintStmtForall(object self, pssast_decl.IConstraintStmtForall *i) with gil:
    self.visitConstraintStmtForall(ConstraintStmtForall.mk(i, False))
cdef public api pssast_call_visitConstraintStmtForeach(object self, pssast_decl.IConstraintStmtForeach *i) with gil:
    self.visitConstraintStmtForeach(ConstraintStmtForeach.mk(i, False))
cdef public api pssast_call_visitConstraintStmtImplication(object self, pssast_decl.IConstraintStmtImplication *i) with gil:
    self.visitConstraintStmtImplication(ConstraintStmtImplication.mk(i, False))
cdef public api pssast_call_visitTypeScope(object self, pssast_decl.ITypeScope *i) with gil:
    self.visitTypeScope(TypeScope.mk(i, False))
cdef public api pssast_call_visitExprRefPathStaticFunc(object self, pssast_decl.IExprRefPathStaticFunc *i) with gil:
    self.visitExprRefPathStaticFunc(ExprRefPathStaticFunc.mk(i, False))
cdef public api pssast_call_visitExprRefPathSuper(object self, pssast_decl.IExprRefPathSuper *i) with gil:
    self.visitExprRefPathSuper(ExprRefPathSuper.mk(i, False))
cdef public api pssast_call_visitAction(object self, pssast_decl.IAction *i) with gil:
    self.visitAction(Action.mk(i, False))
cdef public api pssast_call_visitComponent(object self, pssast_decl.IComponent *i) with gil:
    self.visitComponent(Component.mk(i, False))
cdef public api pssast_call_visitStruct(object self, pssast_decl.IStruct *i) with gil:
    self.visitStruct(Struct.mk(i, False))
cdef public api pssast_call_visitState(object self, pssast_decl.IState *i) with gil:
    self.visitState(State.mk(i, False))
cdef public api pssast_call_visitStream(object self, pssast_decl.IStream *i) with gil:
    self.visitStream(Stream.mk(i, False))
cdef public api pssast_call_visitBuffer(object self, pssast_decl.IBuffer *i) with gil:
    self.visitBuffer(Buffer.mk(i, False))
cdef public api pssast_call_visitResource(object self, pssast_decl.IResource *i) with gil:
    self.visitResource(Resource.mk(i, False))
