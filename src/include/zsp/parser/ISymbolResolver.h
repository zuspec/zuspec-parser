
#pragma once
#include "zsp/ast/INamedScopeChild.h"

namespace zsp {
namespace parser {

class ISymbolScope;

struct ResolveResult {
    bool                                is_terminal;
    union {
        zsp::ast::INamedScopeChild     *terminal;
        ISymbolScope                    *scope;
    };
};

class ISymbolResolver {
public:

    virtual ~ISymbolResolver() { }

    virtual bool resolve(
        const std::string       &name,
        ResolveResult           &result) = 0;

};

}
}

