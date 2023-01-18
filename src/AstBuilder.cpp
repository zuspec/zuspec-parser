/*
 * AstBuilder.cpp
 *
 *  Created on: Oct 10, 2020
 *      Author: ballance
 */

#include <stdio.h>
#include "AstBuilder.h"

#include "AstBuilderInt.h"

namespace zsp {
namespace parser {


AstBuilder::AstBuilder(
    dmgr::IDebugMgr     *dmgr,
	ast::IFactory		*factory,
	IMarkerListener 	*marker_l) :
	m_builder_int(new AstBuilderInt(dmgr, factory, marker_l)) {
	// TODO Auto-generated constructor stub

}

AstBuilder::~AstBuilder() {
	// TODO Auto-generated destructor stub
}

void AstBuilder::build(
		ast::IGlobalScope	*global,
		std::istream		*in) {
	m_builder_int->build(global, in);
}

}
} /* namespace zsp */
