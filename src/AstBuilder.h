/*
 * AstBuilder.h
 *
 *  Created on: Oct 10, 2020
 *      Author: ballance
 */

#pragma once
#include <memory>
#include <iostream>
#include "dmgr/IDebugMgr.h"
#include "zsp/parser/IAstBuilder.h"
#include "zsp/ast/IFactory.h"
#include "zsp/ast/IGlobalScope.h"
#include "zsp/parser/IMarkerListener.h"

namespace zsp {
namespace parser {


class AstBuilderInt;
typedef std::unique_ptr<AstBuilderInt> AstBuilderIntUP;

class AstBuilder : public virtual IAstBuilder {
public:
	AstBuilder(
        dmgr::IDebugMgr     *dmgr,
		ast::IFactory		*factory,
		IMarkerListener 	*marker_l);

	virtual ~AstBuilder();

	virtual void build(
			ast::IGlobalScope	*global,
			std::istream		*in) override;

private:
	AstBuilderIntUP				m_builder_int;
};

}
} /* namespace zsp */

