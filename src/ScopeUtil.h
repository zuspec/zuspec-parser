/*
 * ScopeUtil.h
 *
 *  Created on: Oct 29, 2020
 *      Author: ballance
 */

#pragma once
#include "zsp/ast/IExprId.h"
#include "zsp/ast/INamedScopeChild.h"
#include "zsp/ast/IScope.h"
#include "zsp/ast/IScopeChild.h"

namespace zsp {

class ScopeUtil {
public:
	ScopeUtil();

	virtual ~ScopeUtil();

	static ast::INamedScopeChild *findChild(ast::IScope *s, const std::string &name);

	static bool addChild(ast::IScope *s, ast::INamedScopeChild *c);

	static void addChild(ast::IScope *s, ast::IScopeChild *c);
};

} /* namespace zsp */

