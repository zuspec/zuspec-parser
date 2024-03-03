/*
 * AstBuilder.cpp
 *
 * Copyright 2022 Matthew Ballance and Contributors
 *
 * Licensed under the Apache License, Version 2.0 (the "License"); you may 
 * not use this file except in compliance with the License.  
 * You may obtain a copy of the License at:
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software 
 * distributed under the License is distributed on an "AS IS" BASIS, 
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  
 * See the License for the specific language governing permissions and 
 * limitations under the License.
 *
 * Created on:
 *     Author:
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

zsp::ast::IFactory *AstBuilder::getFactory() {
    return m_builder_int->getFactory();
}

void AstBuilder::setMarkerListener(IMarkerListener *l) {
    m_builder_int->setMarkerListener(l);
}

void AstBuilder::setCollectDocStrings(bool c) {
    m_builder_int->setCollectDocStrings(c);
}

bool AstBuilder::getCollectDocStrings() {
    return m_builder_int->getCollectDocStrings();
}

void AstBuilder::setEnableProfile(bool e) {
    m_builder_int->setEnableProfile(e);
}

bool AstBuilder::getEnableProfile() {
    return m_builder_int->getEnableProfile();
}

}
} /* namespace zsp */
