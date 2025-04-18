/*
 * AstBuilderInt.h
 *
 *  Created on: Sep 13, 2020
 *      Author: ballance
 */

#pragma once
#include <memory>
#include <istream>
#include "dmgr/IDebugMgr.h"
#include "zsp/parser/IMarkerListener.h"
#include "PSSParserBaseVisitor.h"
#include "BaseErrorListener.h"
#include "zsp/ast/IExprId.h"
#include "zsp/ast/IFactory.h"
#include "zsp/ast/IGlobalScope.h"
#include "zsp/ast/IScope.h"

using namespace antlr4;
using namespace antlrcpp;

namespace zsp {
namespace parser {


class AstBuilderInt :
		public PSSParserBaseVisitor,
		public BaseErrorListener {
public:
	AstBuilderInt(
        dmgr::IDebugMgr         *dmgr,
		ast::IFactory			*factory,
		IMarkerListener 		*marker_l);

	virtual ~AstBuilderInt();

	void build(
			ast::IGlobalScope	*global,
			std::istream 		*in);

    zsp::ast::IFactory *getFactory() {
        return m_factory;
    }

    void setMarkerListener(IMarkerListener *l) {
        m_marker_l = l;
    }

    virtual void setCollectDocStrings(bool c) {
        m_collectDocStrings = c;
    }

    virtual bool getCollectDocStrings() {
        return m_collectDocStrings;
    }

    virtual void setEnableProfile(bool e) {
        m_enableProfile = e;
    }

    virtual bool getEnableProfile() {
        return m_enableProfile;
    }

	// B.1 package declaration
	virtual antlrcpp::Any visitPackage_declaration(PSSParser::Package_declarationContext *ctx) override;

	virtual antlrcpp::Any visitImport_stmt(PSSParser::Import_stmtContext *ctx) override;

    virtual antlrcpp::Any visitPyimport_single_module(PSSParser::Pyimport_single_moduleContext *ctx) override;

    virtual antlrcpp::Any visitPyimport_from_module(PSSParser::Pyimport_from_moduleContext *ctx) override;

	virtual antlrcpp::Any visitExtend_stmt(PSSParser::Extend_stmtContext *ctx) override;

	virtual antlrcpp::Any visitConst_field_declaration(PSSParser::Const_field_declarationContext *ctx) override;

	// B.2 Action declaration

	virtual antlrcpp::Any visitAction_declaration(PSSParser::Action_declarationContext *ctx) override;

	virtual antlrcpp::Any visitAbstract_action_declaration(PSSParser::Abstract_action_declarationContext *ctx);

    virtual antlrcpp::Any visitActivity_bind_stmt(PSSParser::Activity_bind_stmtContext *ctx) override;

    virtual antlrcpp::Any visitActivity_declaration(PSSParser::Activity_declarationContext *ctx) override;

	virtual antlrcpp::Any visitFlow_ref_field_declaration(PSSParser::Flow_ref_field_declarationContext *ctx) override;
	
	virtual antlrcpp::Any visitResource_ref_field_declaration(PSSParser::Resource_ref_field_declarationContext *ctx) override;

	virtual antlrcpp::Any visitActivity_data_field(PSSParser::Activity_data_fieldContext *ctx) override;

	// B.3 Struct declarations
	virtual antlrcpp::Any visitStruct_declaration(PSSParser::Struct_declarationContext *ctx) override;

	// B.4 Exec blocks
    virtual antlrcpp::Any visitExec_block(PSSParser::Exec_blockContext *ctx) override;

    virtual antlrcpp::Any visitTarget_code_exec_block(PSSParser::Target_code_exec_blockContext *ctx) override;

    virtual antlrcpp::Any visitTarget_file_exec_block(PSSParser::Target_file_exec_blockContext *ctx) override;

    virtual antlrcpp::Any visitExec_super_stmt(PSSParser::Exec_super_stmtContext *ctx) override;
    
	// B.5 Functions
    virtual antlrcpp::Any visitProcedural_function(PSSParser::Procedural_functionContext *ctx) override;

    virtual antlrcpp::Any visitFunction_decl(PSSParser::Function_declContext *ctx) override;

    virtual antlrcpp::Any visitFunction_prototype(PSSParser::Function_prototypeContext *ctx) override;

    virtual antlrcpp::Any visitImport_function(PSSParser::Import_functionContext *ctx) override;

	// B.7 Procedural Statements
    virtual antlrcpp::Any visitProcedural_sequence_block_stmt(PSSParser::Procedural_sequence_block_stmtContext *ctx) override;

    virtual antlrcpp::Any visitProcedural_assignment_stmt(PSSParser::Procedural_assignment_stmtContext *ctx) override;

    virtual antlrcpp::Any visitProcedural_void_function_call_stmt(PSSParser::Procedural_void_function_call_stmtContext *ctx) override;

    virtual antlrcpp::Any visitProcedural_return_stmt(PSSParser::Procedural_return_stmtContext *ctx) override;

    virtual antlrcpp::Any visitProcedural_repeat_stmt(PSSParser::Procedural_repeat_stmtContext *ctx) override;

    virtual antlrcpp::Any visitProcedural_foreach_stmt(PSSParser::Procedural_foreach_stmtContext *ctx) override;

    virtual antlrcpp::Any visitProcedural_if_else_stmt(PSSParser::Procedural_if_else_stmtContext *ctx) override;

    virtual antlrcpp::Any visitProcedural_match_stmt(PSSParser::Procedural_match_stmtContext *ctx) override;

    virtual antlrcpp::Any visitProcedural_break_stmt(PSSParser::Procedural_break_stmtContext *ctx) override;

    virtual antlrcpp::Any visitProcedural_continue_stmt(PSSParser::Procedural_continue_stmtContext *ctx) override;

    virtual antlrcpp::Any visitProcedural_data_declaration(PSSParser::Procedural_data_declarationContext *ctx) override;

    virtual antlrcpp::Any visitProcedural_yield_stmt(PSSParser::Procedural_yield_stmtContext *ctx) override;

	// B.8 Component declarations

	virtual antlrcpp::Any visitComponent_declaration(PSSParser::Component_declarationContext *ctx) override;

	// B.9 Activity statements

	virtual antlrcpp::Any visitActivity_labeled_stmt(PSSParser::Activity_labeled_stmtContext *ctx) override;

	virtual antlrcpp::Any visitActivity_action_traversal_stmt(PSSParser::Activity_action_traversal_stmtContext *ctx) override;

	virtual antlrcpp::Any visitActivity_sequence_block_stmt(PSSParser::Activity_sequence_block_stmtContext *ctx) override;

	virtual antlrcpp::Any visitActivity_parallel_stmt(PSSParser::Activity_parallel_stmtContext *ctx) override;

	virtual antlrcpp::Any visitActivity_schedule_stmt(PSSParser::Activity_schedule_stmtContext *ctx) override;

	virtual antlrcpp::Any visitActivity_repeat_stmt(PSSParser::Activity_repeat_stmtContext *ctx) override;

	// B.11 Data declarations

	virtual antlrcpp::Any visitData_declaration(PSSParser::Data_declarationContext *ctx) override;

	virtual antlrcpp::Any visitAttr_field(PSSParser::Attr_fieldContext *ctx) override;

	// B.13 Data types

 	virtual antlrcpp::Any visitChandle_type(PSSParser::Chandle_typeContext *ctx) override;

	virtual antlrcpp::Any visitInteger_type(PSSParser::Integer_typeContext *ctx) override;

    virtual antlrcpp::Any visitString_type(PSSParser::String_typeContext *context) override;

	virtual antlrcpp::Any visitBool_type(PSSParser::Bool_typeContext *ctx) override;

	virtual antlrcpp::Any visitEnum_type(PSSParser::Enum_typeContext *ctx) override;
	
    virtual antlrcpp::Any visitEnum_declaration(PSSParser::Enum_declarationContext *ctx) override;

    virtual antlrcpp::Any visitPyobj_type(PSSParser::Pyobj_typeContext *ctx) override;

	virtual antlrcpp::Any visitReference_type(PSSParser::Reference_typeContext *ctx) override;

	// B.14 Constraints
	virtual antlrcpp::Any visitConstraint_declaration(PSSParser::Constraint_declarationContext *ctx) override;

//	virtual antlrcpp::Any visitConstraint_set(PSSParser::Constraint_setContext *ctx) override;

	virtual antlrcpp::Any visitConstraint_block(PSSParser::Constraint_blockContext *ctx) override;

	virtual antlrcpp::Any visitDefault_constraint(PSSParser::Default_constraintContext *ctx) override;

	virtual antlrcpp::Any visitDefault_disable_constraint(PSSParser::Default_disable_constraintContext *ctx) override;

	virtual antlrcpp::Any visitExpression_constraint_item(PSSParser::Expression_constraint_itemContext *ctx) override;

	virtual antlrcpp::Any visitForeach_constraint_item(PSSParser::Foreach_constraint_itemContext *ctx) override;

	virtual antlrcpp::Any visitForall_constraint_item(PSSParser::Forall_constraint_itemContext *ctx) override;

	virtual antlrcpp::Any visitIf_constraint_item(PSSParser::If_constraint_itemContext *ctx) override;

	virtual antlrcpp::Any visitImplication_constraint_item(PSSParser::Implication_constraint_itemContext *ctx) override;
	
	virtual antlrcpp::Any visitUnique_constraint_item(PSSParser::Unique_constraint_itemContext *ctx) override;

	void visitConstraintSetItems(PSSParser::Constraint_setContext *ctx);

	// B.17 Expressions

	virtual antlrcpp::Any visitExpression(PSSParser::ExpressionContext *ctx) override;

	virtual antlrcpp::Any visitBool_literal(PSSParser::Bool_literalContext *ctx) override;

	virtual antlrcpp::Any visitString_literal(PSSParser::String_literalContext *ctx) override;

	virtual antlrcpp::Any visitNull_ref(PSSParser::Null_refContext *ctx) override;

	virtual antlrcpp::Any visitCast_expression(PSSParser::Cast_expressionContext *ctx) override;

	virtual antlrcpp::Any visitRef_path(PSSParser::Ref_pathContext *ctx) override;

	// B.18 Identifiers
	virtual antlrcpp::Any visitIdentifier(PSSParser::IdentifierContext *ctx) override;

    virtual antlrcpp::Any visitType_identifier(PSSParser::Type_identifierContext *context) override;


	// B.19 Numbers
	virtual antlrcpp::Any visitNumber(PSSParser::NumberContext *ctx) override;

    virtual antlrcpp::Any visitAggregate_literal(PSSParser::Aggregate_literalContext *ctx) override;

    virtual antlrcpp::Any visitEmpty_aggregate_literal(PSSParser::Empty_aggregate_literalContext *ctx) override;

    virtual antlrcpp::Any visitValue_list_literal(PSSParser::Value_list_literalContext *ctx) override;

    virtual antlrcpp::Any visitMap_literal(PSSParser::Map_literalContext *ctx) override;

    virtual antlrcpp::Any visitStruct_literal(PSSParser::Struct_literalContext *ctx) override;

    virtual void syntaxError(
    		Recognizer *recognizer,
			Token * offendingSymbol,
			size_t line,
			size_t charPositionInLine,
			const std::string &msg,
			std::exception_ptr e) override;


private:

    void addChild(ast::IScopeChild *c, Token *t, const ast::Location *loc=0, Token *ct=0);

    void addChild(ast::ISymbolScope *c, Token *t, Token *end);

    void addChild(ast::INamedScopeChild *c, Token *t);

    void addChild(ast::IConstraintScope *c, Token *start, Token *end);

    void addChild(ast::IExecScope *c, Token *start, Token *end);

    void addChild(ast::IFunctionDefinition *c, Token *start, Token *end);

    void addChild(ast::INamedScope *c, Token *start, Token *end);

    void addChild(ast::IScope *c, Token *start, Token *end);

    void addDocstring(ast::IScopeChild *c, Token *t);

    std::string processDocStringMultiLineComment(
    		const std::vector<Token *>		&mlc_tokens,
			const std::vector<Token *>		&ws_tokens);

    std::string processDocStringSingleLineComment(
    		const std::vector<Token *>		&slc_tokens,
			const std::vector<Token *>		&ws_tokens);

    ast::IScope *scope() const { return m_scopes.back(); }

    void push_scope(ast::IScope *s);

    void pop_scope();

	ast::IActivityJoinSpec *mkActivityJoinSpec(PSSParser::Activity_join_specContext *ctx);

    void addActivityStmt(
        ast::ISymbolScope                   *scope,
        PSSParser::Activity_stmt_annContext *ctx);

	ast::IScopeChild *mkActivityStmt(PSSParser::Activity_stmt_annContext *ctx);

	ast::IConstraintStmt *mkConstraintSet(PSSParser::Constraint_setContext *ctx);

	ast::IDataType *mkDataType(PSSParser::Data_typeContext *ctx);

	ast::IDataTypeUserDefined *mkDataTypeUserDefined(PSSParser::Type_identifierContext *ctx);

    ast::IDataTypeUserDefined *mkDataTypeArray(
        ast::IDataType          *elem_t,
        ast::IExpr              *size);

	template <class T> T *mkDataTypeT(PSSParser::Data_typeContext *ctx) {
		return dynamic_cast<T *>(mkDataType(ctx));
	}

	ast::IExprDomainOpenRangeList *mkDomainOpenRangeList(PSSParser::Domain_open_range_listContext *ctx);

    ast::IScopeChild *mkExecStmt(PSSParser::Procedural_stmtContext *ctx);

    void addExecStmt(PSSParser::Procedural_stmtContext *ctx);

    ast::IFunctionPrototype *mkFunctionPrototype(PSSParser::Function_prototypeContext *ctx);

    ast::IFunctionParamDecl *mkFunctionParamDecl(PSSParser::Function_parameterContext *ctx);

	ast::IExprId *mkId(PSSParser::IdentifierContext *ctx);

    std::string toString(PSSParser::IdentifierContext *ctx);

	ast::IExprHierarchicalId *mkHierarchicalId(PSSParser::Hierarchical_idContext *ctx);

	ast::IExprHierarchicalId *mkHierarchicalId(
        PSSParser::Static_ref_pathContext *root_ctx,
        PSSParser::Hierarchical_idContext *leaf_ctx);

	ast::IExprHierarchicalId *mkHierarchicalId(PSSParser::Member_path_elemContext *ctx);

    ast::IExprMemberPathElem *mkMemberPathElem(PSSParser::Member_path_elemContext *ctx);

	void mkTypeId(
		std::vector<ast::IExprIdUP>				&type_id,
		PSSParser::Type_identifierContext		*ctx);

	ast::ITypeIdentifier *mkTypeId(
		PSSParser::Type_identifierContext		*ctx);

	ast::ITypeIdentifierElem *mkTypeIdElem(
		PSSParser::Type_identifier_elemContext		*ctx);

	ast::ITypeIdentifierElem *mkTypeIdElem(
		PSSParser::IdentifierContext		    *ctx);

	ast::IExpr *mkExpr(
		PSSParser::ExpressionContext 			*ctx);

    ast::IExprBitSlice *mkExprBitSlice(
        PSSParser::Bit_sliceContext             *ctx);

    ast::IExprRefPath *mkExprRefPath(
        PSSParser::Ref_pathContext              *ctx);

    ast::IExprRefPathStatic *mkExprRefPathStatic(
        PSSParser::Static_ref_pathContext       *ctx);

    ast::ITemplateParamDeclList *mkTypeParamDecl(
        PSSParser::Template_param_decl_listContext *ctx);

    ast::ITemplateParamValueList *mkTemplateParamValueList(
        PSSParser::Template_param_value_listContext *ctx);

    void setLoc(ast::IScopeChild *c, Token *start);

    void setLoc(ast::IExprId *c, Token *start);

private:
    static dmgr::IDebug                         *m_dbg;
    int32_t                                     m_file_id;
	bool										m_collectDocStrings;
    bool                                        m_enableProfile;
    IMarkerListener								*m_marker_l;
	ast::IFactory								*m_factory;
	ast::IExpr									*m_expr;
	ast::IDataType								*m_type;
    std::vector<ast::IScope *>					m_scopes;
	ast::IScopeChild							*m_activity_stmt;
	ast::IExprId								*m_labeled_activity_id;
	ast::IConstraintStmt						*m_constraint;
    ast::IScopeChild                            *m_exec_stmt;
    int32_t                                     m_exec_stmt_cnt;
    std::vector<ast::IExecScope *>              m_exec_scope_s;
	std::vector<ast::IConstraintScope *>		m_constraint_s;
    std::unique_ptr<CommonTokenStream>			m_tokens;
	std::vector<ast::IExprIdUP>					*m_type_id;
	uint32_t									m_field_depth;
	std::vector<ast::IField *>					m_fields;

};

}
}

