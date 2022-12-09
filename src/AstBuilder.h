/*
 * AstBuilder.h
 *
 *  Created on: Oct 10, 2020
 *      Author: ballance
 */

#pragma once
#include <memory>
#include <iostream>
#include "zsp/ast/IFactory.h"
#include "zsp/ast/IGlobalScope.h"
#include "zsp/IMarkerListener.h"

namespace zsp {

class AstBuilderInt;
typedef std::unique_ptr<AstBuilderInt> AstBuilderIntUP;

class AstBuilder {
public:
	AstBuilder(
		ast::IFactory		*factory,
		IMarkerListener 	*marker_l);

	virtual ~AstBuilder();

	void build(
			ast::IGlobalScope	*global,
			std::istream		*in);

private:
	AstBuilderIntUP				m_builder_int;
};

} /* namespace zsp */

