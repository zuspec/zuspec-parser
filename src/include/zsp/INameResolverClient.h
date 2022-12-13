/**
 * INameResolverClient.h
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
#include "zsp/INamespace.h"
#include "zsp/INameResolver.h"

namespace zsp {


class INameResolverClient {
public:

    virtual ~INameResolverClient() { }

    virtual void init(INameResolver *resolver) = 0;

    virtual INamespace *getGlobalNamespace() = 0;

    /**
     * @brief Defines a new interface object to represent
     *        the specified AST object. 
     * 
     */
    virtual ITypeDecl *defineType(ast::ITypeScope *ast) = 0;

};

} /* namespace zsp */


