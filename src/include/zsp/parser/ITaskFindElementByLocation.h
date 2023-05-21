/**
 * ITaskFindElementByLocation.h
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
#include <vector>
#include "zsp/ast/IScopeChild.h"
#include "zsp/ast/ISymbolScope.h"

namespace zsp {
namespace parser {


class ITaskFindElementByLocation;
using ITaskFindElementByLocationUP=std::unique_ptr<ITaskFindElementByLocation>;
class ITaskFindElementByLocation {
public:
    struct Result {
        bool                isValid;
        bool                isType;
        ast::IScopeChild    *target;
        std::string         docComment;
    };
public:

    virtual ~ITaskFindElementByLocation() { }

    virtual ITaskFindElementByLocation::Result find(
        ast::ISymbolScope                   *root,
        ast::IGlobalScope                   *file,
        int32_t                             lineno,
        int32_t                             linepos) = 0;

};

} /* namespace parser */
} /* namespace zsp */


