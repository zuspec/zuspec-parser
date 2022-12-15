
#pragma once
#include "zsp/IAstBuilder.h"
#include "zsp/IMarkerListener.h"
#include "zsp/INameResolver.h"
#include "zsp/ISymbolTable.h"
#include "zsp/ast/IFactory.h"

namespace zsp {

class IAstBuilder;
class IMarkerListener;

class IFactory {
public:

    virtual ~IFactory() { }

    virtual ast::IFactory *getAstFactory() = 0;

    virtual IAstBuilder *mkAstBuilder(IMarkerListener *marker_l) = 0;

    virtual ISymbolTableIterator *mkAstSymbolTableIterator(
        ast::ISymbolScope       *root) = 0;

    virtual INameResolver *mkNameResolver(
        ISymbolTable            *symtab,
        IMarkerListener         *marker_l) = 0;


    virtual ISymbolTable *mkSymbolTable() = 0;

};

}