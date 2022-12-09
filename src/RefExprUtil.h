/*
 * RefExprUtil.h
 *
 *  Created on: Oct 30, 2020
 *      Author: ballance
 */

#include "zsp/ast/IRefExpr.h"
#include "zsp/ast/IRefExprTypeScopeGlobal.h"
#include "zsp/ast/IRefExprTypeScopeContext.h"
#include "zsp/ast/IRefExprScopeIndex.h"

namespace zsp {

class RefExprUtil {
public:
	RefExprUtil();

	virtual ~RefExprUtil();

	static ast::IRefExprTypeScopeGlobalSP mkTypeScopeGlobal(int32_t fileid);

	static ast::IRefExprScopeIndexSP mkScopeIndex(ast::IRefExprSP base, int32_t index);
};

} /* namespace zsp */

