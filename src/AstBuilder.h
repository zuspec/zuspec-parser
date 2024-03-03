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

    virtual zsp::ast::IFactory *getFactory() override;

    virtual void setMarkerListener(IMarkerListener *l) override;

    virtual void setCollectDocStrings(bool c) override;

    virtual bool getCollectDocStrings() override;

    virtual void setEnableProfile(bool e) override;

    virtual bool getEnableProfile() override;

private:
	AstBuilderIntUP				m_builder_int;
};

}
} /* namespace zsp */

