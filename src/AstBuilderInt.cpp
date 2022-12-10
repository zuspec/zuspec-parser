/*
 * AstBuilderInt.cpp
 *
 *  Created on: Sep 13, 2020
 *      Author: ballance
 */

#include <vector>
#include "AstBuilderInt.h"
#include "PSSLexer.h"
#include "zsp/ast/IFactory.h"
#include "zsp/ast/IAction.h"
#include "zsp/ast/IComponent.h"
#include "zsp/ast/IExprId.h"
#include "zsp/ast/INamedScope.h"
#include "zsp/ast/IPackageImportStmt.h"
#include "zsp/ast/Location.h"
#include "ScopeUtil.h"
#include "Marker.h"

#define DEBUG_ENTER(fmt, ...) \
	fprintf(stdout, "--> AstBuilderInt::"); \
	fprintf(stdout, fmt, #__VA_ARGS__); \
	fprintf(stdout, "\n")

#define DEBUG(fmt, ...) \
	fprintf(stdout, "AstBuilderInt: "); \
	fprintf(stdout, fmt, #__VA_ARGS__); \
	fprintf(stdout, "\n")

#define DEBUG_LEAVE(fmt, ...) \
	fprintf(stdout, "<-- AstBuilderInt::"); \
	fprintf(stdout, fmt, #__VA_ARGS__); \
	fprintf(stdout, "\n")


namespace zsp {

using namespace ast;

AstBuilderInt::AstBuilderInt(
	ast::IFactory		*factory,
	IMarkerListener 	*marker_l) : m_factory(factory), m_marker_l(marker_l) {
	// TODO Auto-generated constructor stub

}

AstBuilderInt::~AstBuilderInt() {
	// TODO Auto-generated destructor stub
}

void AstBuilderInt::build(
			ast::IGlobalScope		*global,
			std::istream 			*in) {
	ANTLRInputStream input(*in);
	PSSLexer lexer(&input);
	m_tokens = std::unique_ptr<CommonTokenStream>(new CommonTokenStream(&lexer));
	PSSParser parser(m_tokens.get());

	parser.removeErrorListeners();
	parser.addErrorListener(this);

	PSSParser::Compilation_unitContext *ctx = parser.compilation_unit();

	// Only proceed to build out the AST if there are no syntax errors
	if (!m_marker_l->hasSeverity(MarkerSeverityE::Error)) {
		push_scope(global);
		ctx->accept(this);
		pop_scope();
	}
}

antlrcpp::Any AstBuilderInt::visitPackage_declaration(
	PSSParser::Package_declarationContext *ctx) {
	IPackageScope *pkg = m_factory->mkPackageScope();

	// TODO: populate Id list
	fprintf(stdout, "%d elements in package_identifier\n",
		ctx->package_id_path()->package_identifier().size());
	/*
	for (std::vector<PSSParser::Package_identifierContext *>::const_iterator
		it=ctx->package_id_path()->package_identifier().begin();
		it!=ctx->package_id_path()->package_identifier().end(); it++) {
		PSSParser::Package_identifierContext *id = (*it);
		pkg->getId().push_back(IExprIdUP(mkId(id->identifier())));
	}
	 */

	addChild(pkg);
	push_scope(pkg);
	std::vector<PSSParser::Package_body_itemContext *> items = ctx->package_body_item();
	for (std::vector<PSSParser::Package_body_itemContext *>::const_iterator
		it=items.begin();
		it!=items.end(); it++) {
		(*it)->accept(this);
	}
	pop_scope();

	return 0;
}

antlrcpp::Any AstBuilderInt::visitImport_stmt(PSSParser::Import_stmtContext *ctx) {
	bool is_wildcard = false;
	IExprId *alias = 0;
	
	if (ctx->package_import_pattern()->package_import_qualifier()) {
		if (ctx->package_import_pattern()->package_import_qualifier()->package_import_wildcard()) {
			is_wildcard = true;
		} else {
			alias = mkId(ctx->package_import_pattern()->package_import_qualifier()->
				package_import_alias()->package_identifier()->identifier());
		}
	}

	IPackageImportStmt *imp = m_factory->mkPackageImportStmt(is_wildcard, alias);

	std::vector<PSSParser::Type_identifier_elemContext *> elems = 
		ctx->package_import_pattern()->type_identifier()->type_identifier_elem();
//	mkTypeId(imp->getPath(), ctx->package_import_pattern()->type_identifier());
	for (std::vector<PSSParser::Type_identifier_elemContext *>::const_iterator
		it=elems.begin();
		it!=elems.end(); it++) {
		imp->getPath().push_back(IExprIdUP(mkId((*it)->identifier())));
	}
	addChild(imp);


	return 0;
}

static std::map<std::string,ast::StructKind> StructKind_m = {
	{"struct", ast::StructKind::Struct},
	{"buffer", ast::StructKind::Buffer},
	{"resource", ast::StructKind::Resource},
	{"state", ast::StructKind::State},
	{"stream", ast::StructKind::Stream}
};

antlrcpp::Any AstBuilderInt::visitStruct_declaration(PSSParser::Struct_declarationContext *ctx) {
	DEBUG_ENTER("visitStruct_declaration");
	ast::IExprId *id = mkId(ctx->identifier());

	ast::ITypeIdentifier *super_t = 0;

	PSSParser::Struct_super_specContext *super_t_ctx = ctx->struct_super_spec();
	if (super_t_ctx) {
		super_t = mkTypeId(super_t_ctx->type_identifier());
	}
	ast::IStruct *s = m_factory->mkStruct(
		id,
		super_t,
		StructKind_m.find(ctx->struct_kind()->toString())->second);

	m_scopes.back()->getChildren().push_back(ast::IScopeChildUP(s));
	s->setParent(m_scopes.back());
	m_scopes.push_back(s);
	std::vector<PSSParser::Struct_body_itemContext *> body = ctx->struct_body_item();
	for (std::vector<PSSParser::Struct_body_itemContext *>::const_iterator
		it=body.begin();
		it!=body.end(); it++) {
		(*it)->accept(this);
	}

	m_scopes.pop_back();

	DEBUG_LEAVE("visitStruct_declaration");
	return 0;
}

// B.9 Activity statements
antlrcpp::Any AstBuilderInt::visitActivity_action_traversal_stmt(PSSParser::Activity_action_traversal_stmtContext *ctx) {
	DEBUG_ENTER("visitActivity_action_traversal_stmt");
	DEBUG("TODO: skipping activity traversal statement");
	DEBUG_LEAVE("visitActivity_action_traversal_stmt");
	return 0;
}

// B.13 Data types
antlrcpp::Any AstBuilderInt::visitChandle_type(PSSParser::Chandle_typeContext *ctx) {
	DEBUG_ENTER("visitChandle_type");
	m_type = m_factory->mkDataTypeChandle();
	DEBUG_LEAVE("visitChandle_type");
	return 0;
}

antlrcpp::Any AstBuilderInt::visitInteger_type(PSSParser::Integer_typeContext *ctx) {
	DEBUG_ENTER("visitInteger_type");

	ast::IExpr *width = 0;
	ast::IExprDomainOpenRangeList *in = 0;

	if (ctx->lhs) {
		ctx->lhs->accept(this);
		width = m_expr;
	}

	if (ctx->is_in) {
		in = mkDomainOpenRangeList(ctx->domain);
	}

	ast::IDataTypeInt *type = m_factory->mkDataTypeInt(
		ctx->integer_atom_type()->TOK_INT(),
		width,
		in
	);

	m_type = type;

	DEBUG_LEAVE("visitInteger_type");
	return 0;
}

antlrcpp::Any AstBuilderInt::visitBool_type(PSSParser::Bool_typeContext *ctx) {
	DEBUG_ENTER("visitBool_type");
	m_type = m_factory->mkDataTypeBool();
	DEBUG_LEAVE("visitBool_type");
	return 0;
}

antlrcpp::Any AstBuilderInt::visitEnum_type(PSSParser::Enum_typeContext *ctx) {
	DEBUG_ENTER("visitEnum_type");
	ctx->enum_type_identifier()->accept(this);
	ast::IDataTypeUserDefined *dt = dynamic_cast<ast::IDataTypeUserDefined *>(m_type);
	ast::IExprOpenRangeList *in = 0;

	if (ctx->TOK_IN()) {
		ctx->open_range_list()->accept(this);
		in = dynamic_cast<ast::IExprOpenRangeList*>(m_expr);
	}

	ast::IDataTypeEnum *type_enum = m_factory->mkDataTypeEnum(dt, in);

	m_type = type_enum;
	DEBUG_LEAVE("visitEnum_type");
	return 0;
}

antlrcpp::Any AstBuilderInt::visitEnum_declaration(PSSParser::Enum_declarationContext *ctx) {
	DEBUG_ENTER("visitEnum_declaration");

	ast::IEnumDecl *decl = m_factory->mkEnumDecl(mkId(ctx->enum_identifier()->identifier()));

	std::vector<PSSParser::Enum_itemContext *> items = ctx->enum_item();
	for (std::vector<PSSParser::Enum_itemContext *>::const_iterator
		it=items.begin();
		it!=items.end(); it++) {
		ast::IExpr *value = 0;

		if ((*it)->constant_expression()) {
			(*it)->constant_expression()->accept(this);
			value = m_expr;
		}

		ast::IEnumItem *item = m_factory->mkEnumItem(
			mkId((*it)->identifier()),
			value);
		decl->getItems().push_back(ast::IEnumItemUP(item));
	}

	m_scopes.back()->getChildren().push_back(ast::IScopeChildUP(decl));

	DEBUG_LEAVE("visitEnum_declaration");
	return 0;
}

antlrcpp::Any AstBuilderInt::visitReference_type(PSSParser::Reference_typeContext *ctx) {
	DEBUG_ENTER("visitReference_type");

	ast::IDataTypeUserDefined *type = 0;
	ctx->entity_type_identifier()->accept(this);
	type = dynamic_cast<ast::IDataTypeUserDefined *>(m_type);

	ast::IDataTypeRef *ref = m_factory->mkDataTypeRef(type);

	m_type = ref;
	DEBUG_LEAVE("visitReference_type");
	return 0;
}


// B.14 Constraints
antlrcpp::Any AstBuilderInt::visitConstraint_declaration(PSSParser::Constraint_declarationContext *ctx) {
	DEBUG_ENTER("visitConstraint_declaration");
	std::string name;

	if (ctx->identifier()) {
		name = ctx->identifier()->toString();
	}

	ast::IConstraintBlock *constraint = m_factory->mkConstraintBlock(
		name,
		ctx->is_dynamic);

	m_scopes.back()->getChildren().push_back(ast::IScopeChildUP(constraint));
	m_constraint_s.push_back(constraint);

	if (ctx->constraint_set()) {
		ctx->constraint_set()->accept(this);
	} else {
		std::vector<PSSParser::Constraint_body_itemContext *> items = 
			ctx->constraint_block()->constraint_body_item();
		for (std::vector<PSSParser::Constraint_body_itemContext *>::const_iterator
			it=items.begin();
			it!=items.end(); it++) {
			(*it)->accept(this);
		}
	}

	m_constraint_s.pop_back();

	DEBUG_LEAVE("visitConstraint_declaration");
	return 0;
}

// antlrcpp::Any AstBuilderInt::visitConstraint_set(PSSParser::Constraint_setContext *ctx) {
// 	DEBUG_ENTER("visitConstraint_set");

// 	if (ctx->constraint_body_item()) {
// 		ctx->constraint_body_item()->accept(this);
// 	} else {
// 		ctx->constraint_block()->accept(this);
// 	}

// 	DEBUG_LEAVE("visitConstraint_set");
// 	return 0;
// }

antlrcpp::Any AstBuilderInt::visitConstraint_block(PSSParser::Constraint_blockContext *ctx) {
	DEBUG_ENTER("visitConstraint_block");

	ast::IConstraintScope *scope = m_factory->mkConstraintScope();
	m_constraint_s.back()->getConstraints().push_back(ast::IConstraintStmtUP(scope));
//	scope->setParent(m_constraint_s.back());
	m_constraint_s.push_back(scope);
	std::vector<PSSParser::Constraint_body_itemContext *> items = ctx->constraint_body_item();
	for (std::vector<PSSParser::Constraint_body_itemContext *>::const_iterator
		it=items.begin();
		it!=items.end(); it++) {
		(*it)->accept(this);
	}
	m_constraint_s.pop_back();

	DEBUG_LEAVE("visitConstraint_block");
	return 0;
}

antlrcpp::Any AstBuilderInt::visitDefault_constraint(PSSParser::Default_constraintContext *ctx) {
	DEBUG_ENTER("visitDefault_constraint");
	DEBUG("TODO");
	DEBUG_LEAVE("visitDefault_constraint");
	return 0;
}

antlrcpp::Any AstBuilderInt::visitDefault_disable_constraint(PSSParser::Default_disable_constraintContext *ctx) {
	DEBUG_ENTER("visitDefault_disable_constraint");
	DEBUG("TODO");
	DEBUG_LEAVE("visitDefault_disable_constraint");
	return 0;
}

antlrcpp::Any AstBuilderInt::visitExpression_constraint_item(PSSParser::Expression_constraint_itemContext *ctx) {
	DEBUG_ENTER("visitExpression_constraint_item");
	ast::IConstraintStmtExpr *c = m_factory->mkConstraintStmtExpr(
		mkExpr(ctx->expression()));
	m_constraint_s.back()->getConstraints().push_back(ast::IConstraintStmtUP(c));
	DEBUG_LEAVE("visitExpression_constraint_item");
	return 0;
}

antlrcpp::Any AstBuilderInt::visitForeach_constraint_item(PSSParser::Foreach_constraint_itemContext *ctx) {
	DEBUG_ENTER("visitForeach_constraint_item");
	ast::IConstraintStmtForeach *c = m_factory->mkConstraintStmtForeach(
		mkExpr(ctx->expression()));
	
	if (ctx->it_id) {
		ast::IConstraintStmtField *it = m_factory->mkConstraintStmtField(
			mkId(ctx->it_id->identifier()),
			0 // TODO: what do we do about datatype here?
		);
		c->setIt(it);
		c->getConstraints().push_back(ast::IConstraintStmtUP(it));
	}

	if (ctx->idx_id) {
		ast::IConstraintStmtField *idx = m_factory->mkConstraintStmtField(
			mkId(ctx->idx_id->identifier()),
			0 // TODO: 
		);
		c->setIdx(idx);
		c->getConstraints().push_back(ast::IConstraintStmtUP(idx));
	}

	m_constraint_s.back()->getConstraints().push_back(ast::IConstraintScopeUP(c));
	m_constraint_s.push_back(c);
	visitConstraintSetItems(ctx->constraint_set());
	m_constraint_s.pop_back();
	DEBUG_LEAVE("visitForeach_constraint_item");
	return 0;
}

antlrcpp::Any AstBuilderInt::visitForall_constraint_item(PSSParser::Forall_constraint_itemContext *ctx) {
	DEBUG_ENTER("visitForall_constraint_item");
	DEBUG("TODO");
	DEBUG_LEAVE("visitForall_constraint_item");
	return 0;

}

antlrcpp::Any AstBuilderInt::visitIf_constraint_item(PSSParser::If_constraint_itemContext *ctx) {
	DEBUG_ENTER("visitIf_constraint_item");
	ast::IExpr *cond = mkExpr(ctx->expression());
	ast::IConstraintScope *true_c = m_factory->mkConstraintScope();
	ast::IConstraintScope *false_c = 0;
	m_constraint_s.push_back(true_c);
	visitConstraintSetItems(ctx->constraint_set(0));
	m_constraint_s.pop_back();

	if (ctx->constraint_set(1)) {
		false_c = m_factory->mkConstraintScope();
		m_constraint_s.push_back(false_c);
		visitConstraintSetItems(ctx->constraint_set(1));
		m_constraint_s.pop_back();
	}

	IConstraintStmtIf *c = m_factory->mkConstraintStmtIf(
		cond,
		true_c,
		false_c);

	m_constraint_s.back()->getConstraints().push_back(
		IConstraintStmtUP(c));

	DEBUG_LEAVE("visitIf_constraint_item");
	return 0;
}

antlrcpp::Any AstBuilderInt::visitImplication_constraint_item(PSSParser::Implication_constraint_itemContext *ctx) {
	DEBUG_ENTER("visitImplication_constraint_item");
	ast::IConstraintStmtImplication *c = m_factory->mkConstraintStmtImplication(mkExpr(ctx->expression()));

	m_constraint_s.back()->getConstraints().push_back(ast::IConstraintStmtUP(c));
	m_constraint_s.push_back(c);
	visitConstraintSetItems(ctx->constraint_set());
	m_constraint_s.pop_back();

	DEBUG_LEAVE("visitImplication_constraint_item");
	return 0;
}

antlrcpp::Any AstBuilderInt::visitUnique_constraint_item(PSSParser::Unique_constraint_itemContext *ctx) {
	DEBUG_ENTER("visitUnique_constraint_item");
	ast::IConstraintStmtUnique *c = m_factory->mkConstraintStmtUnique();

	std::vector<PSSParser::Hierarchical_idContext *> items = 
		ctx->hierarchical_id_list()->hierarchical_id();
	
	for (std::vector<PSSParser::Hierarchical_idContext *>::const_iterator
		it=items.begin();
		it!=items.end(); it++) {
		ast::IExprHierarchicalId *hid = mkHierarchicalId(*it);
		c->getList().push_back(ast::IExprHierarchicalIdUP(hid));
	}

	DEBUG_LEAVE("visitUnique_constraint_item");
	return 0;
}

void AstBuilderInt::visitConstraintSetItems(PSSParser::Constraint_setContext *ctx) {
	DEBUG_ENTER("visitConstraintSetItems");

	if (ctx->constraint_body_item()) {
		ctx->constraint_body_item()->accept(this);
	} else {
		std::vector<PSSParser::Constraint_body_itemContext *> items =
			ctx->constraint_block()->constraint_body_item();
		for (std::vector<PSSParser::Constraint_body_itemContext *>::const_iterator
			it=items.begin();
			it!=items.end(); it++) {
			(*it)->accept(this);
		}
	}

	DEBUG_LEAVE("visitConstraintSetItems");
}

// B.17 Expressions

static std::map<std::string, ast::ExprUnaryOp> prv_str2unop = {

};

static std::map<std::string, ast::ExprBinOp> prv_str2binop = {
	{"||", ast::ExprBinOp::BinOp_LogOr},
	{"&&", ast::ExprBinOp::BinOp_LogAnd},
	{"|", ast::ExprBinOp::BinOp_BitOr},
	{"^", ast::ExprBinOp::BinOp_BitXor},
	{"&", ast::ExprBinOp::BinOp_BitAnd},
	{"<", ast::ExprBinOp::BinOp_Lt},
	{"<=", ast::ExprBinOp::BinOp_Le},
	{">", ast::ExprBinOp::BinOp_Gt},
	{">=", ast::ExprBinOp::BinOp_Ge},
	{"**", ast::ExprBinOp::BinOp_Exp},
	{"*", ast::ExprBinOp::BinOp_Mul},
	{"/", ast::ExprBinOp::BinOp_Div},
	{"%", ast::ExprBinOp::BinOp_Mod},
	{"+", ast::ExprBinOp::BinOp_Add},
	{"-", ast::ExprBinOp::BinOp_Sub},
	{"<<", ast::ExprBinOp::BinOp_Shl},
	{">>", ast::ExprBinOp::BinOp_Shr},
	{"==", ast::ExprBinOp::BinOp_Eq},
	{"!=", ast::ExprBinOp::BinOp_Ne}
};

antlrcpp::Any AstBuilderInt::visitExpression(PSSParser::ExpressionContext *ctx) {
	DEBUG_ENTER("visitExpression");

	if (ctx->unary_op()) {
		ctx->lhs->accept(this);
		ast::IExpr *lhs = m_expr;

	} else if (ctx->lhs && ctx->rhs) {
		// It's some form of binary op
		ctx->lhs->accept(this);
		ast::IExpr *lhs = m_expr;

		ctx->rhs->accept(this);
		ast::IExpr *rhs = m_expr;

		ast::ExprBinOp op = ast::ExprBinOp::BinOp_LogOr;
		if (ctx->exp_op()) {
			op = ast::ExprBinOp::BinOp_Exp;
		} else if (ctx->mul_div_mod_op()) {
			op = prv_str2binop.find(ctx->mul_div_mod_op()->toString())->second;
		} else if (ctx->add_sub_op()) {
			op = prv_str2binop.find(ctx->add_sub_op()->toString())->second;
		} else if (ctx->shift_op()) {
			op = prv_str2binop.find(ctx->shift_op()->toString())->second;
		} else if (ctx->logical_inequality_op()) {
			op = prv_str2binop.find(ctx->logical_inequality_op()->toString())->second;
		} else if (ctx->eq_neq_op()) {
			op = prv_str2binop.find(ctx->eq_neq_op()->toString())->second;
		} else if (ctx->binary_and_op()) {
			op = ExprBinOp::BinOp_BitAnd;
		} else if (ctx->binary_xor_op()) {
			op = ExprBinOp::BinOp_BitXor;
		} else if (ctx->binary_or_op()) {
			op = ExprBinOp::BinOp_BitOr;
		} else if (ctx->logical_and_op()) {
			op = ExprBinOp::BinOp_LogAnd;
		} else if (ctx->logical_or_op()) {
			op = ExprBinOp::BinOp_LogOr;
		}

		m_expr = m_factory->mkExprBin(
			lhs,
			op,
			rhs);
	} else if (ctx->lhs) {
		// It's either an 'in' or a conditional 
		if (ctx->in_expression()) {
			DEBUG("TODO: in_expression");
		} else {
			// Conditional
			ctx->lhs->accept(this);
			ast::IExpr *cond = m_expr;

			ctx->conditional_expr()->true_expr->accept(this);
			ast::IExpr *true_e = m_expr;

			ctx->conditional_expr()->false_expr->accept(this);
			ast::IExpr *false_e = m_expr;

			m_expr = m_factory->mkExprCond(
				cond,
				true_e,
				false_e);
		}
	} else {
		// It's a primary
		ctx->primary()->accept(this);
	}

	DEBUG_LEAVE("visitExpression");
	return 0;
}

antlrcpp::Any AstBuilderInt::visitBool_literal(PSSParser::Bool_literalContext *ctx) {
	DEBUG_ENTER("visitBool_literal");
	m_expr = m_factory->mkExprBool(ctx->TOK_TRUE());
	DEBUG_LEAVE("visitBool_literal");
	return 0;
}

antlrcpp::Any AstBuilderInt::visitString_literal(PSSParser::String_literalContext *ctx) {
	DEBUG_ENTER("visitString_literal");
	if (ctx->DOUBLE_QUOTED_STRING()) {
		std::string value = ctx->DOUBLE_QUOTED_STRING()->toString();
		value = value.substr(1, value.size()-1);
		m_expr = m_factory->mkExprString(value, false);
	} else { 
		std::string value = ctx->TRIPLE_DOUBLE_QUOTED_STRING()->toString();
		value = value.substr(3, value.size()-3);
		m_expr = m_factory->mkExprString(value, true);
	}
	DEBUG_LEAVE("visitString_literal");
	return 0;
}

antlrcpp::Any AstBuilderInt::visitNull_ref(PSSParser::Null_refContext *ctx) {
	DEBUG_ENTER("visitNull_ref");
	m_expr = m_factory->mkExprNull();
	DEBUG_LEAVE("visitNull_ref");
	return 0;
}

antlrcpp::Any AstBuilderInt::visitRef_path(PSSParser::Ref_pathContext *ctx) {
	DEBUG_ENTER("visitRef_path");

	DEBUG("TODO: visitRef_path");

	if (ctx->TOK_SUPER()) {

	} else if (ctx->static_ref_path()) {

	} else {
		// Just a regular context path
	}

	DEBUG_LEAVE("visitRef_path");
	return 0;
}

antlrcpp::Any AstBuilderInt::visitCast_expression(PSSParser::Cast_expressionContext *ctx) {
	DEBUG_ENTER("visitCast_expression");
	ctx->expression()->accept(this);
	ast::IExpr *expr = m_expr;

	ctx->casting_type()->accept(this);
	ast::IDataType *type = m_type;

	m_expr = m_factory->mkExprCast(type, expr);

	DEBUG_LEAVE("visitCast_expression");
	return 0;
}

// B.18 Identifiers

antlrcpp::Any AstBuilderInt::visitIdentifier(PSSParser::IdentifierContext *ctx) {
	DEBUG_ENTER("visitIdentifier");
	IExprId *id;
	
	if (ctx->ESCAPED_ID()) {
		id = m_factory->mkExprId(ctx->ESCAPED_ID()->toString(), true);
	} else {
		id = m_factory->mkExprId(ctx->ID()->toString(), false);
	}

	Location loc = id->getLocation();
	loc.lineno = ctx->start->getLine();
	loc.linepos = ctx->start->getCharPositionInLine();
	id->setLocation(loc);


	// TODO: Fill in location info

	m_expr = id;

	DEBUG_LEAVE("visitIdentifier");
	return 0;
}

// B.19 Numbers

antlrcpp::Any AstBuilderInt::visitNumber(PSSParser::NumberContext *ctx) {
	DEBUG_ENTER("visitNumber");
	DEBUG("TODO: Number");
	m_expr = m_factory->mkExprSignedNumber("0", 0, 0);

	DEBUG_LEAVE("visitNumber");

	return 0;
}


void AstBuilderInt::syntaxError(
    		Recognizer *recognizer,
			Token * offendingSymbol,
			size_t line,
			size_t charPositionInLine,
			const std::string &msg,
			std::exception_ptr e) {
	if (m_marker_l) {
		ast::Location loc;
		loc.fileid = 0;
		loc.lineno = line;
		loc.linepos = charPositionInLine;

		Marker m(
				msg,
				MarkerSeverityE::Error,
				loc);
		m_marker_l->marker(&m);
	}
}

void AstBuilderInt::addChild(ast::IScopeChild *c) {
	scope()->getChildren().push_back(ast::IScopeChildUP(c));
//	ScopeUtil::addChild(scope(), c);
}

void AstBuilderInt::addChild(ast::INamedScopeChild *c) {
	scope()->getChildren().push_back(ast::IScopeChildUP(c));
//	ScopeUtil::addChild(scope(), c);
}

void AstBuilderInt::addChild(ast::INamedScope *c) {
	scope()->getChildren().push_back(ast::IScopeChildUP(c));
}

void AstBuilderInt::addDocstring(ast::IScopeChild *c, Token *t) {
	std::vector<Token *> ws_tokens = m_tokens->getHiddenTokensToLeft(
			t->getTokenIndex(), 10);
	std::vector<Token *> slc_tokens = m_tokens->getHiddenTokensToLeft(
			t->getTokenIndex(), 11);
	std::vector<Token *> mlc_tokens = m_tokens->getHiddenTokensToLeft(
			t->getTokenIndex(), 12);

	fprintf(stdout, "ws_tokens=%d slc_tokens=%d mlc_tokens=%d\n",
			ws_tokens.size(), slc_tokens.size(), mlc_tokens.size());

	if (slc_tokens.size() == 0 && mlc_tokens.size() == 0) {
		return;
	}


	int32_t last_ws_line = -1;
	if (ws_tokens.size() > 0) {
		last_ws_line = ws_tokens.back()->getLine();
	}

	std::string docstring;
	if (slc_tokens.size() > 0 && mlc_tokens.size() > 0) {
		if (slc_tokens.back()->getLine() > mlc_tokens.back()->getLine()) {
			// Single-line comment is last
			docstring = processDocStringSingleLineComment(
					slc_tokens,
					ws_tokens);
		} else {
			// Multi-line comment is last
			docstring = processDocStringMultiLineComment(
					mlc_tokens,
					ws_tokens);
		}
	} else if (slc_tokens.size() > 0) {
		// Single-line comment
		docstring = processDocStringSingleLineComment(
				slc_tokens,
				ws_tokens);
	} else {
		// Multi-line comment
		docstring = processDocStringMultiLineComment(
				mlc_tokens,
				ws_tokens);
	}

	if (docstring != "") {
		c->setDocstring(docstring);
	}

	/*
	fprintf(stdout, "Token pos: %d\n", comp->getLine());
	for (std::vector<Token*>::const_iterator
			it=tokens.begin();
			it!=tokens.end(); it++) {
		fprintf(stdout, "Token %d: %s\n",
				(*it)->getLine(),
				(*it)->getText().c_str());
	}
	 */
}

std::string AstBuilderInt::processDocStringMultiLineComment(
    		const std::vector<Token *>		&mlc_tokens,
			const std::vector<Token *>		&ws_tokens) {
	int32_t last_ws_line = -1;
	if (ws_tokens.size() > 0) {
		last_ws_line = ws_tokens.back()->getLine();
	}

	fprintf(stdout, "last_ws_line=%d comment_line=%d\n",
			last_ws_line,
			mlc_tokens.back()->getLine());
	std::string comment;
	if (last_ws_line < 0 || last_ws_line < mlc_tokens.back()->getLine()) {
		fprintf(stdout, "OK: no whitespace between element and comment\n");
	} else if (last_ws_line >= 0) {
		fprintf(stdout, "TODO: check if whitespace exceeds a limit\n");

		// Find the extent of the comment
		uint32_t comment_last_line = mlc_tokens.back()->getLine();
		comment = mlc_tokens.back()->getText();
		std::string ws = ws_tokens.back()->getText();
		int32_t i=0;
		while (i < comment.size() &&
				(i=comment.find('\n', i)) != std::string::npos) {
			comment_last_line++;
			i++;
		}

		i=0;
		while (i < comment.size() &&
				(i=ws.find('\n', i)) != std::string::npos) {
			last_ws_line++;
			i++;
		}

		fprintf(stdout, "Comment last line: %d\n", comment_last_line);
		fprintf(stdout, "Whitespace last line: %d\n", last_ws_line);

		if (last_ws_line <= (comment_last_line+2)) {
			fprintf(stdout, "Note: Have a doc comment\n");

			// TODO: now we need to clean up the comment
			//

			// Trim off the beginning and end of the comment
			comment = comment.substr(2,comment.size()-4);

			fprintf(stdout, "Comment: %s\n", comment.c_str());
			// Step through the lines looking for a '*' prefix
			i=0;
			while (i<comment.size()) {
				if (comment.at(i) == '*') {
					comment.erase(i, 1);
					fprintf(stdout, "Post-remove(1): %s\n", comment.c_str());
				} else if ((i+1<comment.size()) &&
						(isspace(comment.at(i)) && comment.at(i+1) == '*')) {
					comment.erase(i, 2);
					fprintf(stdout, "Post-remove(2): %s\n", comment.c_str());
				}
				if ((i=comment.find('\n',i)) != std::string::npos) {
					i++;
				} else {
					break;
				}
			}
		} else {
			fprintf(stdout, "Note: False alarm\n");
			comment.clear();
		}
	}

	return comment;
}

std::string AstBuilderInt::processDocStringSingleLineComment(
    		const std::vector<Token *>		&slc_tokens,
			const std::vector<Token *>		&ws_tokens) {
	return "";
}

ast::IExprDomainOpenRangeList *AstBuilderInt::mkDomainOpenRangeList(PSSParser::Domain_open_range_listContext *ctx) {
	DEBUG_ENTER("mkDomainOpenRangeList");
	ast::IExprDomainOpenRangeList *ret = m_factory->mkExprDomainOpenRangeList();
	std::vector<PSSParser::Domain_open_range_valueContext *> items =
		ctx->domain_open_range_value();
	
	for (std::vector<PSSParser::Domain_open_range_valueContext *>::const_iterator
		it=items.begin();
		it!=items.end(); it++) {

		ast::IExpr *lhs = 0;
		if ((*it)->lhs) {
			(*it)->lhs->accept(this);
			lhs = m_expr;
		}

		ast::IExpr *rhs = 0;
		if ((*it)->rhs) {
			(*it)->rhs->accept(this);
			rhs = m_expr;
		}

		ast::IExprDomainOpenRangeValue *value = m_factory->mkExprDomainOpenRangeValue(
			!((*it)->limit_high || (*it)->limit_mid || (*it)->limit_low),
			lhs,
			rhs
		);
		ret->getValues().push_back(ast::IExprDomainOpenRangeValueUP(value));
	}
	DEBUG_LEAVE("mkDomainOpenRangeList");
	return ret;
}

IExprId *AstBuilderInt::mkId(PSSParser::IdentifierContext *ctx) {
	IExprId *id;
	
	if (ctx->ESCAPED_ID()) {
		id = m_factory->mkExprId(ctx->ESCAPED_ID()->toString(), true);
	} else {
		id = m_factory->mkExprId(ctx->ID()->toString(), false);
	}

	Location loc = id->getLocation();
	loc.lineno = ctx->start->getLine();
	loc.linepos = ctx->start->getCharPositionInLine();
	id->setLocation(loc);


	// TODO: Fill in location info

	return id;
}

ast::IExprHierarchicalId *AstBuilderInt::mkHierarchicalId(PSSParser::Hierarchical_idContext *ctx) {

	return 0;
}

void AstBuilderInt::mkTypeId(
		std::vector<IExprIdUP>					&type_id,
		PSSParser::Type_identifierContext		*ctx) {
	for (std::vector<PSSParser::Type_identifier_elemContext *>::const_iterator
		it=ctx->type_identifier_elem().begin();
		it!=ctx->type_identifier_elem().end(); it++) {
//		type_id.push_back(IExprIdUP(mkId((*it)->identifier())));
	}
}

ast::ITypeIdentifier *AstBuilderInt::mkTypeId(
		PSSParser::Type_identifierContext		*ctx) {
	ast::ITypeIdentifier *ret = m_factory->mkTypeIdentifier();
	std::vector<PSSParser::Type_identifier_elemContext *> elems = ctx->type_identifier_elem();

	for (std::vector<PSSParser::Type_identifier_elemContext *>::const_iterator
		it=elems.begin();
		it!=elems.end(); it++) {
		ast::ITypeIdentifierElem *elem = m_factory->mkTypeIdentifierElem(
			mkId((*it)->identifier()));
		
		// TODO: handle parameterized types
		
		ret->getElems().push_back(ast::ITypeIdentifierElemUP(elem));
	}

	return ret;
}

ast::IExpr *AstBuilderInt::mkExpr(
		PSSParser::ExpressionContext 			*ctx) {
	return 0;
}

}
