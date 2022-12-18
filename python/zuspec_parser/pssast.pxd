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

from pssparser cimport pssast_decl
cdef class Factory(object):
    cdef pssast_decl.IFactory *_hndl
    cpdef ExecStmt mkExecStmt(self)
    cpdef Expr mkExpr(self)
    cpdef RefExpr mkRefExpr(self)
    cpdef TemplateParamDeclList mkTemplateParamDeclList(self)
    cpdef TemplateParamDecl mkTemplateParamDecl(self,
    ExprId name)
    cpdef ScopeChild mkScopeChild(self)
    cpdef TemplateParamValueList mkTemplateParamValueList(self)
    cpdef TemplateParamValue mkTemplateParamValue(self)
    cpdef TemplateParamTypeValue mkTemplateParamTypeValue(self,
    TypeIdentifier value)
    cpdef TemplateParamExprValue mkTemplateParamExprValue(self,
    Expr value)
    cpdef ConstraintStmt mkConstraintStmt(self)
    cpdef Scope mkScope(self)
    cpdef NamedScopeChild mkNamedScopeChild(self,
    ExprId name)
    cpdef PackageImportStmt mkPackageImportStmt(self,
    bool wildcard,
    ExprId alias)
    cpdef DataType mkDataType(self)
    cpdef ExecScope mkExecScope(self)
    cpdef ProceduralStmtDataDeclaration mkProceduralStmtDataDeclaration(self,
    DataType datatype,
    ExprId name)
    cpdef ExprBin mkExprBin(self,
    Expr lhs,
     op,
    Expr rhs)
    cpdef ExprBitSlice mkExprBitSlice(self,
    Expr expr,
    Expr lhs,
    Expr rhs)
    cpdef ExprBool mkExprBool(self,
    bool value)
    cpdef ExprCast mkExprCast(self,
    Expr casting_type,
    Expr expr)
    cpdef ExprCompileHas mkExprCompileHas(self,
    ExprRefPathStatic ref)
    cpdef ExprCond mkExprCond(self,
    Expr cond_e,
    Expr true_e,
    Expr false_e)
    cpdef ExprDomainOpenRangeList mkExprDomainOpenRangeList(self)
    cpdef ExprDomainOpenRangeValue mkExprDomainOpenRangeValue(self,
    bool single,
    Expr lhs,
    Expr rhs)
    cpdef ExprHierarchicalId mkExprHierarchicalId(self)
    cpdef ExprId mkExprId(self,
    std_string id,
    bool is_escaped)
    cpdef ExprIn mkExprIn(self,
    Expr lhs,
    ExprOpenRangeList rhs)
    cpdef ExprMemberPathElem mkExprMemberPathElem(self,
    ExprId id,
    MethodParameterList params,
    Expr subscript)
    cpdef ExprNumber mkExprNumber(self)
    cpdef ExprAggregateLiteral mkExprAggregateLiteral(self)
    cpdef ExprOpenRangeList mkExprOpenRangeList(self)
    cpdef ExprOpenRangeValue mkExprOpenRangeValue(self,
    Expr lhs,
    Expr rhs)
    cpdef ExprRefPath mkExprRefPath(self)
    cpdef ExprRefPathElem mkExprRefPathElem(self)
    cpdef ExprRefPathStaticRooted mkExprRefPathStaticRooted(self,
    ExprRefPathStatic root,
    ExprRefPathContext leaf)
    cpdef ExprStaticRefPath mkExprStaticRefPath(self,
    bool is_global,
    ExprMemberPathElem leaf)
    cpdef ExprString mkExprString(self,
    std_string value,
    bool is_raw)
    cpdef ExprSubscript mkExprSubscript(self,
    Expr expr,
    Expr subscript)
    cpdef ExprUnary mkExprUnary(self,
     op,
    Expr rhs)
    cpdef MethodParameterList mkMethodParameterList(self)
    cpdef TypeIdentifier mkTypeIdentifier(self)
    cpdef TypeIdentifierElem mkTypeIdentifierElem(self,
    ExprId id)
    cpdef RefExprTypeScopeGlobal mkRefExprTypeScopeGlobal(self,
    int32_t fileid)
    cpdef RefExprTypeScopeContext mkRefExprTypeScopeContext(self,
    RefExpr base,
    int32_t offset)
    cpdef RefExprScopeIndex mkRefExprScopeIndex(self,
    RefExpr base,
    int32_t offset)
    cpdef TemplateGenericTypeParamDecl mkTemplateGenericTypeParamDecl(self,
    ExprId name,
    TypeIdentifier dflt)
    cpdef TemplateCategoryTypeParamDecl mkTemplateCategoryTypeParamDecl(self,
    ExprId name,
     category,
    TypeIdentifier restriction,
    TypeIdentifier dflt)
    cpdef TemplateValueParamDecl mkTemplateValueParamDecl(self,
    ExprId name,
    Expr dflt)
    cpdef ConstraintBlock mkConstraintBlock(self,
    std_string name,
    bool is_dynamic)
    cpdef ConstraintScope mkConstraintScope(self)
    cpdef ConstraintStmtDefault mkConstraintStmtDefault(self,
    ExprHierarchicalId hid,
    Expr expr)
    cpdef ConstraintStmtDefaultDisable mkConstraintStmtDefaultDisable(self,
    ExprHierarchicalId hid)
    cpdef ConstraintStmtExpr mkConstraintStmtExpr(self,
    Expr expr)
    cpdef ConstraintStmtField mkConstraintStmtField(self,
    ExprId name,
    DataType type)
    cpdef ConstraintStmtIf mkConstraintStmtIf(self,
    Expr cond,
    ConstraintScope true_c,
    ConstraintScope false_c)
    cpdef ConstraintStmtUnique mkConstraintStmtUnique(self)
    cpdef GlobalScope mkGlobalScope(self,
    int32_t fileid)
    cpdef NamedScope mkNamedScope(self,
    ExprId name)
    cpdef PackageScope mkPackageScope(self)
    cpdef DataTypeArray mkDataTypeArray(self,
    DataType type,
    Expr size)
    cpdef DataTypeBool mkDataTypeBool(self)
    cpdef DataTypeChandle mkDataTypeChandle(self)
    cpdef DataTypeEnum mkDataTypeEnum(self,
    DataTypeUserDefined tid,
    ExprOpenRangeList in_rangelist)
    cpdef DataTypeInt mkDataTypeInt(self,
    bool is_signed,
    Expr width_lhs,
    Expr width_rhs,
    ExprDomainOpenRangeList in_range)
    cpdef DataTypeString mkDataTypeString(self,
    bool has_range)
    cpdef DataTypeUserDefined mkDataTypeUserDefined(self,
    bool is_global)
    cpdef ExprRefPathContext mkExprRefPathContext(self,
    ExprHierarchicalId hier_id)
    cpdef ExprRefPathStatic mkExprRefPathStatic(self,
    bool is_global)
    cpdef ExprSignedNumber mkExprSignedNumber(self,
    std_string image,
    uint32_t width,
    int64_t value)
    cpdef ExprUnsignedNumber mkExprUnsignedNumber(self,
    std_string image,
    uint32_t width,
    uint64_t value)
    cpdef ConstraintStmtForall mkConstraintStmtForall(self,
    ExprId iterator_id,
    DataTypeUserDefined type_id,
    ExprRefPath ref_path)
    cpdef ConstraintStmtForeach mkConstraintStmtForeach(self,
    Expr expr)
    cpdef ConstraintStmtImplication mkConstraintStmtImplication(self,
    Expr cond)
    cpdef TypeScope mkTypeScope(self,
    ExprId name,
    TypeIdentifier super_t)
    cpdef ExprRefPathStaticFunc mkExprRefPathStaticFunc(self,
    bool is_global,
    MethodParameterList params)
    cpdef ExprRefPathSuper mkExprRefPathSuper(self,
    ExprHierarchicalId hier_id)
    cpdef Action mkAction(self,
    ExprId name,
    TypeIdentifier super_t,
    bool is_abstract)
    cpdef Component mkComponent(self,
    ExprId name,
    TypeIdentifier super_t)
    cpdef Struct mkStruct(self,
    ExprId name,
    TypeIdentifier super_t)
    cpdef State mkState(self,
    ExprId name,
    TypeIdentifier super_t)
    cpdef Stream mkStream(self,
    ExprId name,
    TypeIdentifier super_t)
    cpdef Buffer mkBuffer(self,
    ExprId name,
    TypeIdentifier super_t)
    cpdef Resource mkResource(self,
    ExprId name,
    TypeIdentifier super_t)
    @staticmethod
    cdef mk(pssast_decl.IFactory *hndl)
cdef class ExecStmt(object):
    cdef pssast_decl.IExecStmt    *_hndl
    cdef bool           _owned
    
    cpdef void accept(self, VisitorBase v)
    cdef pssast_decl.IExecStmt *asExecStmt(self)
    @staticmethod
    cdef ExecStmt mk(pssast_decl.IExecStmt *hndl, bool owned)

cdef class Expr(object):
    cdef pssast_decl.IExpr    *_hndl
    cdef bool           _owned
    
    cpdef void accept(self, VisitorBase v)
    cdef pssast_decl.IExpr *asExpr(self)
    @staticmethod
    cdef Expr mk(pssast_decl.IExpr *hndl, bool owned)

cdef class RefExpr(object):
    cdef pssast_decl.IRefExpr    *_hndl
    cdef bool           _owned
    
    cpdef void accept(self, VisitorBase v)
    cdef pssast_decl.IRefExpr *asRefExpr(self)
    @staticmethod
    cdef RefExpr mk(pssast_decl.IRefExpr *hndl, bool owned)

cdef class TemplateParamDeclList(object):
    cdef pssast_decl.ITemplateParamDeclList    *_hndl
    cdef bool           _owned
    
    cpdef void accept(self, VisitorBase v)
    cdef pssast_decl.ITemplateParamDeclList *asTemplateParamDeclList(self)
    @staticmethod
    cdef TemplateParamDeclList mk(pssast_decl.ITemplateParamDeclList *hndl, bool owned)

cdef class TemplateParamDecl(object):
    cdef pssast_decl.ITemplateParamDecl    *_hndl
    cdef bool           _owned
    
    cpdef void accept(self, VisitorBase v)
    cdef pssast_decl.ITemplateParamDecl *asTemplateParamDecl(self)
    @staticmethod
    cdef TemplateParamDecl mk(pssast_decl.ITemplateParamDecl *hndl, bool owned)

cdef class ScopeChild(object):
    cdef pssast_decl.IScopeChild    *_hndl
    cdef bool           _owned
    
    cpdef void accept(self, VisitorBase v)
    cdef pssast_decl.IScopeChild *asScopeChild(self)
    @staticmethod
    cdef ScopeChild mk(pssast_decl.IScopeChild *hndl, bool owned)
    cpdef std_string getDocstring(self)
    cpdef int32_t getIndex(self)

cdef class TemplateParamValueList(object):
    cdef pssast_decl.ITemplateParamValueList    *_hndl
    cdef bool           _owned
    
    cpdef void accept(self, VisitorBase v)
    cdef pssast_decl.ITemplateParamValueList *asTemplateParamValueList(self)
    @staticmethod
    cdef TemplateParamValueList mk(pssast_decl.ITemplateParamValueList *hndl, bool owned)

cdef class TemplateParamValue(object):
    cdef pssast_decl.ITemplateParamValue    *_hndl
    cdef bool           _owned
    
    cpdef void accept(self, VisitorBase v)
    cdef pssast_decl.ITemplateParamValue *asTemplateParamValue(self)
    @staticmethod
    cdef TemplateParamValue mk(pssast_decl.ITemplateParamValue *hndl, bool owned)

cdef class TemplateParamTypeValue(object):
    cdef pssast_decl.ITemplateParamTypeValue    *_hndl
    cdef bool           _owned
    
    cpdef void accept(self, VisitorBase v)
    cdef pssast_decl.ITemplateParamTypeValue *asTemplateParamTypeValue(self)
    @staticmethod
    cdef TemplateParamTypeValue mk(pssast_decl.ITemplateParamTypeValue *hndl, bool owned)

cdef class TemplateParamExprValue(object):
    cdef pssast_decl.ITemplateParamExprValue    *_hndl
    cdef bool           _owned
    
    cpdef void accept(self, VisitorBase v)
    cdef pssast_decl.ITemplateParamExprValue *asTemplateParamExprValue(self)
    @staticmethod
    cdef TemplateParamExprValue mk(pssast_decl.ITemplateParamExprValue *hndl, bool owned)

cdef class ConstraintStmt(ScopeChild):
    
    cdef pssast_decl.IConstraintStmt *asConstraintStmt(self)
    @staticmethod
    cdef ConstraintStmt mk(pssast_decl.IConstraintStmt *hndl, bool owned)

cdef class Scope(ScopeChild):
    
    cdef pssast_decl.IScope *asScope(self)
    @staticmethod
    cdef Scope mk(pssast_decl.IScope *hndl, bool owned)

cdef class NamedScopeChild(ScopeChild):
    
    cdef pssast_decl.INamedScopeChild *asNamedScopeChild(self)
    @staticmethod
    cdef NamedScopeChild mk(pssast_decl.INamedScopeChild *hndl, bool owned)

cdef class PackageImportStmt(ScopeChild):
    
    cdef pssast_decl.IPackageImportStmt *asPackageImportStmt(self)
    @staticmethod
    cdef PackageImportStmt mk(pssast_decl.IPackageImportStmt *hndl, bool owned)
    cpdef bool getWildcard(self)

cdef class DataType(ScopeChild):
    
    cdef pssast_decl.IDataType *asDataType(self)
    @staticmethod
    cdef DataType mk(pssast_decl.IDataType *hndl, bool owned)

cdef class ExecScope(ExecStmt):
    
    cdef pssast_decl.IExecScope *asExecScope(self)
    @staticmethod
    cdef ExecScope mk(pssast_decl.IExecScope *hndl, bool owned)

cdef class ProceduralStmtDataDeclaration(ExecStmt):
    
    cdef pssast_decl.IProceduralStmtDataDeclaration *asProceduralStmtDataDeclaration(self)
    @staticmethod
    cdef ProceduralStmtDataDeclaration mk(pssast_decl.IProceduralStmtDataDeclaration *hndl, bool owned)

cdef class ExprBin(Expr):
    
    cdef pssast_decl.IExprBin *asExprBin(self)
    @staticmethod
    cdef ExprBin mk(pssast_decl.IExprBin *hndl, bool owned)

cdef class ExprBitSlice(Expr):
    
    cdef pssast_decl.IExprBitSlice *asExprBitSlice(self)
    @staticmethod
    cdef ExprBitSlice mk(pssast_decl.IExprBitSlice *hndl, bool owned)

cdef class ExprBool(Expr):
    
    cdef pssast_decl.IExprBool *asExprBool(self)
    @staticmethod
    cdef ExprBool mk(pssast_decl.IExprBool *hndl, bool owned)
    cpdef bool getValue(self)

cdef class ExprCast(Expr):
    
    cdef pssast_decl.IExprCast *asExprCast(self)
    @staticmethod
    cdef ExprCast mk(pssast_decl.IExprCast *hndl, bool owned)

cdef class ExprCompileHas(Expr):
    
    cdef pssast_decl.IExprCompileHas *asExprCompileHas(self)
    @staticmethod
    cdef ExprCompileHas mk(pssast_decl.IExprCompileHas *hndl, bool owned)

cdef class ExprCond(Expr):
    
    cdef pssast_decl.IExprCond *asExprCond(self)
    @staticmethod
    cdef ExprCond mk(pssast_decl.IExprCond *hndl, bool owned)

cdef class ExprDomainOpenRangeList(Expr):
    
    cdef pssast_decl.IExprDomainOpenRangeList *asExprDomainOpenRangeList(self)
    @staticmethod
    cdef ExprDomainOpenRangeList mk(pssast_decl.IExprDomainOpenRangeList *hndl, bool owned)

cdef class ExprDomainOpenRangeValue(Expr):
    
    cdef pssast_decl.IExprDomainOpenRangeValue *asExprDomainOpenRangeValue(self)
    @staticmethod
    cdef ExprDomainOpenRangeValue mk(pssast_decl.IExprDomainOpenRangeValue *hndl, bool owned)
    cpdef bool getSingle(self)

cdef class ExprHierarchicalId(Expr):
    
    cdef pssast_decl.IExprHierarchicalId *asExprHierarchicalId(self)
    @staticmethod
    cdef ExprHierarchicalId mk(pssast_decl.IExprHierarchicalId *hndl, bool owned)

cdef class ExprId(Expr):
    
    cdef pssast_decl.IExprId *asExprId(self)
    @staticmethod
    cdef ExprId mk(pssast_decl.IExprId *hndl, bool owned)
    cpdef std_string getId(self)
    cpdef bool getIs_escaped(self)

cdef class ExprIn(Expr):
    
    cdef pssast_decl.IExprIn *asExprIn(self)
    @staticmethod
    cdef ExprIn mk(pssast_decl.IExprIn *hndl, bool owned)

cdef class ExprMemberPathElem(Expr):
    
    cdef pssast_decl.IExprMemberPathElem *asExprMemberPathElem(self)
    @staticmethod
    cdef ExprMemberPathElem mk(pssast_decl.IExprMemberPathElem *hndl, bool owned)
    cpdef int32_t getTarget(self)

cdef class ExprNumber(Expr):
    
    cdef pssast_decl.IExprNumber *asExprNumber(self)
    @staticmethod
    cdef ExprNumber mk(pssast_decl.IExprNumber *hndl, bool owned)

cdef class ExprAggregateLiteral(Expr):
    
    cdef pssast_decl.IExprAggregateLiteral *asExprAggregateLiteral(self)
    @staticmethod
    cdef ExprAggregateLiteral mk(pssast_decl.IExprAggregateLiteral *hndl, bool owned)

cdef class ExprOpenRangeList(Expr):
    
    cdef pssast_decl.IExprOpenRangeList *asExprOpenRangeList(self)
    @staticmethod
    cdef ExprOpenRangeList mk(pssast_decl.IExprOpenRangeList *hndl, bool owned)

cdef class ExprOpenRangeValue(Expr):
    
    cdef pssast_decl.IExprOpenRangeValue *asExprOpenRangeValue(self)
    @staticmethod
    cdef ExprOpenRangeValue mk(pssast_decl.IExprOpenRangeValue *hndl, bool owned)

cdef class ExprRefPath(Expr):
    
    cdef pssast_decl.IExprRefPath *asExprRefPath(self)
    @staticmethod
    cdef ExprRefPath mk(pssast_decl.IExprRefPath *hndl, bool owned)

cdef class ExprRefPathElem(Expr):
    
    cdef pssast_decl.IExprRefPathElem *asExprRefPathElem(self)
    @staticmethod
    cdef ExprRefPathElem mk(pssast_decl.IExprRefPathElem *hndl, bool owned)

cdef class ExprRefPathStaticRooted(Expr):
    
    cdef pssast_decl.IExprRefPathStaticRooted *asExprRefPathStaticRooted(self)
    @staticmethod
    cdef ExprRefPathStaticRooted mk(pssast_decl.IExprRefPathStaticRooted *hndl, bool owned)

cdef class ExprStaticRefPath(Expr):
    
    cdef pssast_decl.IExprStaticRefPath *asExprStaticRefPath(self)
    @staticmethod
    cdef ExprStaticRefPath mk(pssast_decl.IExprStaticRefPath *hndl, bool owned)
    cpdef bool getIs_global(self)

cdef class ExprString(Expr):
    
    cdef pssast_decl.IExprString *asExprString(self)
    @staticmethod
    cdef ExprString mk(pssast_decl.IExprString *hndl, bool owned)
    cpdef std_string getValue(self)
    cpdef bool getIs_raw(self)

cdef class ExprSubscript(Expr):
    
    cdef pssast_decl.IExprSubscript *asExprSubscript(self)
    @staticmethod
    cdef ExprSubscript mk(pssast_decl.IExprSubscript *hndl, bool owned)

cdef class ExprUnary(Expr):
    
    cdef pssast_decl.IExprUnary *asExprUnary(self)
    @staticmethod
    cdef ExprUnary mk(pssast_decl.IExprUnary *hndl, bool owned)

cdef class MethodParameterList(Expr):
    
    cdef pssast_decl.IMethodParameterList *asMethodParameterList(self)
    @staticmethod
    cdef MethodParameterList mk(pssast_decl.IMethodParameterList *hndl, bool owned)

cdef class TypeIdentifier(Expr):
    
    cdef pssast_decl.ITypeIdentifier *asTypeIdentifier(self)
    @staticmethod
    cdef TypeIdentifier mk(pssast_decl.ITypeIdentifier *hndl, bool owned)

cdef class TypeIdentifierElem(Expr):
    
    cdef pssast_decl.ITypeIdentifierElem *asTypeIdentifierElem(self)
    @staticmethod
    cdef TypeIdentifierElem mk(pssast_decl.ITypeIdentifierElem *hndl, bool owned)

cdef class RefExprTypeScopeGlobal(RefExpr):
    
    cdef pssast_decl.IRefExprTypeScopeGlobal *asRefExprTypeScopeGlobal(self)
    @staticmethod
    cdef RefExprTypeScopeGlobal mk(pssast_decl.IRefExprTypeScopeGlobal *hndl, bool owned)
    cpdef int32_t getFileid(self)

cdef class RefExprTypeScopeContext(RefExpr):
    
    cdef pssast_decl.IRefExprTypeScopeContext *asRefExprTypeScopeContext(self)
    @staticmethod
    cdef RefExprTypeScopeContext mk(pssast_decl.IRefExprTypeScopeContext *hndl, bool owned)
    cpdef int32_t getOffset(self)

cdef class RefExprScopeIndex(RefExpr):
    
    cdef pssast_decl.IRefExprScopeIndex *asRefExprScopeIndex(self)
    @staticmethod
    cdef RefExprScopeIndex mk(pssast_decl.IRefExprScopeIndex *hndl, bool owned)
    cpdef int32_t getOffset(self)

cdef class TemplateGenericTypeParamDecl(TemplateParamDecl):
    
    cdef pssast_decl.ITemplateGenericTypeParamDecl *asTemplateGenericTypeParamDecl(self)
    @staticmethod
    cdef TemplateGenericTypeParamDecl mk(pssast_decl.ITemplateGenericTypeParamDecl *hndl, bool owned)

cdef class TemplateCategoryTypeParamDecl(TemplateParamDecl):
    
    cdef pssast_decl.ITemplateCategoryTypeParamDecl *asTemplateCategoryTypeParamDecl(self)
    @staticmethod
    cdef TemplateCategoryTypeParamDecl mk(pssast_decl.ITemplateCategoryTypeParamDecl *hndl, bool owned)

cdef class TemplateValueParamDecl(TemplateParamDecl):
    
    cdef pssast_decl.ITemplateValueParamDecl *asTemplateValueParamDecl(self)
    @staticmethod
    cdef TemplateValueParamDecl mk(pssast_decl.ITemplateValueParamDecl *hndl, bool owned)

cdef class ConstraintBlock(ConstraintStmt):
    
    cdef pssast_decl.IConstraintBlock *asConstraintBlock(self)
    @staticmethod
    cdef ConstraintBlock mk(pssast_decl.IConstraintBlock *hndl, bool owned)
    cpdef std_string getName(self)
    cpdef bool getIs_dynamic(self)

cdef class ConstraintScope(ConstraintStmt):
    
    cdef pssast_decl.IConstraintScope *asConstraintScope(self)
    @staticmethod
    cdef ConstraintScope mk(pssast_decl.IConstraintScope *hndl, bool owned)

cdef class ConstraintStmtDefault(ConstraintStmt):
    
    cdef pssast_decl.IConstraintStmtDefault *asConstraintStmtDefault(self)
    @staticmethod
    cdef ConstraintStmtDefault mk(pssast_decl.IConstraintStmtDefault *hndl, bool owned)

cdef class ConstraintStmtDefaultDisable(ConstraintStmt):
    
    cdef pssast_decl.IConstraintStmtDefaultDisable *asConstraintStmtDefaultDisable(self)
    @staticmethod
    cdef ConstraintStmtDefaultDisable mk(pssast_decl.IConstraintStmtDefaultDisable *hndl, bool owned)

cdef class ConstraintStmtExpr(ConstraintStmt):
    
    cdef pssast_decl.IConstraintStmtExpr *asConstraintStmtExpr(self)
    @staticmethod
    cdef ConstraintStmtExpr mk(pssast_decl.IConstraintStmtExpr *hndl, bool owned)

cdef class ConstraintStmtField(ConstraintStmt):
    
    cdef pssast_decl.IConstraintStmtField *asConstraintStmtField(self)
    @staticmethod
    cdef ConstraintStmtField mk(pssast_decl.IConstraintStmtField *hndl, bool owned)

cdef class ConstraintStmtIf(ConstraintStmt):
    
    cdef pssast_decl.IConstraintStmtIf *asConstraintStmtIf(self)
    @staticmethod
    cdef ConstraintStmtIf mk(pssast_decl.IConstraintStmtIf *hndl, bool owned)

cdef class ConstraintStmtUnique(ConstraintStmt):
    
    cdef pssast_decl.IConstraintStmtUnique *asConstraintStmtUnique(self)
    @staticmethod
    cdef ConstraintStmtUnique mk(pssast_decl.IConstraintStmtUnique *hndl, bool owned)

cdef class GlobalScope(Scope):
    
    cdef pssast_decl.IGlobalScope *asGlobalScope(self)
    @staticmethod
    cdef GlobalScope mk(pssast_decl.IGlobalScope *hndl, bool owned)
    cpdef int32_t getFileid(self)

cdef class NamedScope(Scope):
    
    cdef pssast_decl.INamedScope *asNamedScope(self)
    @staticmethod
    cdef NamedScope mk(pssast_decl.INamedScope *hndl, bool owned)

cdef class PackageScope(Scope):
    
    cdef pssast_decl.IPackageScope *asPackageScope(self)
    @staticmethod
    cdef PackageScope mk(pssast_decl.IPackageScope *hndl, bool owned)

cdef class DataTypeArray(DataType):
    
    cdef pssast_decl.IDataTypeArray *asDataTypeArray(self)
    @staticmethod
    cdef DataTypeArray mk(pssast_decl.IDataTypeArray *hndl, bool owned)

cdef class DataTypeBool(DataType):
    
    cdef pssast_decl.IDataTypeBool *asDataTypeBool(self)
    @staticmethod
    cdef DataTypeBool mk(pssast_decl.IDataTypeBool *hndl, bool owned)

cdef class DataTypeChandle(DataType):
    
    cdef pssast_decl.IDataTypeChandle *asDataTypeChandle(self)
    @staticmethod
    cdef DataTypeChandle mk(pssast_decl.IDataTypeChandle *hndl, bool owned)

cdef class DataTypeEnum(DataType):
    
    cdef pssast_decl.IDataTypeEnum *asDataTypeEnum(self)
    @staticmethod
    cdef DataTypeEnum mk(pssast_decl.IDataTypeEnum *hndl, bool owned)

cdef class DataTypeInt(DataType):
    
    cdef pssast_decl.IDataTypeInt *asDataTypeInt(self)
    @staticmethod
    cdef DataTypeInt mk(pssast_decl.IDataTypeInt *hndl, bool owned)
    cpdef bool getIs_signed(self)

cdef class DataTypeString(DataType):
    
    cdef pssast_decl.IDataTypeString *asDataTypeString(self)
    @staticmethod
    cdef DataTypeString mk(pssast_decl.IDataTypeString *hndl, bool owned)
    cpdef bool getHas_range(self)

cdef class DataTypeUserDefined(DataType):
    
    cdef pssast_decl.IDataTypeUserDefined *asDataTypeUserDefined(self)
    @staticmethod
    cdef DataTypeUserDefined mk(pssast_decl.IDataTypeUserDefined *hndl, bool owned)
    cpdef bool getIs_global(self)

cdef class ExprRefPathContext(ExprRefPath):
    
    cdef pssast_decl.IExprRefPathContext *asExprRefPathContext(self)
    @staticmethod
    cdef ExprRefPathContext mk(pssast_decl.IExprRefPathContext *hndl, bool owned)

cdef class ExprRefPathStatic(ExprRefPath):
    
    cdef pssast_decl.IExprRefPathStatic *asExprRefPathStatic(self)
    @staticmethod
    cdef ExprRefPathStatic mk(pssast_decl.IExprRefPathStatic *hndl, bool owned)
    cpdef bool getIs_global(self)

cdef class ExprSignedNumber(ExprNumber):
    
    cdef pssast_decl.IExprSignedNumber *asExprSignedNumber(self)
    @staticmethod
    cdef ExprSignedNumber mk(pssast_decl.IExprSignedNumber *hndl, bool owned)
    cpdef std_string getImage(self)
    cpdef uint32_t getWidth(self)
    cpdef int64_t getValue(self)

cdef class ExprUnsignedNumber(ExprNumber):
    
    cdef pssast_decl.IExprUnsignedNumber *asExprUnsignedNumber(self)
    @staticmethod
    cdef ExprUnsignedNumber mk(pssast_decl.IExprUnsignedNumber *hndl, bool owned)
    cpdef std_string getImage(self)
    cpdef uint32_t getWidth(self)
    cpdef uint64_t getValue(self)

cdef class ConstraintStmtForall(ConstraintScope):
    
    cdef pssast_decl.IConstraintStmtForall *asConstraintStmtForall(self)
    @staticmethod
    cdef ConstraintStmtForall mk(pssast_decl.IConstraintStmtForall *hndl, bool owned)

cdef class ConstraintStmtForeach(ConstraintScope):
    
    cdef pssast_decl.IConstraintStmtForeach *asConstraintStmtForeach(self)
    @staticmethod
    cdef ConstraintStmtForeach mk(pssast_decl.IConstraintStmtForeach *hndl, bool owned)

cdef class ConstraintStmtImplication(ConstraintScope):
    
    cdef pssast_decl.IConstraintStmtImplication *asConstraintStmtImplication(self)
    @staticmethod
    cdef ConstraintStmtImplication mk(pssast_decl.IConstraintStmtImplication *hndl, bool owned)

cdef class TypeScope(NamedScope):
    
    cdef pssast_decl.ITypeScope *asTypeScope(self)
    @staticmethod
    cdef TypeScope mk(pssast_decl.ITypeScope *hndl, bool owned)

cdef class ExprRefPathStaticFunc(ExprRefPathStatic):
    
    cdef pssast_decl.IExprRefPathStaticFunc *asExprRefPathStaticFunc(self)
    @staticmethod
    cdef ExprRefPathStaticFunc mk(pssast_decl.IExprRefPathStaticFunc *hndl, bool owned)

cdef class ExprRefPathSuper(ExprRefPathContext):
    
    cdef pssast_decl.IExprRefPathSuper *asExprRefPathSuper(self)
    @staticmethod
    cdef ExprRefPathSuper mk(pssast_decl.IExprRefPathSuper *hndl, bool owned)

cdef class Action(TypeScope):
    
    cdef pssast_decl.IAction *asAction(self)
    @staticmethod
    cdef Action mk(pssast_decl.IAction *hndl, bool owned)
    cpdef bool getIs_abstract(self)

cdef class Component(TypeScope):
    
    cdef pssast_decl.IComponent *asComponent(self)
    @staticmethod
    cdef Component mk(pssast_decl.IComponent *hndl, bool owned)

cdef class Struct(TypeScope):
    
    cdef pssast_decl.IStruct *asStruct(self)
    @staticmethod
    cdef Struct mk(pssast_decl.IStruct *hndl, bool owned)

cdef class State(Struct):
    
    cdef pssast_decl.IState *asState(self)
    @staticmethod
    cdef State mk(pssast_decl.IState *hndl, bool owned)

cdef class Stream(Struct):
    
    cdef pssast_decl.IStream *asStream(self)
    @staticmethod
    cdef Stream mk(pssast_decl.IStream *hndl, bool owned)

cdef class Buffer(Struct):
    
    cdef pssast_decl.IBuffer *asBuffer(self)
    @staticmethod
    cdef Buffer mk(pssast_decl.IBuffer *hndl, bool owned)

cdef class Resource(Struct):
    
    cdef pssast_decl.IResource *asResource(self)
    @staticmethod
    cdef Resource mk(pssast_decl.IResource *hndl, bool owned)

cdef class VisitorBase(object):
    cdef pssast_decl.PyBaseVisitor *_hndl
    cdef bool                  _owned
    cpdef void visitExecStmt(self, ExecStmt i)
    cpdef void visitExpr(self, Expr i)
    cpdef void visitRefExpr(self, RefExpr i)
    cpdef void visitTemplateParamDeclList(self, TemplateParamDeclList i)
    cpdef void visitTemplateParamDecl(self, TemplateParamDecl i)
    cpdef void visitScopeChild(self, ScopeChild i)
    cpdef void visitTemplateParamValueList(self, TemplateParamValueList i)
    cpdef void visitTemplateParamValue(self, TemplateParamValue i)
    cpdef void visitTemplateParamTypeValue(self, TemplateParamTypeValue i)
    cpdef void visitTemplateParamExprValue(self, TemplateParamExprValue i)
    cpdef void visitConstraintStmt(self, ConstraintStmt i)
    cpdef void visitScope(self, Scope i)
    cpdef void visitNamedScopeChild(self, NamedScopeChild i)
    cpdef void visitPackageImportStmt(self, PackageImportStmt i)
    cpdef void visitDataType(self, DataType i)
    cpdef void visitExecScope(self, ExecScope i)
    cpdef void visitProceduralStmtDataDeclaration(self, ProceduralStmtDataDeclaration i)
    cpdef void visitExprBin(self, ExprBin i)
    cpdef void visitExprBitSlice(self, ExprBitSlice i)
    cpdef void visitExprBool(self, ExprBool i)
    cpdef void visitExprCast(self, ExprCast i)
    cpdef void visitExprCompileHas(self, ExprCompileHas i)
    cpdef void visitExprCond(self, ExprCond i)
    cpdef void visitExprDomainOpenRangeList(self, ExprDomainOpenRangeList i)
    cpdef void visitExprDomainOpenRangeValue(self, ExprDomainOpenRangeValue i)
    cpdef void visitExprHierarchicalId(self, ExprHierarchicalId i)
    cpdef void visitExprId(self, ExprId i)
    cpdef void visitExprIn(self, ExprIn i)
    cpdef void visitExprMemberPathElem(self, ExprMemberPathElem i)
    cpdef void visitExprNumber(self, ExprNumber i)
    cpdef void visitExprAggregateLiteral(self, ExprAggregateLiteral i)
    cpdef void visitExprOpenRangeList(self, ExprOpenRangeList i)
    cpdef void visitExprOpenRangeValue(self, ExprOpenRangeValue i)
    cpdef void visitExprRefPath(self, ExprRefPath i)
    cpdef void visitExprRefPathElem(self, ExprRefPathElem i)
    cpdef void visitExprRefPathStaticRooted(self, ExprRefPathStaticRooted i)
    cpdef void visitExprStaticRefPath(self, ExprStaticRefPath i)
    cpdef void visitExprString(self, ExprString i)
    cpdef void visitExprSubscript(self, ExprSubscript i)
    cpdef void visitExprUnary(self, ExprUnary i)
    cpdef void visitMethodParameterList(self, MethodParameterList i)
    cpdef void visitTypeIdentifier(self, TypeIdentifier i)
    cpdef void visitTypeIdentifierElem(self, TypeIdentifierElem i)
    cpdef void visitRefExprTypeScopeGlobal(self, RefExprTypeScopeGlobal i)
    cpdef void visitRefExprTypeScopeContext(self, RefExprTypeScopeContext i)
    cpdef void visitRefExprScopeIndex(self, RefExprScopeIndex i)
    cpdef void visitTemplateGenericTypeParamDecl(self, TemplateGenericTypeParamDecl i)
    cpdef void visitTemplateCategoryTypeParamDecl(self, TemplateCategoryTypeParamDecl i)
    cpdef void visitTemplateValueParamDecl(self, TemplateValueParamDecl i)
    cpdef void visitConstraintBlock(self, ConstraintBlock i)
    cpdef void visitConstraintScope(self, ConstraintScope i)
    cpdef void visitConstraintStmtDefault(self, ConstraintStmtDefault i)
    cpdef void visitConstraintStmtDefaultDisable(self, ConstraintStmtDefaultDisable i)
    cpdef void visitConstraintStmtExpr(self, ConstraintStmtExpr i)
    cpdef void visitConstraintStmtField(self, ConstraintStmtField i)
    cpdef void visitConstraintStmtIf(self, ConstraintStmtIf i)
    cpdef void visitConstraintStmtUnique(self, ConstraintStmtUnique i)
    cpdef void visitGlobalScope(self, GlobalScope i)
    cpdef void visitNamedScope(self, NamedScope i)
    cpdef void visitPackageScope(self, PackageScope i)
    cpdef void visitDataTypeArray(self, DataTypeArray i)
    cpdef void visitDataTypeBool(self, DataTypeBool i)
    cpdef void visitDataTypeChandle(self, DataTypeChandle i)
    cpdef void visitDataTypeEnum(self, DataTypeEnum i)
    cpdef void visitDataTypeInt(self, DataTypeInt i)
    cpdef void visitDataTypeString(self, DataTypeString i)
    cpdef void visitDataTypeUserDefined(self, DataTypeUserDefined i)
    cpdef void visitExprRefPathContext(self, ExprRefPathContext i)
    cpdef void visitExprRefPathStatic(self, ExprRefPathStatic i)
    cpdef void visitExprSignedNumber(self, ExprSignedNumber i)
    cpdef void visitExprUnsignedNumber(self, ExprUnsignedNumber i)
    cpdef void visitConstraintStmtForall(self, ConstraintStmtForall i)
    cpdef void visitConstraintStmtForeach(self, ConstraintStmtForeach i)
    cpdef void visitConstraintStmtImplication(self, ConstraintStmtImplication i)
    cpdef void visitTypeScope(self, TypeScope i)
    cpdef void visitExprRefPathStaticFunc(self, ExprRefPathStaticFunc i)
    cpdef void visitExprRefPathSuper(self, ExprRefPathSuper i)
    cpdef void visitAction(self, Action i)
    cpdef void visitComponent(self, Component i)
    cpdef void visitStruct(self, Struct i)
    cpdef void visitState(self, State i)
    cpdef void visitStream(self, Stream i)
    cpdef void visitBuffer(self, Buffer i)
    cpdef void visitResource(self, Resource i)
