
#pragma once
#include "zsp/IAstBuilder.h"
#include "zsp/ILinker.h"
#include "zsp/IMarkerCollector.h"
#include "zsp/IMarkerListener.h"
#include "zsp/INameResolver.h"
#include "zsp/ISymbolTable.h"
#include "zsp/ast/IFactory.h"

namespace zsp {

class IAstBuilder;
class IMarkerListener;

class IFactory;
using IFactoryUP=std::unique_ptr<IFactory>;
class IFactory {
public:

    virtual ~IFactory() { }

    virtual void init(ast::IFactory *ast_factory) = 0;

    virtual ast::IFactory *getAstFactory() = 0;

    virtual IAstBuilder *mkAstBuilder(IMarkerListener *marker_l) = 0;

    virtual ILinker *mkAstLinker() = 0;

    virtual ISymbolTableIterator *mkAstSymbolTableIterator(
        ast::ISymbolScope       *root) = 0;

    virtual IMarker *mkMarker(
        const std::string           &msg,
        MarkerSeverityE             severity,
        const ast::Location         &loc) = 0;

    virtual IMarkerCollector *mkMarkerCollector() = 0;

    virtual INameResolver *mkNameResolver(
        ISymbolTable            *symtab,
        IMarkerListener         *marker_l) = 0;


    virtual ISymbolTable *mkSymbolTable() = 0;

};

}