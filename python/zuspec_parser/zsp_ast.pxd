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

from zuspec_parser cimport zsp_ast_decl
cdef class Factory(object):
    cdef zsp_ast_decl.IFactory *_hndl
    cpdef ScopeChild mkScopeChild(self)
    cpdef SymbolImportSpec mkSymbolImportSpec(self)
    cpdef ActivityJoinSpec mkActivityJoinSpec(self)
    cpdef RefExpr mkRefExpr(self)
    cpdef RefTarget mkRefTarget(self)
    cpdef TemplateParamDeclList mkTemplateParamDeclList(self)
    cpdef TemplateParamDecl mkTemplateParamDecl(self,
    ExprId name)
    cpdef ActivitySelectBranch mkActivitySelectBranch(self,
    Expr guard,
    Expr weight,
    ScopeChild body)
    cpdef TemplateParamValueList mkTemplateParamValueList(self)
    cpdef TemplateParamValue mkTemplateParamValue(self)
    cpdef ActivityMatchChoice mkActivityMatchChoice(self,
    bool is_default,
    ExprOpenRangeList cond,
    ScopeChild body)
    cpdef TemplateParamTypeValue mkTemplateParamTypeValue(self,
    TypeIdentifier value)
    cpdef TemplateParamExprValue mkTemplateParamExprValue(self,
    Expr value)
    cpdef ExecStmt mkExecStmt(self)
    cpdef Expr mkExpr(self)
    cpdef ActivityStmt mkActivityStmt(self)
    cpdef ActivitySchedulingConstraint mkActivitySchedulingConstraint(self,
    bool is_parallel)
    cpdef ActivityJoinSpecBranch mkActivityJoinSpecBranch(self)
    cpdef ActivityJoinSpecSelect mkActivityJoinSpecSelect(self,
    Expr count)
    cpdef ActivityJoinSpecNone mkActivityJoinSpecNone(self)
    cpdef ActivityJoinSpecFirst mkActivityJoinSpecFirst(self,
    Expr count)
    cpdef ConstraintStmt mkConstraintStmt(self)
    cpdef Scope mkScope(self)
    cpdef ScopeChildRef mkScopeChildRef(self,
    ScopeChild target)
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
    DataType casting_type,
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
    cpdef ExprNull mkExprNull(self)
    cpdef ExprNumber mkExprNumber(self)
    cpdef ExprAggregateLiteral mkExprAggregateLiteral(self)
    cpdef ExprOpenRangeList mkExprOpenRangeList(self)
    cpdef ExprOpenRangeValue mkExprOpenRangeValue(self,
    Expr lhs,
    Expr rhs)
    cpdef ExprRefPath mkExprRefPath(self)
    cpdef ExprRefPathContext mkExprRefPathContext(self,
    ExprHierarchicalId hier_id)
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
    cpdef ExtendEnum mkExtendEnum(self,
    TypeIdentifier target)
    cpdef SymbolScope mkSymbolScope(self,
    int32_t id,
    std_string name)
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
    cpdef ActivityBindStmt mkActivityBindStmt(self,
    ExprHierarchicalId lhs)
    cpdef ActivityConstraint mkActivityConstraint(self,
    ConstraintStmt constraint)
    cpdef ActivityLabeledStmt mkActivityLabeledStmt(self)
    cpdef ActivityLabeledScope mkActivityLabeledScope(self)
    cpdef ConstraintScope mkConstraintScope(self)
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
    cpdef ConstraintStmtDefault mkConstraintStmtDefault(self,
    ExprHierarchicalId hid,
    Expr expr)
    cpdef ConstraintStmtDefaultDisable mkConstraintStmtDefaultDisable(self,
    ExprHierarchicalId hid)
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
    cpdef EnumItem mkEnumItem(self,
    ExprId name,
    Expr value)
    cpdef EnumDecl mkEnumDecl(self,
    ExprId name)
    cpdef DataTypeInt mkDataTypeInt(self,
    bool is_signed,
    Expr width,
    ExprDomainOpenRangeList in_range)
    cpdef DataTypeRef mkDataTypeRef(self,
    DataTypeUserDefined type)
    cpdef DataTypeString mkDataTypeString(self,
    bool has_range)
    cpdef DataTypeUserDefined mkDataTypeUserDefined(self,
    bool is_global,
    TypeIdentifier type_id)
    cpdef ExprRefPathStatic mkExprRefPathStatic(self,
    bool is_global,
    ExprBitSlice slice)
    cpdef ExprRefPathSuper mkExprRefPathSuper(self,
    ExprHierarchicalId hier_id)
    cpdef ExprSignedNumber mkExprSignedNumber(self,
    std_string image,
    int32_t width,
    int64_t value)
    cpdef ExprUnsignedNumber mkExprUnsignedNumber(self,
    std_string image,
    int32_t width,
    uint64_t value)
    cpdef ExtendType mkExtendType(self,
     kind,
    TypeIdentifier target)
    cpdef Field mkField(self,
    ExprId name,
    DataType type,
     attr,
    Expr array_dim,
    Expr init)
    cpdef FieldRef mkFieldRef(self,
    ExprId name,
    DataTypeUserDefined type,
    Expr array_dim,
    bool is_input)
    cpdef FieldClaim mkFieldClaim(self,
    ExprId name,
    DataTypeUserDefined type,
    Expr array_dim,
    bool is_lock)
    cpdef SymbolTypeScope mkSymbolTypeScope(self,
    int32_t id,
    std_string name,
    SymbolScope plist)
    cpdef SymbolFunctionScope mkSymbolFunctionScope(self,
    int32_t id,
    std_string name,
    SymbolScope plist)
    cpdef ActivityActionHandleTraversal mkActivityActionHandleTraversal(self,
    ExprRefPathContext target,
    ConstraintStmt with_c)
    cpdef ActivityActionTypeTraversal mkActivityActionTypeTraversal(self,
    DataTypeUserDefined target,
    ConstraintStmt with_c)
    cpdef ActivitySequence mkActivitySequence(self)
    cpdef ActivityParallel mkActivityParallel(self,
    ActivityJoinSpec join_spec)
    cpdef ActivitySchedule mkActivitySchedule(self,
    ActivityJoinSpec join_spec)
    cpdef ActivityRepeatCount mkActivityRepeatCount(self,
    ExprId loop_var,
    Expr count,
    ScopeChild body)
    cpdef ActivityRepeatWhile mkActivityRepeatWhile(self,
    Expr cond,
    ScopeChild body)
    cpdef ActivityForeach mkActivityForeach(self,
    ExprId it_id,
    ExprId idx_id,
    ExprRefPathContext target,
    ScopeChild body)
    cpdef ActivitySelect mkActivitySelect(self)
    cpdef ActivityIfElse mkActivityIfElse(self,
    Expr cond,
    ActivityStmt true_s,
    ActivityStmt false_s)
    cpdef ActivityMatch mkActivityMatch(self,
    Expr cond)
    cpdef ActivityReplicate mkActivityReplicate(self,
    ExprId idx_id,
    ExprId it_label,
    ScopeChild body)
    cpdef ActivitySuper mkActivitySuper(self)
    cpdef ConstraintBlock mkConstraintBlock(self,
    std_string name,
    bool is_dynamic)
    cpdef ConstraintStmtForeach mkConstraintStmtForeach(self,
    Expr expr)
    cpdef ConstraintStmtForall mkConstraintStmtForall(self,
    ExprId iterator_id,
    DataTypeUserDefined type_id,
    ExprRefPath ref_path)
    cpdef ConstraintStmtImplication mkConstraintStmtImplication(self,
    Expr cond)
    cpdef ExprRefPathStaticFunc mkExprRefPathStaticFunc(self,
    bool is_global,
    ExprBitSlice slice,
    MethodParameterList params)
    cpdef TypeScope mkTypeScope(self,
    ExprId name,
    TypeIdentifier super_t)
    cpdef Component mkComponent(self,
    ExprId name,
    TypeIdentifier super_t)
    cpdef Struct mkStruct(self,
    ExprId name,
    TypeIdentifier super_t,
     kind)
    cpdef Action mkAction(self,
    ExprId name,
    TypeIdentifier super_t,
    bool is_abstract)
    @staticmethod
    cdef mk(zsp_ast_decl.IFactory *hndl)
cdef class ScopeChild(object):
    cdef zsp_ast_decl.IScopeChild    *_hndl
    cdef bool           _owned
    
    cpdef void accept(self, VisitorBase v)
    cdef zsp_ast_decl.IScopeChild *asScopeChild(self)
    @staticmethod
    cdef ScopeChild mk(zsp_ast_decl.IScopeChild *hndl, bool owned)
    cpdef std_string getDocstring(self)
    cpdef int32_t getIndex(self)

cdef class SymbolImportSpec(object):
    cdef zsp_ast_decl.ISymbolImportSpec    *_hndl
    cdef bool           _owned
    
    cpdef void accept(self, VisitorBase v)
    cdef zsp_ast_decl.ISymbolImportSpec *asSymbolImportSpec(self)
    @staticmethod
    cdef SymbolImportSpec mk(zsp_ast_decl.ISymbolImportSpec *hndl, bool owned)

cdef class ActivityJoinSpec(object):
    cdef zsp_ast_decl.IActivityJoinSpec    *_hndl
    cdef bool           _owned
    
    cpdef void accept(self, VisitorBase v)
    cdef zsp_ast_decl.IActivityJoinSpec *asActivityJoinSpec(self)
    @staticmethod
    cdef ActivityJoinSpec mk(zsp_ast_decl.IActivityJoinSpec *hndl, bool owned)

cdef class RefExpr(object):
    cdef zsp_ast_decl.IRefExpr    *_hndl
    cdef bool           _owned
    
    cpdef void accept(self, VisitorBase v)
    cdef zsp_ast_decl.IRefExpr *asRefExpr(self)
    @staticmethod
    cdef RefExpr mk(zsp_ast_decl.IRefExpr *hndl, bool owned)

cdef class RefTarget(object):
    cdef zsp_ast_decl.IRefTarget    *_hndl
    cdef bool           _owned
    
    cpdef void accept(self, VisitorBase v)
    cdef zsp_ast_decl.IRefTarget *asRefTarget(self)
    @staticmethod
    cdef RefTarget mk(zsp_ast_decl.IRefTarget *hndl, bool owned)

cdef class TemplateParamDeclList(object):
    cdef zsp_ast_decl.ITemplateParamDeclList    *_hndl
    cdef bool           _owned
    
    cpdef void accept(self, VisitorBase v)
    cdef zsp_ast_decl.ITemplateParamDeclList *asTemplateParamDeclList(self)
    @staticmethod
    cdef TemplateParamDeclList mk(zsp_ast_decl.ITemplateParamDeclList *hndl, bool owned)

cdef class TemplateParamDecl(object):
    cdef zsp_ast_decl.ITemplateParamDecl    *_hndl
    cdef bool           _owned
    
    cpdef void accept(self, VisitorBase v)
    cdef zsp_ast_decl.ITemplateParamDecl *asTemplateParamDecl(self)
    @staticmethod
    cdef TemplateParamDecl mk(zsp_ast_decl.ITemplateParamDecl *hndl, bool owned)

cdef class ActivitySelectBranch(object):
    cdef zsp_ast_decl.IActivitySelectBranch    *_hndl
    cdef bool           _owned
    
    cpdef void accept(self, VisitorBase v)
    cdef zsp_ast_decl.IActivitySelectBranch *asActivitySelectBranch(self)
    @staticmethod
    cdef ActivitySelectBranch mk(zsp_ast_decl.IActivitySelectBranch *hndl, bool owned)

cdef class TemplateParamValueList(object):
    cdef zsp_ast_decl.ITemplateParamValueList    *_hndl
    cdef bool           _owned
    
    cpdef void accept(self, VisitorBase v)
    cdef zsp_ast_decl.ITemplateParamValueList *asTemplateParamValueList(self)
    @staticmethod
    cdef TemplateParamValueList mk(zsp_ast_decl.ITemplateParamValueList *hndl, bool owned)

cdef class TemplateParamValue(object):
    cdef zsp_ast_decl.ITemplateParamValue    *_hndl
    cdef bool           _owned
    
    cpdef void accept(self, VisitorBase v)
    cdef zsp_ast_decl.ITemplateParamValue *asTemplateParamValue(self)
    @staticmethod
    cdef TemplateParamValue mk(zsp_ast_decl.ITemplateParamValue *hndl, bool owned)

cdef class ActivityMatchChoice(object):
    cdef zsp_ast_decl.IActivityMatchChoice    *_hndl
    cdef bool           _owned
    
    cpdef void accept(self, VisitorBase v)
    cdef zsp_ast_decl.IActivityMatchChoice *asActivityMatchChoice(self)
    @staticmethod
    cdef ActivityMatchChoice mk(zsp_ast_decl.IActivityMatchChoice *hndl, bool owned)
    cpdef bool getIs_default(self)

cdef class TemplateParamTypeValue(object):
    cdef zsp_ast_decl.ITemplateParamTypeValue    *_hndl
    cdef bool           _owned
    
    cpdef void accept(self, VisitorBase v)
    cdef zsp_ast_decl.ITemplateParamTypeValue *asTemplateParamTypeValue(self)
    @staticmethod
    cdef TemplateParamTypeValue mk(zsp_ast_decl.ITemplateParamTypeValue *hndl, bool owned)

cdef class TemplateParamExprValue(object):
    cdef zsp_ast_decl.ITemplateParamExprValue    *_hndl
    cdef bool           _owned
    
    cpdef void accept(self, VisitorBase v)
    cdef zsp_ast_decl.ITemplateParamExprValue *asTemplateParamExprValue(self)
    @staticmethod
    cdef TemplateParamExprValue mk(zsp_ast_decl.ITemplateParamExprValue *hndl, bool owned)

cdef class ExecStmt(object):
    cdef zsp_ast_decl.IExecStmt    *_hndl
    cdef bool           _owned
    
    cpdef void accept(self, VisitorBase v)
    cdef zsp_ast_decl.IExecStmt *asExecStmt(self)
    @staticmethod
    cdef ExecStmt mk(zsp_ast_decl.IExecStmt *hndl, bool owned)

cdef class Expr(object):
    cdef zsp_ast_decl.IExpr    *_hndl
    cdef bool           _owned
    
    cpdef void accept(self, VisitorBase v)
    cdef zsp_ast_decl.IExpr *asExpr(self)
    @staticmethod
    cdef Expr mk(zsp_ast_decl.IExpr *hndl, bool owned)

cdef class ActivityStmt(ScopeChild):
    
    cdef zsp_ast_decl.IActivityStmt *asActivityStmt(self)
    @staticmethod
    cdef ActivityStmt mk(zsp_ast_decl.IActivityStmt *hndl, bool owned)

cdef class ActivitySchedulingConstraint(ScopeChild):
    
    cdef zsp_ast_decl.IActivitySchedulingConstraint *asActivitySchedulingConstraint(self)
    @staticmethod
    cdef ActivitySchedulingConstraint mk(zsp_ast_decl.IActivitySchedulingConstraint *hndl, bool owned)
    cpdef bool getIs_parallel(self)

cdef class ActivityJoinSpecBranch(ActivityJoinSpec):
    
    cdef zsp_ast_decl.IActivityJoinSpecBranch *asActivityJoinSpecBranch(self)
    @staticmethod
    cdef ActivityJoinSpecBranch mk(zsp_ast_decl.IActivityJoinSpecBranch *hndl, bool owned)

cdef class ActivityJoinSpecSelect(ActivityJoinSpec):
    
    cdef zsp_ast_decl.IActivityJoinSpecSelect *asActivityJoinSpecSelect(self)
    @staticmethod
    cdef ActivityJoinSpecSelect mk(zsp_ast_decl.IActivityJoinSpecSelect *hndl, bool owned)

cdef class ActivityJoinSpecNone(ActivityJoinSpec):
    
    cdef zsp_ast_decl.IActivityJoinSpecNone *asActivityJoinSpecNone(self)
    @staticmethod
    cdef ActivityJoinSpecNone mk(zsp_ast_decl.IActivityJoinSpecNone *hndl, bool owned)

cdef class ActivityJoinSpecFirst(ActivityJoinSpec):
    
    cdef zsp_ast_decl.IActivityJoinSpecFirst *asActivityJoinSpecFirst(self)
    @staticmethod
    cdef ActivityJoinSpecFirst mk(zsp_ast_decl.IActivityJoinSpecFirst *hndl, bool owned)

cdef class ConstraintStmt(ScopeChild):
    
    cdef zsp_ast_decl.IConstraintStmt *asConstraintStmt(self)
    @staticmethod
    cdef ConstraintStmt mk(zsp_ast_decl.IConstraintStmt *hndl, bool owned)

cdef class Scope(ScopeChild):
    
    cdef zsp_ast_decl.IScope *asScope(self)
    @staticmethod
    cdef Scope mk(zsp_ast_decl.IScope *hndl, bool owned)

cdef class ScopeChildRef(ScopeChild):
    
    cdef zsp_ast_decl.IScopeChildRef *asScopeChildRef(self)
    @staticmethod
    cdef ScopeChildRef mk(zsp_ast_decl.IScopeChildRef *hndl, bool owned)

cdef class NamedScopeChild(ScopeChild):
    
    cdef zsp_ast_decl.INamedScopeChild *asNamedScopeChild(self)
    @staticmethod
    cdef NamedScopeChild mk(zsp_ast_decl.INamedScopeChild *hndl, bool owned)

cdef class PackageImportStmt(ScopeChild):
    
    cdef zsp_ast_decl.IPackageImportStmt *asPackageImportStmt(self)
    @staticmethod
    cdef PackageImportStmt mk(zsp_ast_decl.IPackageImportStmt *hndl, bool owned)
    cpdef bool getWildcard(self)

cdef class DataType(ScopeChild):
    
    cdef zsp_ast_decl.IDataType *asDataType(self)
    @staticmethod
    cdef DataType mk(zsp_ast_decl.IDataType *hndl, bool owned)

cdef class ExecScope(ExecStmt):
    
    cdef zsp_ast_decl.IExecScope *asExecScope(self)
    @staticmethod
    cdef ExecScope mk(zsp_ast_decl.IExecScope *hndl, bool owned)

cdef class ProceduralStmtDataDeclaration(ExecStmt):
    
    cdef zsp_ast_decl.IProceduralStmtDataDeclaration *asProceduralStmtDataDeclaration(self)
    @staticmethod
    cdef ProceduralStmtDataDeclaration mk(zsp_ast_decl.IProceduralStmtDataDeclaration *hndl, bool owned)

cdef class ExprBin(Expr):
    
    cdef zsp_ast_decl.IExprBin *asExprBin(self)
    @staticmethod
    cdef ExprBin mk(zsp_ast_decl.IExprBin *hndl, bool owned)
    cpdef  getOp(self)

cdef class ExprBitSlice(Expr):
    
    cdef zsp_ast_decl.IExprBitSlice *asExprBitSlice(self)
    @staticmethod
    cdef ExprBitSlice mk(zsp_ast_decl.IExprBitSlice *hndl, bool owned)

cdef class ExprBool(Expr):
    
    cdef zsp_ast_decl.IExprBool *asExprBool(self)
    @staticmethod
    cdef ExprBool mk(zsp_ast_decl.IExprBool *hndl, bool owned)
    cpdef bool getValue(self)

cdef class ExprCast(Expr):
    
    cdef zsp_ast_decl.IExprCast *asExprCast(self)
    @staticmethod
    cdef ExprCast mk(zsp_ast_decl.IExprCast *hndl, bool owned)

cdef class ExprCompileHas(Expr):
    
    cdef zsp_ast_decl.IExprCompileHas *asExprCompileHas(self)
    @staticmethod
    cdef ExprCompileHas mk(zsp_ast_decl.IExprCompileHas *hndl, bool owned)

cdef class ExprCond(Expr):
    
    cdef zsp_ast_decl.IExprCond *asExprCond(self)
    @staticmethod
    cdef ExprCond mk(zsp_ast_decl.IExprCond *hndl, bool owned)

cdef class ExprDomainOpenRangeList(Expr):
    
    cdef zsp_ast_decl.IExprDomainOpenRangeList *asExprDomainOpenRangeList(self)
    @staticmethod
    cdef ExprDomainOpenRangeList mk(zsp_ast_decl.IExprDomainOpenRangeList *hndl, bool owned)

cdef class ExprDomainOpenRangeValue(Expr):
    
    cdef zsp_ast_decl.IExprDomainOpenRangeValue *asExprDomainOpenRangeValue(self)
    @staticmethod
    cdef ExprDomainOpenRangeValue mk(zsp_ast_decl.IExprDomainOpenRangeValue *hndl, bool owned)
    cpdef bool getSingle(self)

cdef class ExprHierarchicalId(Expr):
    
    cdef zsp_ast_decl.IExprHierarchicalId *asExprHierarchicalId(self)
    @staticmethod
    cdef ExprHierarchicalId mk(zsp_ast_decl.IExprHierarchicalId *hndl, bool owned)

cdef class ExprId(Expr):
    
    cdef zsp_ast_decl.IExprId *asExprId(self)
    @staticmethod
    cdef ExprId mk(zsp_ast_decl.IExprId *hndl, bool owned)
    cpdef std_string getId(self)
    cpdef bool getIs_escaped(self)

cdef class ExprIn(Expr):
    
    cdef zsp_ast_decl.IExprIn *asExprIn(self)
    @staticmethod
    cdef ExprIn mk(zsp_ast_decl.IExprIn *hndl, bool owned)

cdef class ExprMemberPathElem(Expr):
    
    cdef zsp_ast_decl.IExprMemberPathElem *asExprMemberPathElem(self)
    @staticmethod
    cdef ExprMemberPathElem mk(zsp_ast_decl.IExprMemberPathElem *hndl, bool owned)
    cpdef int32_t getTarget(self)

cdef class ExprNull(Expr):
    
    cdef zsp_ast_decl.IExprNull *asExprNull(self)
    @staticmethod
    cdef ExprNull mk(zsp_ast_decl.IExprNull *hndl, bool owned)

cdef class ExprNumber(Expr):
    
    cdef zsp_ast_decl.IExprNumber *asExprNumber(self)
    @staticmethod
    cdef ExprNumber mk(zsp_ast_decl.IExprNumber *hndl, bool owned)

cdef class ExprAggregateLiteral(Expr):
    
    cdef zsp_ast_decl.IExprAggregateLiteral *asExprAggregateLiteral(self)
    @staticmethod
    cdef ExprAggregateLiteral mk(zsp_ast_decl.IExprAggregateLiteral *hndl, bool owned)

cdef class ExprOpenRangeList(Expr):
    
    cdef zsp_ast_decl.IExprOpenRangeList *asExprOpenRangeList(self)
    @staticmethod
    cdef ExprOpenRangeList mk(zsp_ast_decl.IExprOpenRangeList *hndl, bool owned)

cdef class ExprOpenRangeValue(Expr):
    
    cdef zsp_ast_decl.IExprOpenRangeValue *asExprOpenRangeValue(self)
    @staticmethod
    cdef ExprOpenRangeValue mk(zsp_ast_decl.IExprOpenRangeValue *hndl, bool owned)

cdef class ExprRefPath(Expr):
    
    cdef zsp_ast_decl.IExprRefPath *asExprRefPath(self)
    @staticmethod
    cdef ExprRefPath mk(zsp_ast_decl.IExprRefPath *hndl, bool owned)

cdef class ExprRefPathContext(Expr):
    
    cdef zsp_ast_decl.IExprRefPathContext *asExprRefPathContext(self)
    @staticmethod
    cdef ExprRefPathContext mk(zsp_ast_decl.IExprRefPathContext *hndl, bool owned)

cdef class ExprRefPathElem(Expr):
    
    cdef zsp_ast_decl.IExprRefPathElem *asExprRefPathElem(self)
    @staticmethod
    cdef ExprRefPathElem mk(zsp_ast_decl.IExprRefPathElem *hndl, bool owned)

cdef class ExprRefPathStaticRooted(Expr):
    
    cdef zsp_ast_decl.IExprRefPathStaticRooted *asExprRefPathStaticRooted(self)
    @staticmethod
    cdef ExprRefPathStaticRooted mk(zsp_ast_decl.IExprRefPathStaticRooted *hndl, bool owned)

cdef class ExprStaticRefPath(Expr):
    
    cdef zsp_ast_decl.IExprStaticRefPath *asExprStaticRefPath(self)
    @staticmethod
    cdef ExprStaticRefPath mk(zsp_ast_decl.IExprStaticRefPath *hndl, bool owned)
    cpdef bool getIs_global(self)

cdef class ExprString(Expr):
    
    cdef zsp_ast_decl.IExprString *asExprString(self)
    @staticmethod
    cdef ExprString mk(zsp_ast_decl.IExprString *hndl, bool owned)
    cpdef std_string getValue(self)
    cpdef bool getIs_raw(self)

cdef class ExprSubscript(Expr):
    
    cdef zsp_ast_decl.IExprSubscript *asExprSubscript(self)
    @staticmethod
    cdef ExprSubscript mk(zsp_ast_decl.IExprSubscript *hndl, bool owned)

cdef class ExprUnary(Expr):
    
    cdef zsp_ast_decl.IExprUnary *asExprUnary(self)
    @staticmethod
    cdef ExprUnary mk(zsp_ast_decl.IExprUnary *hndl, bool owned)
    cpdef  getOp(self)

cdef class MethodParameterList(Expr):
    
    cdef zsp_ast_decl.IMethodParameterList *asMethodParameterList(self)
    @staticmethod
    cdef MethodParameterList mk(zsp_ast_decl.IMethodParameterList *hndl, bool owned)

cdef class TypeIdentifier(Expr):
    
    cdef zsp_ast_decl.ITypeIdentifier *asTypeIdentifier(self)
    @staticmethod
    cdef TypeIdentifier mk(zsp_ast_decl.ITypeIdentifier *hndl, bool owned)

cdef class TypeIdentifierElem(Expr):
    
    cdef zsp_ast_decl.ITypeIdentifierElem *asTypeIdentifierElem(self)
    @staticmethod
    cdef TypeIdentifierElem mk(zsp_ast_decl.ITypeIdentifierElem *hndl, bool owned)

cdef class ExtendEnum(ScopeChild):
    
    cdef zsp_ast_decl.IExtendEnum *asExtendEnum(self)
    @staticmethod
    cdef ExtendEnum mk(zsp_ast_decl.IExtendEnum *hndl, bool owned)

cdef class SymbolScope(ScopeChild):
    
    cdef zsp_ast_decl.ISymbolScope *asSymbolScope(self)
    @staticmethod
    cdef SymbolScope mk(zsp_ast_decl.ISymbolScope *hndl, bool owned)
    cpdef int32_t getId(self)
    cpdef std_string getName(self)

cdef class RefExprTypeScopeGlobal(RefExpr):
    
    cdef zsp_ast_decl.IRefExprTypeScopeGlobal *asRefExprTypeScopeGlobal(self)
    @staticmethod
    cdef RefExprTypeScopeGlobal mk(zsp_ast_decl.IRefExprTypeScopeGlobal *hndl, bool owned)
    cpdef int32_t getFileid(self)

cdef class RefExprTypeScopeContext(RefExpr):
    
    cdef zsp_ast_decl.IRefExprTypeScopeContext *asRefExprTypeScopeContext(self)
    @staticmethod
    cdef RefExprTypeScopeContext mk(zsp_ast_decl.IRefExprTypeScopeContext *hndl, bool owned)
    cpdef int32_t getOffset(self)

cdef class RefExprScopeIndex(RefExpr):
    
    cdef zsp_ast_decl.IRefExprScopeIndex *asRefExprScopeIndex(self)
    @staticmethod
    cdef RefExprScopeIndex mk(zsp_ast_decl.IRefExprScopeIndex *hndl, bool owned)
    cpdef int32_t getOffset(self)

cdef class TemplateGenericTypeParamDecl(TemplateParamDecl):
    
    cdef zsp_ast_decl.ITemplateGenericTypeParamDecl *asTemplateGenericTypeParamDecl(self)
    @staticmethod
    cdef TemplateGenericTypeParamDecl mk(zsp_ast_decl.ITemplateGenericTypeParamDecl *hndl, bool owned)

cdef class TemplateCategoryTypeParamDecl(TemplateParamDecl):
    
    cdef zsp_ast_decl.ITemplateCategoryTypeParamDecl *asTemplateCategoryTypeParamDecl(self)
    @staticmethod
    cdef TemplateCategoryTypeParamDecl mk(zsp_ast_decl.ITemplateCategoryTypeParamDecl *hndl, bool owned)
    cpdef  getCategory(self)

cdef class TemplateValueParamDecl(TemplateParamDecl):
    
    cdef zsp_ast_decl.ITemplateValueParamDecl *asTemplateValueParamDecl(self)
    @staticmethod
    cdef TemplateValueParamDecl mk(zsp_ast_decl.ITemplateValueParamDecl *hndl, bool owned)

cdef class ActivityBindStmt(ActivityStmt):
    
    cdef zsp_ast_decl.IActivityBindStmt *asActivityBindStmt(self)
    @staticmethod
    cdef ActivityBindStmt mk(zsp_ast_decl.IActivityBindStmt *hndl, bool owned)

cdef class ActivityConstraint(ActivityStmt):
    
    cdef zsp_ast_decl.IActivityConstraint *asActivityConstraint(self)
    @staticmethod
    cdef ActivityConstraint mk(zsp_ast_decl.IActivityConstraint *hndl, bool owned)

cdef class ActivityLabeledStmt(ActivityStmt):
    
    cdef zsp_ast_decl.IActivityLabeledStmt *asActivityLabeledStmt(self)
    @staticmethod
    cdef ActivityLabeledStmt mk(zsp_ast_decl.IActivityLabeledStmt *hndl, bool owned)

cdef class ActivityLabeledScope(Scope):
    
    cdef zsp_ast_decl.IActivityLabeledScope *asActivityLabeledScope(self)
    @staticmethod
    cdef ActivityLabeledScope mk(zsp_ast_decl.IActivityLabeledScope *hndl, bool owned)

cdef class ConstraintScope(ConstraintStmt):
    
    cdef zsp_ast_decl.IConstraintScope *asConstraintScope(self)
    @staticmethod
    cdef ConstraintScope mk(zsp_ast_decl.IConstraintScope *hndl, bool owned)

cdef class ConstraintStmtExpr(ConstraintStmt):
    
    cdef zsp_ast_decl.IConstraintStmtExpr *asConstraintStmtExpr(self)
    @staticmethod
    cdef ConstraintStmtExpr mk(zsp_ast_decl.IConstraintStmtExpr *hndl, bool owned)

cdef class ConstraintStmtField(ConstraintStmt):
    
    cdef zsp_ast_decl.IConstraintStmtField *asConstraintStmtField(self)
    @staticmethod
    cdef ConstraintStmtField mk(zsp_ast_decl.IConstraintStmtField *hndl, bool owned)

cdef class ConstraintStmtIf(ConstraintStmt):
    
    cdef zsp_ast_decl.IConstraintStmtIf *asConstraintStmtIf(self)
    @staticmethod
    cdef ConstraintStmtIf mk(zsp_ast_decl.IConstraintStmtIf *hndl, bool owned)

cdef class ConstraintStmtUnique(ConstraintStmt):
    
    cdef zsp_ast_decl.IConstraintStmtUnique *asConstraintStmtUnique(self)
    @staticmethod
    cdef ConstraintStmtUnique mk(zsp_ast_decl.IConstraintStmtUnique *hndl, bool owned)

cdef class ConstraintStmtDefault(ConstraintStmt):
    
    cdef zsp_ast_decl.IConstraintStmtDefault *asConstraintStmtDefault(self)
    @staticmethod
    cdef ConstraintStmtDefault mk(zsp_ast_decl.IConstraintStmtDefault *hndl, bool owned)

cdef class ConstraintStmtDefaultDisable(ConstraintStmt):
    
    cdef zsp_ast_decl.IConstraintStmtDefaultDisable *asConstraintStmtDefaultDisable(self)
    @staticmethod
    cdef ConstraintStmtDefaultDisable mk(zsp_ast_decl.IConstraintStmtDefaultDisable *hndl, bool owned)

cdef class GlobalScope(Scope):
    
    cdef zsp_ast_decl.IGlobalScope *asGlobalScope(self)
    @staticmethod
    cdef GlobalScope mk(zsp_ast_decl.IGlobalScope *hndl, bool owned)
    cpdef int32_t getFileid(self)

cdef class NamedScope(Scope):
    
    cdef zsp_ast_decl.INamedScope *asNamedScope(self)
    @staticmethod
    cdef NamedScope mk(zsp_ast_decl.INamedScope *hndl, bool owned)

cdef class PackageScope(Scope):
    
    cdef zsp_ast_decl.IPackageScope *asPackageScope(self)
    @staticmethod
    cdef PackageScope mk(zsp_ast_decl.IPackageScope *hndl, bool owned)

cdef class DataTypeArray(DataType):
    
    cdef zsp_ast_decl.IDataTypeArray *asDataTypeArray(self)
    @staticmethod
    cdef DataTypeArray mk(zsp_ast_decl.IDataTypeArray *hndl, bool owned)

cdef class DataTypeBool(DataType):
    
    cdef zsp_ast_decl.IDataTypeBool *asDataTypeBool(self)
    @staticmethod
    cdef DataTypeBool mk(zsp_ast_decl.IDataTypeBool *hndl, bool owned)

cdef class DataTypeChandle(DataType):
    
    cdef zsp_ast_decl.IDataTypeChandle *asDataTypeChandle(self)
    @staticmethod
    cdef DataTypeChandle mk(zsp_ast_decl.IDataTypeChandle *hndl, bool owned)

cdef class DataTypeEnum(DataType):
    
    cdef zsp_ast_decl.IDataTypeEnum *asDataTypeEnum(self)
    @staticmethod
    cdef DataTypeEnum mk(zsp_ast_decl.IDataTypeEnum *hndl, bool owned)

cdef class EnumItem(NamedScopeChild):
    
    cdef zsp_ast_decl.IEnumItem *asEnumItem(self)
    @staticmethod
    cdef EnumItem mk(zsp_ast_decl.IEnumItem *hndl, bool owned)

cdef class EnumDecl(NamedScopeChild):
    
    cdef zsp_ast_decl.IEnumDecl *asEnumDecl(self)
    @staticmethod
    cdef EnumDecl mk(zsp_ast_decl.IEnumDecl *hndl, bool owned)

cdef class DataTypeInt(DataType):
    
    cdef zsp_ast_decl.IDataTypeInt *asDataTypeInt(self)
    @staticmethod
    cdef DataTypeInt mk(zsp_ast_decl.IDataTypeInt *hndl, bool owned)
    cpdef bool getIs_signed(self)

cdef class DataTypeRef(DataType):
    
    cdef zsp_ast_decl.IDataTypeRef *asDataTypeRef(self)
    @staticmethod
    cdef DataTypeRef mk(zsp_ast_decl.IDataTypeRef *hndl, bool owned)

cdef class DataTypeString(DataType):
    
    cdef zsp_ast_decl.IDataTypeString *asDataTypeString(self)
    @staticmethod
    cdef DataTypeString mk(zsp_ast_decl.IDataTypeString *hndl, bool owned)
    cpdef bool getHas_range(self)

cdef class DataTypeUserDefined(DataType):
    
    cdef zsp_ast_decl.IDataTypeUserDefined *asDataTypeUserDefined(self)
    @staticmethod
    cdef DataTypeUserDefined mk(zsp_ast_decl.IDataTypeUserDefined *hndl, bool owned)
    cpdef bool getIs_global(self)

cdef class ExprRefPathStatic(ExprRefPath):
    
    cdef zsp_ast_decl.IExprRefPathStatic *asExprRefPathStatic(self)
    @staticmethod
    cdef ExprRefPathStatic mk(zsp_ast_decl.IExprRefPathStatic *hndl, bool owned)
    cpdef bool getIs_global(self)

cdef class ExprRefPathSuper(ExprRefPathContext):
    
    cdef zsp_ast_decl.IExprRefPathSuper *asExprRefPathSuper(self)
    @staticmethod
    cdef ExprRefPathSuper mk(zsp_ast_decl.IExprRefPathSuper *hndl, bool owned)

cdef class ExprSignedNumber(ExprNumber):
    
    cdef zsp_ast_decl.IExprSignedNumber *asExprSignedNumber(self)
    @staticmethod
    cdef ExprSignedNumber mk(zsp_ast_decl.IExprSignedNumber *hndl, bool owned)
    cpdef std_string getImage(self)
    cpdef int32_t getWidth(self)
    cpdef int64_t getValue(self)

cdef class ExprUnsignedNumber(ExprNumber):
    
    cdef zsp_ast_decl.IExprUnsignedNumber *asExprUnsignedNumber(self)
    @staticmethod
    cdef ExprUnsignedNumber mk(zsp_ast_decl.IExprUnsignedNumber *hndl, bool owned)
    cpdef std_string getImage(self)
    cpdef int32_t getWidth(self)
    cpdef uint64_t getValue(self)

cdef class ExtendType(Scope):
    
    cdef zsp_ast_decl.IExtendType *asExtendType(self)
    @staticmethod
    cdef ExtendType mk(zsp_ast_decl.IExtendType *hndl, bool owned)
    cpdef  getKind(self)

cdef class Field(NamedScopeChild):
    
    cdef zsp_ast_decl.IField *asField(self)
    @staticmethod
    cdef Field mk(zsp_ast_decl.IField *hndl, bool owned)
    cpdef  getAttr(self)

cdef class FieldRef(NamedScopeChild):
    
    cdef zsp_ast_decl.IFieldRef *asFieldRef(self)
    @staticmethod
    cdef FieldRef mk(zsp_ast_decl.IFieldRef *hndl, bool owned)
    cpdef bool getIs_input(self)

cdef class FieldClaim(NamedScopeChild):
    
    cdef zsp_ast_decl.IFieldClaim *asFieldClaim(self)
    @staticmethod
    cdef FieldClaim mk(zsp_ast_decl.IFieldClaim *hndl, bool owned)
    cpdef bool getIs_lock(self)

cdef class SymbolTypeScope(SymbolScope):
    
    cdef zsp_ast_decl.ISymbolTypeScope *asSymbolTypeScope(self)
    @staticmethod
    cdef SymbolTypeScope mk(zsp_ast_decl.ISymbolTypeScope *hndl, bool owned)

cdef class SymbolFunctionScope(SymbolScope):
    
    cdef zsp_ast_decl.ISymbolFunctionScope *asSymbolFunctionScope(self)
    @staticmethod
    cdef SymbolFunctionScope mk(zsp_ast_decl.ISymbolFunctionScope *hndl, bool owned)

cdef class ActivityActionHandleTraversal(ActivityLabeledStmt):
    
    cdef zsp_ast_decl.IActivityActionHandleTraversal *asActivityActionHandleTraversal(self)
    @staticmethod
    cdef ActivityActionHandleTraversal mk(zsp_ast_decl.IActivityActionHandleTraversal *hndl, bool owned)

cdef class ActivityActionTypeTraversal(ActivityLabeledStmt):
    
    cdef zsp_ast_decl.IActivityActionTypeTraversal *asActivityActionTypeTraversal(self)
    @staticmethod
    cdef ActivityActionTypeTraversal mk(zsp_ast_decl.IActivityActionTypeTraversal *hndl, bool owned)

cdef class ActivitySequence(ActivityLabeledScope):
    
    cdef zsp_ast_decl.IActivitySequence *asActivitySequence(self)
    @staticmethod
    cdef ActivitySequence mk(zsp_ast_decl.IActivitySequence *hndl, bool owned)

cdef class ActivityParallel(ActivityLabeledScope):
    
    cdef zsp_ast_decl.IActivityParallel *asActivityParallel(self)
    @staticmethod
    cdef ActivityParallel mk(zsp_ast_decl.IActivityParallel *hndl, bool owned)

cdef class ActivitySchedule(ActivityLabeledScope):
    
    cdef zsp_ast_decl.IActivitySchedule *asActivitySchedule(self)
    @staticmethod
    cdef ActivitySchedule mk(zsp_ast_decl.IActivitySchedule *hndl, bool owned)

cdef class ActivityRepeatCount(ActivityLabeledStmt):
    
    cdef zsp_ast_decl.IActivityRepeatCount *asActivityRepeatCount(self)
    @staticmethod
    cdef ActivityRepeatCount mk(zsp_ast_decl.IActivityRepeatCount *hndl, bool owned)

cdef class ActivityRepeatWhile(ActivityLabeledStmt):
    
    cdef zsp_ast_decl.IActivityRepeatWhile *asActivityRepeatWhile(self)
    @staticmethod
    cdef ActivityRepeatWhile mk(zsp_ast_decl.IActivityRepeatWhile *hndl, bool owned)

cdef class ActivityForeach(ActivityLabeledStmt):
    
    cdef zsp_ast_decl.IActivityForeach *asActivityForeach(self)
    @staticmethod
    cdef ActivityForeach mk(zsp_ast_decl.IActivityForeach *hndl, bool owned)

cdef class ActivitySelect(ActivityLabeledStmt):
    
    cdef zsp_ast_decl.IActivitySelect *asActivitySelect(self)
    @staticmethod
    cdef ActivitySelect mk(zsp_ast_decl.IActivitySelect *hndl, bool owned)

cdef class ActivityIfElse(ActivityLabeledStmt):
    
    cdef zsp_ast_decl.IActivityIfElse *asActivityIfElse(self)
    @staticmethod
    cdef ActivityIfElse mk(zsp_ast_decl.IActivityIfElse *hndl, bool owned)

cdef class ActivityMatch(ActivityLabeledStmt):
    
    cdef zsp_ast_decl.IActivityMatch *asActivityMatch(self)
    @staticmethod
    cdef ActivityMatch mk(zsp_ast_decl.IActivityMatch *hndl, bool owned)

cdef class ActivityReplicate(ActivityLabeledStmt):
    
    cdef zsp_ast_decl.IActivityReplicate *asActivityReplicate(self)
    @staticmethod
    cdef ActivityReplicate mk(zsp_ast_decl.IActivityReplicate *hndl, bool owned)

cdef class ActivitySuper(ActivityLabeledStmt):
    
    cdef zsp_ast_decl.IActivitySuper *asActivitySuper(self)
    @staticmethod
    cdef ActivitySuper mk(zsp_ast_decl.IActivitySuper *hndl, bool owned)

cdef class ConstraintBlock(ConstraintScope):
    
    cdef zsp_ast_decl.IConstraintBlock *asConstraintBlock(self)
    @staticmethod
    cdef ConstraintBlock mk(zsp_ast_decl.IConstraintBlock *hndl, bool owned)
    cpdef std_string getName(self)
    cpdef bool getIs_dynamic(self)

cdef class ConstraintStmtForeach(ConstraintScope):
    
    cdef zsp_ast_decl.IConstraintStmtForeach *asConstraintStmtForeach(self)
    @staticmethod
    cdef ConstraintStmtForeach mk(zsp_ast_decl.IConstraintStmtForeach *hndl, bool owned)

cdef class ConstraintStmtForall(ConstraintScope):
    
    cdef zsp_ast_decl.IConstraintStmtForall *asConstraintStmtForall(self)
    @staticmethod
    cdef ConstraintStmtForall mk(zsp_ast_decl.IConstraintStmtForall *hndl, bool owned)

cdef class ConstraintStmtImplication(ConstraintScope):
    
    cdef zsp_ast_decl.IConstraintStmtImplication *asConstraintStmtImplication(self)
    @staticmethod
    cdef ConstraintStmtImplication mk(zsp_ast_decl.IConstraintStmtImplication *hndl, bool owned)

cdef class ExprRefPathStaticFunc(ExprRefPathStatic):
    
    cdef zsp_ast_decl.IExprRefPathStaticFunc *asExprRefPathStaticFunc(self)
    @staticmethod
    cdef ExprRefPathStaticFunc mk(zsp_ast_decl.IExprRefPathStaticFunc *hndl, bool owned)

cdef class TypeScope(NamedScope):
    
    cdef zsp_ast_decl.ITypeScope *asTypeScope(self)
    @staticmethod
    cdef TypeScope mk(zsp_ast_decl.ITypeScope *hndl, bool owned)

cdef class Component(TypeScope):
    
    cdef zsp_ast_decl.IComponent *asComponent(self)
    @staticmethod
    cdef Component mk(zsp_ast_decl.IComponent *hndl, bool owned)

cdef class Struct(TypeScope):
    
    cdef zsp_ast_decl.IStruct *asStruct(self)
    @staticmethod
    cdef Struct mk(zsp_ast_decl.IStruct *hndl, bool owned)
    cpdef  getKind(self)

cdef class Action(TypeScope):
    
    cdef zsp_ast_decl.IAction *asAction(self)
    @staticmethod
    cdef Action mk(zsp_ast_decl.IAction *hndl, bool owned)
    cpdef bool getIs_abstract(self)

cdef class VisitorBase(object):
    cdef zsp_ast_decl.PyBaseVisitor *_hndl
    cdef bool                  _owned
    cpdef void visitScopeChild(self, ScopeChild i)
    cpdef void visitSymbolImportSpec(self, SymbolImportSpec i)
    cpdef void visitActivityJoinSpec(self, ActivityJoinSpec i)
    cpdef void visitRefExpr(self, RefExpr i)
    cpdef void visitRefTarget(self, RefTarget i)
    cpdef void visitTemplateParamDeclList(self, TemplateParamDeclList i)
    cpdef void visitTemplateParamDecl(self, TemplateParamDecl i)
    cpdef void visitActivitySelectBranch(self, ActivitySelectBranch i)
    cpdef void visitTemplateParamValueList(self, TemplateParamValueList i)
    cpdef void visitTemplateParamValue(self, TemplateParamValue i)
    cpdef void visitActivityMatchChoice(self, ActivityMatchChoice i)
    cpdef void visitTemplateParamTypeValue(self, TemplateParamTypeValue i)
    cpdef void visitTemplateParamExprValue(self, TemplateParamExprValue i)
    cpdef void visitExecStmt(self, ExecStmt i)
    cpdef void visitExpr(self, Expr i)
    cpdef void visitActivityStmt(self, ActivityStmt i)
    cpdef void visitActivitySchedulingConstraint(self, ActivitySchedulingConstraint i)
    cpdef void visitActivityJoinSpecBranch(self, ActivityJoinSpecBranch i)
    cpdef void visitActivityJoinSpecSelect(self, ActivityJoinSpecSelect i)
    cpdef void visitActivityJoinSpecNone(self, ActivityJoinSpecNone i)
    cpdef void visitActivityJoinSpecFirst(self, ActivityJoinSpecFirst i)
    cpdef void visitConstraintStmt(self, ConstraintStmt i)
    cpdef void visitScope(self, Scope i)
    cpdef void visitScopeChildRef(self, ScopeChildRef i)
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
    cpdef void visitExprNull(self, ExprNull i)
    cpdef void visitExprNumber(self, ExprNumber i)
    cpdef void visitExprAggregateLiteral(self, ExprAggregateLiteral i)
    cpdef void visitExprOpenRangeList(self, ExprOpenRangeList i)
    cpdef void visitExprOpenRangeValue(self, ExprOpenRangeValue i)
    cpdef void visitExprRefPath(self, ExprRefPath i)
    cpdef void visitExprRefPathContext(self, ExprRefPathContext i)
    cpdef void visitExprRefPathElem(self, ExprRefPathElem i)
    cpdef void visitExprRefPathStaticRooted(self, ExprRefPathStaticRooted i)
    cpdef void visitExprStaticRefPath(self, ExprStaticRefPath i)
    cpdef void visitExprString(self, ExprString i)
    cpdef void visitExprSubscript(self, ExprSubscript i)
    cpdef void visitExprUnary(self, ExprUnary i)
    cpdef void visitMethodParameterList(self, MethodParameterList i)
    cpdef void visitTypeIdentifier(self, TypeIdentifier i)
    cpdef void visitTypeIdentifierElem(self, TypeIdentifierElem i)
    cpdef void visitExtendEnum(self, ExtendEnum i)
    cpdef void visitSymbolScope(self, SymbolScope i)
    cpdef void visitRefExprTypeScopeGlobal(self, RefExprTypeScopeGlobal i)
    cpdef void visitRefExprTypeScopeContext(self, RefExprTypeScopeContext i)
    cpdef void visitRefExprScopeIndex(self, RefExprScopeIndex i)
    cpdef void visitTemplateGenericTypeParamDecl(self, TemplateGenericTypeParamDecl i)
    cpdef void visitTemplateCategoryTypeParamDecl(self, TemplateCategoryTypeParamDecl i)
    cpdef void visitTemplateValueParamDecl(self, TemplateValueParamDecl i)
    cpdef void visitActivityBindStmt(self, ActivityBindStmt i)
    cpdef void visitActivityConstraint(self, ActivityConstraint i)
    cpdef void visitActivityLabeledStmt(self, ActivityLabeledStmt i)
    cpdef void visitActivityLabeledScope(self, ActivityLabeledScope i)
    cpdef void visitConstraintScope(self, ConstraintScope i)
    cpdef void visitConstraintStmtExpr(self, ConstraintStmtExpr i)
    cpdef void visitConstraintStmtField(self, ConstraintStmtField i)
    cpdef void visitConstraintStmtIf(self, ConstraintStmtIf i)
    cpdef void visitConstraintStmtUnique(self, ConstraintStmtUnique i)
    cpdef void visitConstraintStmtDefault(self, ConstraintStmtDefault i)
    cpdef void visitConstraintStmtDefaultDisable(self, ConstraintStmtDefaultDisable i)
    cpdef void visitGlobalScope(self, GlobalScope i)
    cpdef void visitNamedScope(self, NamedScope i)
    cpdef void visitPackageScope(self, PackageScope i)
    cpdef void visitDataTypeArray(self, DataTypeArray i)
    cpdef void visitDataTypeBool(self, DataTypeBool i)
    cpdef void visitDataTypeChandle(self, DataTypeChandle i)
    cpdef void visitDataTypeEnum(self, DataTypeEnum i)
    cpdef void visitEnumItem(self, EnumItem i)
    cpdef void visitEnumDecl(self, EnumDecl i)
    cpdef void visitDataTypeInt(self, DataTypeInt i)
    cpdef void visitDataTypeRef(self, DataTypeRef i)
    cpdef void visitDataTypeString(self, DataTypeString i)
    cpdef void visitDataTypeUserDefined(self, DataTypeUserDefined i)
    cpdef void visitExprRefPathStatic(self, ExprRefPathStatic i)
    cpdef void visitExprRefPathSuper(self, ExprRefPathSuper i)
    cpdef void visitExprSignedNumber(self, ExprSignedNumber i)
    cpdef void visitExprUnsignedNumber(self, ExprUnsignedNumber i)
    cpdef void visitExtendType(self, ExtendType i)
    cpdef void visitField(self, Field i)
    cpdef void visitFieldRef(self, FieldRef i)
    cpdef void visitFieldClaim(self, FieldClaim i)
    cpdef void visitSymbolTypeScope(self, SymbolTypeScope i)
    cpdef void visitSymbolFunctionScope(self, SymbolFunctionScope i)
    cpdef void visitActivityActionHandleTraversal(self, ActivityActionHandleTraversal i)
    cpdef void visitActivityActionTypeTraversal(self, ActivityActionTypeTraversal i)
    cpdef void visitActivitySequence(self, ActivitySequence i)
    cpdef void visitActivityParallel(self, ActivityParallel i)
    cpdef void visitActivitySchedule(self, ActivitySchedule i)
    cpdef void visitActivityRepeatCount(self, ActivityRepeatCount i)
    cpdef void visitActivityRepeatWhile(self, ActivityRepeatWhile i)
    cpdef void visitActivityForeach(self, ActivityForeach i)
    cpdef void visitActivitySelect(self, ActivitySelect i)
    cpdef void visitActivityIfElse(self, ActivityIfElse i)
    cpdef void visitActivityMatch(self, ActivityMatch i)
    cpdef void visitActivityReplicate(self, ActivityReplicate i)
    cpdef void visitActivitySuper(self, ActivitySuper i)
    cpdef void visitConstraintBlock(self, ConstraintBlock i)
    cpdef void visitConstraintStmtForeach(self, ConstraintStmtForeach i)
    cpdef void visitConstraintStmtForall(self, ConstraintStmtForall i)
    cpdef void visitConstraintStmtImplication(self, ConstraintStmtImplication i)
    cpdef void visitExprRefPathStaticFunc(self, ExprRefPathStaticFunc i)
    cpdef void visitTypeScope(self, TypeScope i)
    cpdef void visitComponent(self, Component i)
    cpdef void visitStruct(self, Struct i)
    cpdef void visitAction(self, Action i)
