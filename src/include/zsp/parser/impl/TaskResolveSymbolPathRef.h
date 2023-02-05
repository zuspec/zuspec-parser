/**
 * TaskResolveSymbolPathRef.h
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
#include <vector>
#include "zsp/ast/ISymbolScope.h"
#include "zsp/ast/ISymbolRefPath.h"
#include "zsp/ast/ISymbolTypeScope.h"

namespace zsp {
namespace parser {



class TaskResolveSymbolPathRef {
public:
    TaskResolveSymbolPathRef(ast::ISymbolScope *root) : m_root(root) { }

    virtual ~TaskResolveSymbolPathRef() { }


    ast::IScopeChild *resolve(const ast::ISymbolRefPath *ref) {
        ast::IScopeChild *ret = 0;
        ast::ISymbolScope *scope = m_root;

        for (std::vector<ast::SymbolRefPathElem>::const_iterator
            it=ref->getPath().begin();
            it!=ref->getPath().end(); it++) {
            
            switch (it->kind) {
                case ast::SymbolRefPathElemKind::ElemKind_ChildIdx: {
                    ret = scope->getChildren().at(it->idx);
                } break;
                case ast::SymbolRefPathElemKind::ElemKind_ParamIdx: {
                    ast::ISymbolTypeScope *scope_ts = dynamic_cast<ast::ISymbolTypeScope *>(scope);
                    ret = scope_ts->getPlist()->getChildren().at(it->idx);
                } break;
                case ast::SymbolRefPathElemKind::ElemKind_Super: {
                    ast::ISymbolTypeScope *scope_ts = dynamic_cast<ast::ISymbolTypeScope *>(scope);
                    fprintf(stdout, "TODO: handle super ref\n");
                    fflush(stdout);
                } break;
                case ast::SymbolRefPathElemKind::ElemKind_TypeSpec: {
                    ast::ISymbolTypeScope *scope_ts = dynamic_cast<ast::ISymbolTypeScope *>(scope);
                    ret = scope_ts->getSpec_types().at(it->idx).get();
                } break;
                default:
                    fprintf(stdout, "TODO: handle ElemKind %d\n", it->kind);
                    fflush(stdout);
                    break;
            }
            
            if (it+1 != ref->getPath().end()) {
                scope = dynamic_cast<ast::ISymbolScope *>(ret);
            }
        }

        return ret;
    }

    template <class T> T *resolveT(const ast::ISymbolRefPath *ref) {
        return dynamic_cast<T *>(resolve(ref));
    }

private:
    ast::ISymbolScope                           *m_root;


};

}
}


