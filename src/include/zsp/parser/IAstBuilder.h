/*
 * IAstBuilder.h
 *
 *  Created on: May 27, 2022
 *      Author: mballance
 */

#pragma once
#include <iostream>
#include <memory>
#include "zsp/parser/IMarkerListener.h"
#include "zsp/ast/IGlobalScope.h"
#include "zsp/ast/IFactory.h"


namespace zsp {
namespace parser {

class IAstBuilder;
using IAstBuilderUP=std::unique_ptr<IAstBuilder>;
class IAstBuilder {
public:

	virtual ~IAstBuilder() { }

	virtual void build(
		ast::IGlobalScope		*global,
		std::istream			*in) = 0;

    virtual zsp::ast::IFactory *getFactory() = 0;

    virtual void setMarkerListener(IMarkerListener *l) = 0;

};

}
}
