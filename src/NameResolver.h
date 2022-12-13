/*
 * NameResolver.h
 *
 *  Created on: Oct 29, 2020
 *      Author: ballance
 */

#pragma once
#include "zsp/INameResolver.h"
#include "zsp/INameResolverClient.h"
#include "zsp/ast/impl/VisitorBase.h"
#include "zsp/IMarkerListener.h"
#include "zsp/ISymbolTable.h"

namespace zsp {

class NameResolver : 
    public virtual INameResolver,
    public virtual ast::VisitorBase {
public:
	NameResolver(
            ISymbolTable                *symtab,
			IMarkerListener             *marker);

	virtual ~NameResolver();

	void resolve(ast::IGlobalScope *root);

    virtual void visitDataTypeUserDefined(ast::IDataTypeUserDefined *i) override;

private:
    ISymbolTable                        *m_symtab;
    IMarkerListener						*m_marker_l;
    std::vector<ast::IGlobalScope *>	m_context;
    uint32_t							m_phase;
    std::vector<ast::IScope *>			m_scopes;
};

} /* namespace zsp */

