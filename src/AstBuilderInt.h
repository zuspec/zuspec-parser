/*
 * AstBuilderInt.h
 *
 *  Created on: Sep 13, 2020
 *      Author: ballance
 */

#pragma once
#include <memory>
#include <istream>
#include "zsp/IMarkerListener.h"
#include "PSSParserBaseVisitor.h"
#include "BaseErrorListener.h"
#include "zsp/ast/IExprId.h"
#include "zsp/ast/IFactory.h"
#include "zsp/ast/IGlobalScope.h"
#include "zsp/ast/IScope.h"

using namespace antlr4;
using namespace antlrcpp;

namespace zsp {

class AstBuilderInt :
		public PSSParserBaseVisitor,
		public BaseErrorListener {
public:
	AstBuilderInt(
		ast::IFactory			*factory,
		IMarkerListener 		*marker_l);

	virtual ~AstBuilderInt();

	void build(
			ast::IGlobalScope	*global,
			std::istream 		*in);

	virtual antlrcpp::Any visitPackage_declaration(PSSParser::Package_declarationContext *ctx) override;

	virtual antlrcpp::Any visitImport_stmt(PSSParser::Import_stmtContext *ctx) override;

//	virtual antlrcpp::Any visitAction_declaration(PSSParser::Action_declarationContext *ctx) override;


	// B.3 Struct declarations
	virtual antlrcpp::Any visitStruct_declaration(PSSParser::Struct_declarationContext *ctx) override;

	// B.14 Constraints
	virtual antlrcpp::Any visitConstraint_declaration(PSSParser::Constraint_declarationContext *ctx) override;

	virtual antlrcpp::Any visitConstraint_set(PSSParser::Constraint_setContext *ctx) override;

	virtual antlrcpp::Any visitConstraint_block(PSSParser::Constraint_blockContext *ctx) override;

	virtual antlrcpp::Any visitDefault_constraint_item(PSSParser::Default_constraint_itemContext *ctx) override;

	virtual antlrcpp::Any visitDefault_disable_constraint(PSSParser::Default_disable_constraintContext *ctx) override;

	virtual antlrcpp::Any visitExpression_constraint_item(PSSParser::Expression_constraint_itemContext *ctx) override;

	virtual antlrcpp::Any visitForeach_constraint_item(PSSParser::Foreach_constraint_itemContext *ctx) override;

	virtual antlrcpp::Any visitForall_constraint_item(PSSParser::Forall_constraint_itemContext *ctx) override;

	virtual antlrcpp::Any visitIf_constraint_item(PSSParser::If_constraint_itemContext *ctx) override;

	virtual antlrcpp::Any visitImplication_constraint_item(PSSParser::Implication_constraint_itemContext *ctx) override;
	
	virtual antlrcpp::Any visitUnique_constraint_item(PSSParser::Unique_constraint_itemContext *ctx) override;

    virtual void syntaxError(
    		Recognizer *recognizer,
			Token * offendingSymbol,
			size_t line,
			size_t charPositionInLine,
			const std::string &msg,
			std::exception_ptr e) override;


private:
    void addChild(ast::IScopeChild *c);

    void addChild(ast::INamedScopeChild *c);

    void addChild(ast::INamedScope *c);

    void addDocstring(ast::IScopeChild *c, Token *t);

    std::string processDocStringMultiLineComment(
    		const std::vector<Token *>		&mlc_tokens,
			const std::vector<Token *>		&ws_tokens);

    std::string processDocStringSingleLineComment(
    		const std::vector<Token *>		&slc_tokens,
			const std::vector<Token *>		&ws_tokens);

    ast::IScope *scope() const { return m_scopes.back(); }

    void push_scope(ast::IScope *s) { m_scopes.push_back(s); }

    void pop_scope() { m_scopes.pop_back(); }

	ast::IExprId *mkId(PSSParser::IdentifierContext *ctx);

	void mkTypeId(
		std::vector<ast::IExprIdUP>				&type_id,
		PSSParser::Type_identifierContext		*ctx);

	ast::ITypeIdentifier *mkTypeId(
		PSSParser::Type_identifierContext		*ctx);



private:
    IMarkerListener								*m_marker_l;
	ast::IFactory								*m_factory;
    std::vector<ast::IScope *>					m_scopes;
	std::vector<ast::IConstraintScope *>		m_constraint_s;
    std::unique_ptr<CommonTokenStream>			m_tokens;
	std::vector<ast::IExprIdUP>					*m_type_id;

};

}

