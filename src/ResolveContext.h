/**
 * ResolveContext.h
 *
 * Copyright 2023 Matthew Ballance and Contributors
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
#include <stdint.h>
#include <string>
#include <vector>
#include "dmgr/IDebugMgr.h"
#include "zsp/ast/ISymbolRefPath.h"
#include "zsp/parser/IFactory.h"
#include "zsp/parser/IMarkerListener.h"
#include "zsp/parser/ISymbolTableIterator.h"

namespace zsp {
namespace parser {



class ResolveContext {
public:
    ResolveContext(
        IFactory            *factory,
        IMarkerListener     *marker_l,
        ast::ISymbolScope   *root);

    virtual ~ResolveContext();

    ast::ISymbolScope *root() const { return m_root; }

    void pushInlineCtxt(ast::ISymbolScope *s) {
        m_inline_ctxt_s.push_back(s);
    }

    ast::ISymbolScope *inlineCtxt() const { 
        return (m_inline_ctxt_s.size())?m_inline_ctxt_s.back():0;
    }

    void popInlineCtxt() {
        m_inline_ctxt_s.pop_back();
    }

    IFactory *getFactory() const { return m_factory; }

    dmgr::IDebugMgr *getDebugMgr() const { return m_factory->getDebugMgr(); }

    int32_t specializationDepth() const { return m_specialization_depth; }

    void incSpecializationDepth() { m_specialization_depth++; }

    void decSpecializationDepth() { m_specialization_depth--; }

    void pushSymtab(ISymbolTableIterator *t) {
        m_symtab_it_s.push_back(ISymbolTableIteratorUP(t));
    }

    void pushCloneSymtab() {
        pushSymtab(cloneSymtab());
    }

    const ISymbolTableIterator *symtab() const {
        return (m_symtab_it_s.size())?m_symtab_it_s.back().get():0;
    }

    ISymbolTableIterator *symtab() {
        return (m_symtab_it_s.size())?m_symtab_it_s.back().get():0;
    }

    ISymbolTableIterator *cloneSymtab() const {
        return (m_symtab_it_s.size())?m_symtab_it_s.back()->clone():0;
    }

    void popSymtab() {
        m_symtab_it_s.pop_back();
    }

    ast::IScopeChild *resolveSymbolPathRef(ast::ISymbolRefPath *path);

    void addMarker(
        MarkerSeverityE     severity,
        const ast::Location &loc,
        const char          *fmt,
        va_list             ap);

    void addMarker(
        MarkerSeverityE     severity,
        const ast::Location &loc,
        const char          *fmt,
        ...);

    void addErrorMarker(
        const ast::Location &loc,
        const char          *fmt,
        ...);

private:
    ast::ISymbolScope                       *m_root;
    std::vector<ast::ISymbolScope *>        m_inline_ctxt_s;
    IFactory                                *m_factory;
    IMarkerListener                         *m_marker_l;
    int32_t                                 m_specialization_depth;
    std::vector<ISymbolTableIteratorUP>     m_symtab_it_s;

};

}
}


