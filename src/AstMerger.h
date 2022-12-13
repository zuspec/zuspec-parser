/**
 * AstMerger.h
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
#include <map>
#include <memory>
#include <vector>
#include "zsp/ast/IFactory.h"
#include "zsp/ast/impl/VisitorBase.h"

namespace zsp {

class AstMerger : public virtual ast::VisitorBase {
public:
    AstMerger(ast::IFactory *factory);

    virtual ~AstMerger();

    virtual ast::IGlobalScope *merge(
        const std::vector<ast::IGlobalScope *> &asts);

    virtual void visitPackageScope(ast::IPackageScope *i) override;

    virtual void visitScopeChild(ast::IScopeChild *i) override;

private:
    struct Scope;
    using ScopeUP=std::unique_ptr<Scope>;
    struct Scope {
        Scope(ast::IScope *s) : scope(s) { }
        ast::IScope                     *scope;
        std::map<std::string, ScopeUP>  subscope_m;
    };

private:
    ast::IFactory            *m_factory;
    std::vector<Scope *>     m_scope_s;

};

}
