/*
 * AstBuilderInt.cpp
 *
 *  Created on: Sep 13, 2020
 *      Author: ballance
 */

#include <vector>
#include "dmgr/impl/DebugMacros.h"
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

namespace zsp {
namespace parser {


using namespace ast;

AstBuilderInt::AstBuilderInt(
    dmgr::IDebugMgr     *dmgr,
	ast::IFactory		*factory,
	IMarkerListener 	*marker_l) : m_factory(factory), m_marker_l(marker_l) {
    DEBUG_INIT("AstBuilderInt", dmgr);
	m_collectDocStrings = false;
	m_field_depth = 0;
	m_labeled_activity_id = 0;
	m_constraint = 0;

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
	std::vector<PSSParser::Package_identifierContext *> id =
		ctx->package_id_path()->package_identifier();
	for (std::vector<PSSParser::Package_identifierContext *>::const_iterator
		it=id.begin();
		it!=id.end(); it++) {
		PSSParser::Package_identifierContext *id = (*it);
		pkg->getId().push_back(IExprIdUP(mkId((*it)->identifier())));
	}

	addChild(pkg, ctx->start);
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
	DEBUG_ENTER("visitImport_stmt");
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

	imp->setPath(mkTypeId(ctx->package_import_pattern()->type_identifier()));
	addChild(imp, ctx->start);
	DEBUG_LEAVE("visitImport_stmt");
	return 0;
}

static std::map<std::string,ast::ExtendTargetE> ExtendKind_m = {
	{"action", ast::ExtendTargetE::Action},
	{"buffer", ast::ExtendTargetE::Buffer},
	{"component", ast::ExtendTargetE::Component},
	{"enum", ast::ExtendTargetE::Enum},
	{"resource", ast::ExtendTargetE::Resource},
	{"state", ast::ExtendTargetE::State},
	{"stream", ast::ExtendTargetE::Stream},
	{"struct", ast::ExtendTargetE::Struct}
};

antlrcpp::Any AstBuilderInt::visitExtend_stmt(PSSParser::Extend_stmtContext *ctx) {
	DEBUG_ENTER("visitExtend_stmt");
	ExtendTargetE kind;
    
    if (ctx->is_action) {
        kind = ast::ExtendTargetE::Action;
    } else if (ctx->is_component) {
        kind = ast::ExtendTargetE::Component;
    } else if (ctx->is_enum) {
        kind = ast::ExtendTargetE::Enum;
    } else {
        std::map<std::string,ast::ExtendTargetE>::const_iterator it =
            ExtendKind_m.find(ctx->struct_kind()->toString());
        if (it != ExtendKind_m.end()) {
            kind = it->second;
        } else {
            fprintf(stdout, "Error: No match for extend kind\n");
        }
    }

	if (kind == ast::ExtendTargetE::Enum) {
		IExtendEnum *ext = m_factory->mkExtendEnum(mkTypeId(ctx->type_identifier()));
		std::vector<PSSParser::Enum_itemContext *> items = ctx->enum_item();

		for (std::vector<PSSParser::Enum_itemContext *>::const_iterator
			it=items.begin();
			it!=items.end(); it++) {
			ast::IExprId *id = mkId((*it)->identifier());
			ast::IExpr *value = 0;

			if ((*it)->constant_expression()) {
				value = mkExpr((*it)->constant_expression()->expression());
			}
			ast::IEnumItem *item = m_factory->mkEnumItem(id, value);
			ext->getItems().push_back(ast::IEnumItemUP(item));
		}
		
		addChild(ext, ctx->start);
	} else {
		IExtendType *ext = m_factory->mkExtendType(
			kind,
			mkTypeId(ctx->type_identifier()));

		addChild(ext, ctx->start);
		push_scope(ext);
		switch (kind) {
			case ast::ExtendTargetE::Action: {
				std::vector<PSSParser::Action_body_itemContext *> items =
					ctx->action_body_item();
                DEBUG("Extend Action: %d items", items.size());
				for (std::vector<PSSParser::Action_body_itemContext *>::const_iterator
					it=items.begin();
					it!=items.end(); it++) {
					(*it)->accept(this);
				}
			} break;
			case ast::ExtendTargetE::Component: {
				std::vector<PSSParser::Component_body_itemContext *> items =
					ctx->component_body_item();
                DEBUG("Extend Component: %d items", items.size());
				for (std::vector<PSSParser::Component_body_itemContext *>::const_iterator
					it=items.begin();
					it!=items.end(); it++) {
					(*it)->accept(this);
				}
			} break;
			case ast::ExtendTargetE::Buffer:
			case ast::ExtendTargetE::Resource:
			case ast::ExtendTargetE::State:
			case ast::ExtendTargetE::Stream:
			case ast::ExtendTargetE::Struct: {
				std::vector<PSSParser::Struct_body_itemContext *> items =
					ctx->struct_body_item();
                DEBUG("Extend Struct: %d items", items.size());
				for (std::vector<PSSParser::Struct_body_itemContext *>::const_iterator
					it=items.begin();
					it!=items.end(); it++) {
					(*it)->accept(this);
				}
				
			} break;
            default:
                fprintf(stdout, "Error: unhandled extension-type target: %d\n", kind);
                break;
		}

		pop_scope();
	}

	DEBUG_LEAVE("visitExtend_stmt");
	return 0;
}

antlrcpp::Any AstBuilderInt::visitConst_field_declaration(PSSParser::Const_field_declarationContext *ctx) {
	DEBUG_ENTER("visitConst_field_declaration");

	m_field_depth++;
	ctx->data_declaration()->accept(this);
	m_field_depth--;

	if (!m_field_depth) {
		m_fields.clear();
	}

	for (std::vector<ast::IField *>::const_iterator
		it=m_fields.begin();
		it!=m_fields.end(); it++) {
		(*it)->setAttr((*it)->getAttr() | FieldAttr::Const);
	}

	DEBUG_LEAVE("visitConst_field_declaration");
	return 0;
}

// B.2 Action declaration

antlrcpp::Any AstBuilderInt::visitAction_declaration(PSSParser::Action_declarationContext *ctx) {
	DEBUG_ENTER("visitAction_declaration");

	ast::ITypeIdentifier *super_t = 0;
	if (ctx->action_super_spec()) {
		super_t = mkTypeId(ctx->action_super_spec()->type_identifier());
	}

	ast::IAction *action = m_factory->mkAction(
		mkId(ctx->action_identifier()->identifier()),
		super_t,
		false);

	if (ctx->template_param_decl_list()) {
		// TODO: add in declarations
	}

	addChild(action, ctx->start);
	push_scope(action);

	std::vector<PSSParser::Action_body_itemContext *> items = ctx->action_body_item();

	for (std::vector<PSSParser::Action_body_itemContext *>::const_iterator
		it=items.begin();
		it!=items.end(); it++) {
		(*it)->accept(this);
	}

	pop_scope();

	DEBUG_LEAVE("visitAction_declaration");
	return 0;
}

antlrcpp::Any AstBuilderInt::visitAbstract_action_declaration(PSSParser::Abstract_action_declarationContext *ctx) {
	DEBUG_ENTER("visitAbstract_action_declaration");
	ctx->action_declaration()->accept(this);
	ast::IAction *action = dynamic_cast<ast::IAction *>(scope()->getChildren().back().get());
	action->setIs_abstract(true);
	DEBUG_LEAVE("visitAbstract_action_declaration");
	return 0;
}

antlrcpp::Any AstBuilderInt::visitActivity_declaration(PSSParser::Activity_declarationContext *ctx) {
    DEBUG_ENTER("visitActivity_declaration");
    ast::IActivityDecl *activity = m_factory->mkActivityDecl();

	std::vector<PSSParser::Activity_stmtContext *> items = ctx->activity_stmt();
	for (std::vector<PSSParser::Activity_stmtContext *>::const_iterator
		it=items.begin();
		it!=items.end(); it++) {
        addActivityStmt(activity, *it);
	}
    
	m_activity_stmt = activity;

    addChild(activity, ctx->start);
    
    DEBUG_LEAVE("visitActivity_declaration");
    return 0;
}

antlrcpp::Any AstBuilderInt::visitFlow_ref_field_declaration(PSSParser::Flow_ref_field_declarationContext *ctx) {
	DEBUG_ENTER("visitFlow_ref_field_declaration");

	std::vector<PSSParser::Object_ref_fieldContext *> items = ctx->object_ref_field();
	for (std::vector<PSSParser::Object_ref_fieldContext *>::const_iterator
		it=items.begin();
		it!=items.end(); it++) {
		ast::IExpr *array_dim = 0;
		ast::IDataTypeUserDefined *type = 0;

		if (ctx->flow_object_type()->buffer_type_identifier()) {
			type = mkDataTypeUserDefined(ctx->flow_object_type()->buffer_type_identifier()->type_identifier());
		} else if (ctx->flow_object_type()->state_type_identifier()) {
			type = mkDataTypeUserDefined(ctx->flow_object_type()->state_type_identifier()->type_identifier());
		} else if (ctx->flow_object_type()->stream_type_identifier()) {
			type = mkDataTypeUserDefined(ctx->flow_object_type()->stream_type_identifier()->type_identifier());
		} else {
			DEBUG("Unknown flow-object type");
		}

		if ((*it)->array_dim()) {
			array_dim = mkExpr((*it)->array_dim()->constant_expression()->expression());
		}

		ast::IFieldRef *field = m_factory->mkFieldRef(
			mkId((*it)->identifier()),
			type,
			array_dim,
			ctx->is_input);
		addChild(field, ctx->start);
	}

	DEBUG_LEAVE("visitFlow_ref_field_declaration");
	return 0;
}

antlrcpp::Any AstBuilderInt::visitResource_ref_field_declaration(PSSParser::Resource_ref_field_declarationContext *ctx) {
	DEBUG_ENTER("visitResource_ref_field_declaration");

	std::vector<PSSParser::Object_ref_fieldContext *> items = ctx->object_ref_field();
	for (std::vector<PSSParser::Object_ref_fieldContext *>::const_iterator
		it=items.begin();
		it!=items.end(); it++) {
		ast::IExpr *array_dim = 0;
		ast::IDataTypeUserDefined *type = mkDataTypeUserDefined(
			ctx->resource_object_type()->resource_type_identifier()->type_identifier());

		if ((*it)->array_dim()) {
			array_dim = mkExpr((*it)->array_dim()->constant_expression()->expression());
		}

		ast::IFieldClaim *field = m_factory->mkFieldClaim(
			mkId((*it)->identifier()),
			type,
			array_dim,
			ctx->lock);
		addChild(field, ctx->start);
	}

	DEBUG_LEAVE("visitResource_ref_field_declaration");
	return 0;
}

antlrcpp::Any AstBuilderInt::visitActivity_data_field(PSSParser::Activity_data_fieldContext *ctx) {
	DEBUG_ENTER("visitActivity_data_field");
	m_field_depth++;
	m_field_depth--;

	for (std::vector<ast::IField *>::const_iterator
		it=m_fields.begin();
		it!=m_fields.end(); it++) {
		(*it)->setAttr((*it)->getAttr() | FieldAttr::Action);
	}

	if (!m_field_depth) {
		m_fields.clear();
	}
	DEBUG_LEAVE("visitActivity_data_field");
	return 0;
}

static std::map<std::string,ast::StructKind> StructKind_m = {
	{"struct", ast::StructKind::Struct},
	{"buffer", ast::StructKind::Buffer},
	{"resource", ast::StructKind::Resource},
	{"state", ast::StructKind::State},
	{"stream", ast::StructKind::Stream}
};

// B.3 Struct
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

	addChild(s, ctx->start);
	push_scope(s);
	std::vector<PSSParser::Struct_body_itemContext *> body = ctx->struct_body_item();
	for (std::vector<PSSParser::Struct_body_itemContext *>::const_iterator
		it=body.begin();
		it!=body.end(); it++) {
		(*it)->accept(this);
	}
	pop_scope();

	DEBUG_LEAVE("visitStruct_declaration");
	return 0;
}

// B.4 Exec blocks
antlrcpp::Any AstBuilderInt::visitExec_block(PSSParser::Exec_blockContext *ctx) {
    DEBUG_ENTER("visitExec_block");

    DEBUG_LEAVE("visitExec_block");
    return 0;
}

antlrcpp::Any AstBuilderInt::visitTarget_code_exec_block(PSSParser::Target_code_exec_blockContext *ctx) {
    DEBUG_ENTER("visitTarget_code_exec_block");
    DEBUG("TODO: visitTarget_code_exec_block");
    DEBUG_LEAVE("visitTarget_code_exec_block");
    return 0;
}

antlrcpp::Any AstBuilderInt::visitTarget_file_exec_block(PSSParser::Target_file_exec_blockContext *ctx) {
    DEBUG_ENTER("visitTarget_file_exec_block");
    DEBUG("TODO: visitTarget_file_exec_block");
    DEBUG_LEAVE("visitTarget_file_exec_block");
    return 0;
}

antlrcpp::Any AstBuilderInt::visitExec_super_stmt(PSSParser::Exec_super_stmtContext *ctx) {
    DEBUG_ENTER("visitExec_super_stmt");
    DEBUG("TODO: visitExec_super_stmt");
    DEBUG_LEAVE("visitExec_super_stmt");
    return 0;
}

// B.5 Functions
antlrcpp::Any AstBuilderInt::visitProcedural_function(PSSParser::Procedural_functionContext *ctx) {
    DEBUG_ENTER("visitProcedural_function");

    ast::IProceduralStmtSequenceBlock *body = m_factory->mkProceduralStmtSequenceBlock();
    std::vector<PSSParser::Procedural_stmtContext *> items = ctx->procedural_stmt();
    m_exec_scope_s.push_back(body);
    for (std::vector<PSSParser::Procedural_stmtContext *>::const_iterator
        it=items.begin();
        it!=items.end(); it++) {
        addExecStmt(*it);
    }
    m_exec_scope_s.pop_back();

    ast::IFunctionDefinition *func = m_factory->mkFunctionDefinition(
        mkFunctionPrototype(ctx->function_prototype()),
        body
    );

    m_scopes.back()->getChildren().push_back(ast::IScopeChildUP(func));
    DEBUG_LEAVE("visitProcedural_function");
    return 0;
}

antlrcpp::Any AstBuilderInt::visitFunction_decl(PSSParser::Function_declContext *ctx) {
    DEBUG_ENTER("visitFunction_decl");
    ast::IFunctionPrototype *proto = mkFunctionPrototype(ctx->function_prototype());
    DEBUG("TODO: visitFunction_decl");
    DEBUG_LEAVE("visitFunction_decl");
    return 0;
}

antlrcpp::Any AstBuilderInt::visitFunction_prototype(PSSParser::Function_prototypeContext *ctx) {
    DEBUG_ENTER("visitFunction_prototype");
    DEBUG("TODO: visitFunction_prototype");
    DEBUG_LEAVE("visitFunction_prototype");
    return 0;
}

// B.7 Procedural Statements
antlrcpp::Any AstBuilderInt::visitProcedural_sequence_block_stmt(PSSParser::Procedural_sequence_block_stmtContext *ctx) { 
    DEBUG_ENTER("visitProcedural_sequence_block_stmt");
    ast::IProceduralStmtSequenceBlock *block = m_factory->mkProceduralStmtSequenceBlock();
    m_exec_scope_s.push_back(block);

    std::vector<PSSParser::Procedural_stmtContext *> items = ctx->procedural_stmt();
    for (std::vector<PSSParser::Procedural_stmtContext *>::const_iterator
        it=items.begin();
        it!=items.end(); it++) {
        addExecStmt(*it);
    }

    m_exec_stmt = block;
    DEBUG_LEAVE("visitProcedural_sequence_block_stmt");
    return 0;
}

static std::map<std::string, ast::AssignOp> assign_op_m = {
    { "=", ast::AssignOp::AssignOp_Eq },
    { "+=", ast::AssignOp::AssignOp_PlusEq },
    { "-=", ast::AssignOp::AssignOp_MinusEq },
    { "<<=", ast::AssignOp::AssignOp_ShlEq },
    { ">>=", ast::AssignOp::AssignOp_ShrEq },
    { "|=", ast::AssignOp::AssignOp_OrEq },
    { "&=", ast::AssignOp::AssignOp_AndEq }
};

antlrcpp::Any AstBuilderInt::visitProcedural_assignment_stmt(PSSParser::Procedural_assignment_stmtContext *ctx) { 
    DEBUG_ENTER("visitProcedural_assignment_stmt");
    ast::IExprRefPath *lhs = 0; // TODO:
    ast::AssignOp op = assign_op_m.find(ctx->assign_op()->toString())->second;
    ast::IExpr *rhs = mkExpr(ctx->expression());

    ast::IProceduralStmtAssignment *stmt = m_factory->mkProceduralStmtAssignment(
        lhs,
        op,
        rhs);

    m_exec_stmt = stmt;

    DEBUG_LEAVE("visitProcedural_assignment_stmt");
    return 0;
}

antlrcpp::Any AstBuilderInt::visitProcedural_void_function_call_stmt(PSSParser::Procedural_void_function_call_stmtContext *ctx) { 
    DEBUG_ENTER("visitProcedural_void_function_call_stmt");
    IExprRefPathStatic *prefix = 0;

    if (ctx->function_call()->is_global || 
        ctx->function_call()->type_identifier_elem().size() > 0) {
        // Have a static component
        prefix = m_factory->mkExprRefPathStatic(ctx->function_call()->is_global);

        std::vector<PSSParser::Type_identifier_elemContext *> items =
            ctx->function_call()->type_identifier_elem();
        for (std::vector<PSSParser::Type_identifier_elemContext *>::const_iterator
            it=items.begin();
            it!=items.end(); it++) {
            prefix->getBase().push_back(ast::ITypeIdentifierElemUP(mkTypeIdElem(*it)));
        }
    }

    IExprHierarchicalId *hid = m_factory->mkExprHierarchicalId();
    std::vector<PSSParser::Member_path_elemContext *> path =
        ctx->function_call()->function_ref_path()->member_path_elem();
    for (std::vector<PSSParser::Member_path_elemContext *>::const_iterator
        it=path.begin();
        it!=path.end(); it++) {
        hid->getElems().push_back(ast::IExprMemberPathElemUP(mkMemberPathElem(*it)));
    }

    // Now, round up the parameter list
    std::vector<PSSParser::ExpressionContext *> items =
        ctx->function_call()->function_ref_path()->function_parameter_list()->expression();
    ast::IMethodParameterList *params = m_factory->mkMethodParameterList();
    for (std::vector<PSSParser::ExpressionContext *>::const_iterator
        it=items.begin();
        it!=items.end(); it++) {
        params->getParameters().push_back(ast::IExprUP(mkExpr(*it)));
    }

    hid->getElems().push_back(ast::IExprMemberPathElemUP(
        m_factory->mkExprMemberPathElem(
            mkId(ctx->function_call()->function_ref_path()->identifier()),
            params,
            0
        )
    ));

    ast::IProceduralStmtExpr *stmt = m_factory->mkProceduralStmtExpr(
        m_factory->mkExprRefPathStaticRooted(
            prefix,
            m_factory->mkExprRefPathContext(hid))
    );

    m_exec_stmt = stmt;

    DEBUG_LEAVE("visitProcedural_void_function_call_stmt");
    return 0;
}

antlrcpp::Any AstBuilderInt::visitProcedural_return_stmt(PSSParser::Procedural_return_stmtContext *ctx) { 
    DEBUG_ENTER("visitProcedural_return_stmt");
    ast::IExpr *expr = ctx->expression()?mkExpr(ctx->expression()):0;
    ast::IProceduralStmtReturn *stmt = m_factory->mkProceduralStmtReturn(expr);

    m_exec_stmt = stmt;

    DEBUG_LEAVE("visitProcedural_return_stmt");
    return 0;
}

antlrcpp::Any AstBuilderInt::visitProcedural_repeat_stmt(PSSParser::Procedural_repeat_stmtContext *ctx) { 
    DEBUG_ENTER("visitProcedural_repeat_stmt");
    if (ctx->is_repeat) {
    } else if (ctx->is_repeat_while) {
    } else { // 'while'
    }

    DEBUG_LEAVE("visitProcedural_repeat_stmt");
    return 0;
}

antlrcpp::Any AstBuilderInt::visitProcedural_foreach_stmt(PSSParser::Procedural_foreach_stmtContext *ctx) { 
    DEBUG_ENTER("visitProcedural_foreach_stmt");

    DEBUG_LEAVE("visitProcedural_foreach_stmt");
    return 0;
}

antlrcpp::Any AstBuilderInt::visitProcedural_if_else_stmt(PSSParser::Procedural_if_else_stmtContext *ctx) { 
    DEBUG_ENTER("visitProcedural_if_else_stmt");

    ast::IExpr *cond = mkExpr(ctx->expression());
    ast::IExecStmt *true_s = mkExecStmt(ctx->procedural_stmt(0));
    ast::IExecStmt *false_s = ctx->procedural_stmt(1)?mkExecStmt(ctx->procedural_stmt(1)):0;
    ast::IProceduralStmtIfElse *stmt = m_factory->mkProceduralStmtIfElse(
        cond,
        true_s,
        false_s);

    m_exec_stmt = stmt;
    DEBUG_LEAVE("visitProcedural_if_else_stmt");
    return 0;
}

antlrcpp::Any AstBuilderInt::visitProcedural_match_stmt(PSSParser::Procedural_match_stmtContext *ctx) { 
    DEBUG_ENTER("visitProcedural_match_stmt");
    DEBUG("TODO: visitProcedural_match_stmt");
    DEBUG_LEAVE("visitProcedural_match_stmt");
    return 0;
}

antlrcpp::Any AstBuilderInt::visitProcedural_break_stmt(PSSParser::Procedural_break_stmtContext *ctx) { 
    DEBUG_ENTER("visitProcedural_break_stmt");
    ast::IProceduralStmtBreak *stmt = m_factory->mkProceduralStmtBreak();

    m_exec_stmt = stmt;
    DEBUG_LEAVE("visitProcedural_break_stmt");
    return 0;
}

antlrcpp::Any AstBuilderInt::visitProcedural_continue_stmt(PSSParser::Procedural_continue_stmtContext *ctx) { 
    DEBUG_ENTER("visitProcedural_continue_stmt");
    ast::IProceduralStmtContinue *stmt = m_factory->mkProceduralStmtContinue();

    m_exec_stmt = stmt;

    DEBUG_LEAVE("visitProcedural_continue_stmt");
    return 0;
}

antlrcpp::Any AstBuilderInt::visitProcedural_data_declaration(PSSParser::Procedural_data_declarationContext *ctx) { 
    DEBUG_ENTER("visitProcedural_data_declaration");

    std::vector<PSSParser::Procedural_data_instantiationContext *> items = ctx->procedural_data_instantiation();
    for (std::vector<PSSParser::Procedural_data_instantiationContext *>::const_iterator
        it=items.begin();
        it!=items.end(); it++) {
        ast::IDataType *type = mkDataType(ctx->data_type());
        ast::IExprId *name = mkId((*it)->identifier());
        ast::IExpr *array_dim = ((*it)->array_dim())?mkExpr(
            (*it)->array_dim()->constant_expression()->expression()):0;
        ast::IExpr *init = ((*it)->expression())?mkExpr((*it)->expression()):0;
        ast::IProceduralStmtDataDeclaration *decl = m_factory->mkProceduralStmtDataDeclaration(
            name,
            type,
            array_dim,
            init);
        m_exec_scope_s.back()->getChildren().push_back(ast::IExecStmtUP(decl));
    }

    // We've already added to the super scope
    m_exec_stmt = 0;

    DEBUG_LEAVE("visitProcedural_data_declaration");
    return 0;
}

// B.8 Component declarations

antlrcpp::Any AstBuilderInt::visitComponent_declaration(PSSParser::Component_declarationContext *ctx) {
	DEBUG_ENTER("visitComponent_declaration");
	ast::ITypeIdentifier *super_t = 0;

	if (ctx->component_super_spec()) {
		super_t = mkTypeId(ctx->component_super_spec()->type_identifier());
	}

	ast::IComponent *comp = m_factory->mkComponent(
		mkId(ctx->component_identifier()->identifier()),
		super_t);

	addChild(comp, ctx->start);
	push_scope(comp);
	std::vector<PSSParser::Component_body_itemContext *> body = ctx->component_body_item();
	for (std::vector<PSSParser::Component_body_itemContext *>::const_iterator
		it=body.begin();
		it!=body.end(); it++) {
		(*it)->accept(this);
	}
	pop_scope();

	DEBUG_LEAVE("visitComponent_declaration");
	return 0;
}

// B.9 Activity statements

antlrcpp::Any AstBuilderInt::visitActivity_labeled_stmt(PSSParser::Activity_labeled_stmtContext *ctx) {
	DEBUG_ENTER("visitActivity_labeled_stmt");
	if (ctx->identifier()) {
		m_labeled_activity_id = mkId(ctx->identifier());
	} else {
		m_labeled_activity_id = 0;
	}
	ctx->labeled_activity_stmt()->accept(this);

	m_labeled_activity_id = 0;

	DEBUG_LEAVE("visitActivity_labeled_stmt");
	return 0;
}

antlrcpp::Any AstBuilderInt::visitActivity_action_traversal_stmt(PSSParser::Activity_action_traversal_stmtContext *ctx) {
	DEBUG_ENTER("visitActivity_action_traversal_stmt");
	ast::IActivityLabeledStmt *stmt = 0;
	ast::IConstraintStmt *with_c = 0;

	if (ctx->inline_constraints_or_empty()->constraint_set()) {
		with_c = mkConstraintSet(ctx->inline_constraints_or_empty()->constraint_set());
	}

	if (ctx->is_do) {
		// By-type traversal
		stmt = m_factory->mkActivityActionTypeTraversal(
			mkDataTypeUserDefined(ctx->type_identifier()),
			with_c);
	} else {
		// Handle traversal
		ast::IExprHierarchicalId *path = m_factory->mkExprHierarchicalId();
		ast::IExprMemberPathElem *elem = m_factory->mkExprMemberPathElem(
			mkId(ctx->identifier()),
			0,
			(ctx->expression())?mkExpr(ctx->expression()):0);
		path->getElems().push_back(ast::IExprMemberPathElemUP(elem));
		ast::IExprRefPathContext *target = m_factory->mkExprRefPathContext(path);

		stmt = m_factory->mkActivityActionHandleTraversal(
			target,
			with_c);
	}

	if (m_labeled_activity_id) {
		stmt->setLabel(m_labeled_activity_id);
		m_labeled_activity_id = 0;
	}

	m_activity_stmt = stmt;

	DEBUG_LEAVE("visitActivity_action_traversal_stmt");
	return 0;
}

antlrcpp::Any AstBuilderInt::visitActivity_sequence_block_stmt(PSSParser::Activity_sequence_block_stmtContext *ctx) {
	DEBUG_ENTER("visitActivity_sequence_block_stmt");
	ast::IActivitySequence *seq = m_factory->mkActivitySequence();

	if (m_labeled_activity_id) {
		seq->setLabel(m_labeled_activity_id);
		m_labeled_activity_id = 0;
	}

	std::vector<PSSParser::Activity_stmtContext *> items = ctx->activity_stmt();
	for (std::vector<PSSParser::Activity_stmtContext *>::const_iterator
		it=items.begin();
		it!=items.end(); it++) {
        addActivityStmt(seq, *it);
	}

	m_activity_stmt = seq;

	DEBUG_LEAVE("visitActivity_sequence_block_stmt");
	return 0;
}

antlrcpp::Any AstBuilderInt::visitActivity_parallel_stmt(PSSParser::Activity_parallel_stmtContext *ctx) {
	DEBUG_ENTER("visitActivity_parallel_stmt");

	ast::IActivityJoinSpec *spec = 0;
	if (ctx->activity_join_spec()) {
		spec = mkActivityJoinSpec(ctx->activity_join_spec());
	}

	ast::IActivityParallel *par = m_factory->mkActivityParallel(spec);

	if (m_labeled_activity_id) {
		par->setLabel(m_labeled_activity_id);
		m_labeled_activity_id = 0;
	}


	std::vector<PSSParser::Activity_stmtContext *> items = ctx->activity_stmt();
	for (std::vector<PSSParser::Activity_stmtContext *>::const_iterator
		it=items.begin();
		it!=items.end(); it++) {
        addActivityStmt(par, *it);
	}

	m_activity_stmt = par;

	DEBUG_LEAVE("visitActivity_parallel_stmt");
	return 0;
}

antlrcpp::Any AstBuilderInt::visitActivity_schedule_stmt(PSSParser::Activity_schedule_stmtContext *ctx) {
	DEBUG_ENTER("visitActivity_schedule_stmt");

	ast::IActivityJoinSpec *spec = 0;
	if (ctx->activity_join_spec()) {
		spec = mkActivityJoinSpec(ctx->activity_join_spec());
	}

	ast::IActivitySchedule *sched = m_factory->mkActivitySchedule(spec);

	if (m_labeled_activity_id) {
		sched->setLabel(m_labeled_activity_id);
		m_labeled_activity_id = 0;
	}

	std::vector<PSSParser::Activity_stmtContext *> items = ctx->activity_stmt();
	for (std::vector<PSSParser::Activity_stmtContext *>::const_iterator
		it=items.begin();
		it!=items.end(); it++) {
        addActivityStmt(sched, *it);
	}

	m_activity_stmt = sched;

	DEBUG_LEAVE("visitActivity_schedule_stmt");
	return 0;
}

antlrcpp::Any AstBuilderInt::visitActivity_repeat_stmt(PSSParser::Activity_repeat_stmtContext *ctx) {
	DEBUG_ENTER("visitActivity_repeat_stmt");

	IActivityLabeledStmt *stmt = 0;

	if (ctx->is_repeat) {
		ast::IExprId *label = m_labeled_activity_id;
        ast::IScopeChild *body = mkActivityStmt(ctx->activity_stmt());
        if (!body) {
            body = m_factory->mkActivitySequence();
        }

		ast::IActivityRepeatCount *stmt = m_factory->mkActivityRepeatCount(
			(ctx->loop_var)?mkId(ctx->loop_var):0,
			mkExpr(ctx->expression()),
            body);

	} else {

	}

	if (m_labeled_activity_id) {
		stmt->setLabel(m_labeled_activity_id);
		m_labeled_activity_id = 0;
	}

	m_activity_stmt = stmt;

	DEBUG_LEAVE("visitActivity_repeat_stmt");
	return 0;
}

// B.11 Data declarations

antlrcpp::Any AstBuilderInt::visitData_declaration(PSSParser::Data_declarationContext *ctx) {
	DEBUG_ENTER("visitData_declaration");

	std::vector<PSSParser::Data_instantiationContext *> items = ctx->data_instantiation();
	for (std::vector<PSSParser::Data_instantiationContext *>::const_iterator
		it=items.begin();
		it!=items.end(); it++) {
		ast::IDataType *type = mkDataType(ctx->data_type());
		ast::IExpr *array_dim = 0;
		ast::IExpr *init = 0;

		if ((*it)->array_dim()) {
			array_dim = mkExpr((*it)->array_dim()->constant_expression()->expression());
		}

		if ((*it)->constant_expression()) {
			init = mkExpr((*it)->constant_expression()->expression());
		}

		ast::IField *field = m_factory->mkField(
			mkId((*it)->identifier()),
			type,
			FieldAttr::NoFlags,
			array_dim,
			init);

		addChild(field, ctx->start);

		if (m_field_depth > 0) {
			m_fields.push_back(field);
		}
	}
	DEBUG_LEAVE("visitData_declaration");
	return 0;
}

antlrcpp::Any AstBuilderInt::visitAttr_field(PSSParser::Attr_fieldContext *ctx) {
	DEBUG_ENTER("visitAttr_field");

	m_field_depth++;
	ctx->data_declaration()->accept(this);
	m_field_depth--;

	for (std::vector<ast::IField *>::const_iterator
		it=m_fields.begin();
		it!=m_fields.end(); it++) {
		FieldAttr attr = (*it)->getAttr();

		if (ctx->access_modifier()) {

		}

		if (ctx->is_rand) {
			attr |= FieldAttr::Rand;
		}

		if (ctx->is_const) {
			attr |= FieldAttr::Static;
			attr |= FieldAttr::Const;
		}

		(*it)->setAttr(attr);
	}

	if (!m_field_depth) {
		m_fields.clear();
	}
	DEBUG_LEAVE("visitAttr_field");
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
		width = mkExpr(ctx->lhs);
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

	ast::IDataTypeUserDefined *dt = mkDataTypeUserDefined(ctx->enum_type_identifier()->type_identifier());
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
			value = mkExpr((*it)->constant_expression()->expression());
		}

		ast::IEnumItem *item = m_factory->mkEnumItem(
			mkId((*it)->identifier()),
			value);
		decl->getItems().push_back(ast::IEnumItemUP(item));
	}

	addChild(decl, ctx->start);

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

	addChild(constraint, ctx->start);
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
//	scope->setParent(m_constraint_s.back());
	m_constraint_s.push_back(scope);
	std::vector<PSSParser::Constraint_body_itemContext *> items = ctx->constraint_body_item();
	for (std::vector<PSSParser::Constraint_body_itemContext *>::const_iterator
		it=items.begin();
		it!=items.end(); it++) {
		(*it)->accept(this);
	}
	m_constraint_s.pop_back();

	m_constraint = scope;
	if (m_constraint_s.size() > 0) {
		m_constraint_s.back()->getConstraints().push_back(ast::IConstraintStmtUP(scope));
	}

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
	m_constraint = c;
	if (m_constraint_s.size() > 0) {
		m_constraint_s.back()->getConstraints().push_back(ast::IConstraintStmtUP(c));
	}
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

	m_constraint_s.push_back(c);
	visitConstraintSetItems(ctx->constraint_set());
	m_constraint_s.pop_back();

	m_constraint = c;
	if (m_constraint_s.size() > 0) {
		m_constraint_s.back()->getConstraints().push_back(ast::IConstraintScopeUP(c));
	}
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

	m_constraint = c;
	if (m_constraint_s.size() > 0) {
		m_constraint_s.back()->getConstraints().push_back(
			IConstraintStmtUP(c));
	}

	DEBUG_LEAVE("visitIf_constraint_item");
	return 0;
}

antlrcpp::Any AstBuilderInt::visitImplication_constraint_item(PSSParser::Implication_constraint_itemContext *ctx) {
	DEBUG_ENTER("visitImplication_constraint_item");
	ast::IConstraintStmtImplication *c = m_factory->mkConstraintStmtImplication(mkExpr(ctx->expression()));

	m_constraint_s.push_back(c);
	visitConstraintSetItems(ctx->constraint_set());
	m_constraint_s.pop_back();

	m_constraint = c;
	if (m_constraint_s.size()) {
		m_constraint_s.back()->getConstraints().push_back(ast::IConstraintStmtUP(c));
	}

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
		ast::IExpr *lhs = mkExpr(ctx->lhs);

	} else if (ctx->lhs && ctx->rhs) {
		// It's some form of binary op
		ast::IExpr *lhs = mkExpr(ctx->lhs);

		ast::IExpr *rhs = mkExpr(ctx->rhs);

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
			ast::IExpr *cond = mkExpr(ctx->lhs);

			ast::IExpr *true_e = mkExpr(ctx->conditional_expr()->true_expr);

			ast::IExpr *false_e = mkExpr(ctx->conditional_expr()->false_expr);

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
	ast::IExpr *expr = mkExpr(ctx->expression());

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
	fprintf(stdout, "Error: Syntax error\n");
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

void AstBuilderInt::addChild(ast::IScopeChild *c, Token *t) {
	scope()->getChildren().push_back(ast::IScopeChildUP(c));
	c->setParent(scope());

	if (m_collectDocStrings && t) {
		addDocstring(c, t);
	}
}

void AstBuilderInt::addChild(ast::INamedScopeChild *c, Token *t) {
	scope()->getChildren().push_back(ast::IScopeChildUP(c));
	c->setParent(scope());

	if (m_collectDocStrings && t) {
		addDocstring(c, t);
	}
}

void AstBuilderInt::addChild(ast::INamedScope *c, Token *t) {
	scope()->getChildren().push_back(ast::IScopeChildUP(c));

	if (m_collectDocStrings && t) {
		addDocstring(c, t);
	}
}

void AstBuilderInt::addDocstring(ast::IScopeChild *c, Token *t) {
	DEBUG_ENTER("addDocstring");
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

	DEBUG("docstring=%s", docstring.c_str());
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
	DEBUG_LEAVE("addDocstring");
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

void AstBuilderInt::push_scope(ast::IScope *s) { 
	DEBUG("-- push_scope");
	m_scopes.push_back(s); 
}

void AstBuilderInt::pop_scope() { 
	DEBUG("-- pop_scope");
	m_scopes.pop_back(); 
}

ast::IActivityJoinSpec *AstBuilderInt::mkActivityJoinSpec(PSSParser::Activity_join_specContext *ctx) {
	DEBUG_ENTER("mkActivityoinSpec");
	ast::IActivityJoinSpec *spec = 0;
	DEBUG("TODO: mkActivityJoinSpec");

	DEBUG_LEAVE("mkActivityoinSpec");
	return spec;
}

ast::IScopeChild *AstBuilderInt::mkActivityStmt(PSSParser::Activity_stmtContext *ctx) {
	DEBUG_ENTER("mkActivityStmt");
	m_activity_stmt = 0;
	ctx->accept(this);
	DEBUG_LEAVE("mkActivityStmt");
	return m_activity_stmt;
}

void AstBuilderInt::addActivityStmt(
        ast::IScope                         *scope,
        PSSParser::Activity_stmtContext     *ctx) {
    ast::IScopeChild *a_stmt = mkActivityStmt(ctx);
    if (a_stmt) {
        scope->getChildren().push_back(ast::IScopeChildUP(a_stmt));
    }
}

ast::IConstraintStmt *AstBuilderInt::mkConstraintSet(PSSParser::Constraint_setContext *ctx) {
	m_constraint = 0;
	ctx->accept(this);
	return m_constraint;
}

ast::IDataType *AstBuilderInt::mkDataType(PSSParser::Data_typeContext *ctx) {
	m_type = 0;
	ctx->accept(this);
	return m_type;
}

ast::IDataTypeUserDefined *AstBuilderInt::mkDataTypeUserDefined(PSSParser::Type_identifierContext *ctx) {
	DEBUG_ENTER("mkDataTypeUserDefined");
	// std::vector<PSSParser::Type_identifier_elemContext *> items = ctx->type_identifier_elem();

	// for (std::vector<PSSParser::Type_identifier_elemContext *>::const_iterator
	// 	it=items.begin();
	// 	it!=items.end(); it++) {
	// 	ret->getElems().push_back(ast::ITypeIdentifierElemUP(
	// 		m_factory->mkTypeIdentifierElem(mkId((*it)->identifier()))));
	// }

	ast::IDataTypeUserDefined *ret = m_factory->mkDataTypeUserDefined(
		ctx->is_global,
		mkTypeId(ctx));

	DEBUG_LEAVE("mkDataTypeUserDefined");

	return ret;
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
			lhs = mkExpr((*it)->lhs);
		}

		ast::IExpr *rhs = 0;
		if ((*it)->rhs) {
			rhs = mkExpr((*it)->rhs);
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

ast::IExecStmt *AstBuilderInt::mkExecStmt(PSSParser::Procedural_stmtContext *ctx) {
    m_exec_stmt = 0;
    ctx->accept(this);
    return m_exec_stmt;
}

void AstBuilderInt::addExecStmt(PSSParser::Procedural_stmtContext *ctx) {
    ast::IExecStmt *stmt = mkExecStmt(ctx);

    if (stmt) {
        m_exec_scope_s.back()->getChildren().push_back(ast::IExecStmtUP(stmt));
    }

}

static std::map<std::string, ParamDir> param_dir_m = {
    { "input", ParamDir::ParamDir_In},
    { "output", ParamDir::ParamDir_Out},
    { "inout", ParamDir::ParamDir_InOut}
};

ast::IFunctionPrototype *AstBuilderInt::mkFunctionPrototype(
    PSSParser::Function_prototypeContext *ctx) {
    ast::IDataType *rtype = 0;

    if (ctx->function_return_type()->data_type()) {
        rtype = mkDataType(ctx->function_return_type()->data_type());
    }

    ast::IFunctionPrototype *proto = m_factory->mkFunctionPrototype(
        mkId(ctx->function_identifier()->identifier()),
        rtype);

    std::vector<PSSParser::Function_parameterContext *> items =
        ctx->function_parameter_list_prototype()->function_parameter();
    for (std::vector<PSSParser::Function_parameterContext *>::const_iterator
        it=items.begin();
        it!=items.end(); it++) {
        ParamDir dir = ParamDir::ParamDir_Default;

        if ((*it)->function_parameter_dir()) {
            dir = param_dir_m.find((*it)->function_parameter_dir()->toString())->second;
        }
        ast::IDataType *type = mkDataType((*it)->data_type());
        ast::IExprId *name = mkId((*it)->identifier());
        ast::IExpr *dflt = 0;
        if ((*it)->constant_expression()) {
            dflt = mkExpr((*it)->constant_expression()->expression());
        }
        ast::IFunctionParamDecl *param = m_factory->mkFunctionParamDecl(
            name,
            type,
            dir,
            dflt,
            false);
        proto->getParameters().push_back(ast::IFunctionParamDeclUP(param));
    }

    return proto;
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

	return id;
}

ast::IExprHierarchicalId *AstBuilderInt::mkHierarchicalId(PSSParser::Hierarchical_idContext *ctx) {
	DEBUG_ENTER("mkHierarchicalId");
	ast::IExprHierarchicalId *ret = m_factory->mkExprHierarchicalId();
	std::vector<PSSParser::Member_path_elemContext *> items = ctx->member_path_elem();

	for (std::vector<PSSParser::Member_path_elemContext *>::const_iterator
		it=items.begin();
		it!=items.end(); it++) {
		// TODO:
	}

	DEBUG_LEAVE("mkHierarchicalId");
	return ret;
}

ast::IExprMemberPathElem *AstBuilderInt::mkMemberPathElem(
    PSSParser::Member_path_elemContext *ctx) {
    ast::IExprId *id = 0;
    ast::IMethodParameterList *params = 0;
    ast::IExpr *subscript = 0;

    id = mkId(ctx->identifier());

    if (ctx->function_parameter_list()) {
        params = m_factory->mkMethodParameterList();
        std::vector<PSSParser::ExpressionContext *> plist =
            ctx->function_parameter_list()->expression();
        for (std::vector<PSSParser::ExpressionContext *>::const_iterator
            it=plist.begin();
            it!=plist.end(); it++) {
            params->getParameters().push_back(ast::IExprUP(mkExpr(*it)));
        }
    }

    if (ctx->expression()) {
        subscript = mkExpr(ctx->expression());
    }

    return m_factory->mkExprMemberPathElem(
        id,
        params,
        subscript);
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

	if (elems.size() == 0) {
		fprintf(stdout, "Error: elems.size==0\n");
	}

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

ast::ITypeIdentifierElem *AstBuilderInt::mkTypeIdElem(
		PSSParser::Type_identifier_elemContext		*ctx) {
	ast::ITypeIdentifierElem *elem = m_factory->mkTypeIdentifierElem(
			mkId(ctx->identifier()));
    return elem;
}

ast::IExpr *AstBuilderInt::mkExpr(
		PSSParser::ExpressionContext 			*ctx) {
	m_expr = 0;
	ctx->accept(this);
	return m_expr;
}

dmgr::IDebug *AstBuilderInt::m_dbg = 0;

}
}
