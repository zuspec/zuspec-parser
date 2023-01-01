/**
 * ILinker.h
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
#include "zsp/parser/IMarkerListener.h"
#include "zsp/ast/ISymbolScope.h"

namespace zsp {
namespace parser {

class ILinker;
using ILinkerUP=std::unique_ptr<ILinker>;
class ILinker {
public:

    virtual ~ILinker() { }

    virtual ast::ISymbolScope *link(
        IMarkerListener                         *marker_l,
        const std::vector<ast::IGlobalScope *>  &scopes) = 0;

};

}
} /* namespace zsp */


