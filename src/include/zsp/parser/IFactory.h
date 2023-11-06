
#pragma once
#include "dmgr/IDebugMgr.h"
#include "zsp/ast/IFactory.h"
#include "zsp/parser/IAstBuilder.h"
#include "zsp/parser/ILinker.h"
#include "zsp/parser/IMarkerCollector.h"
#include "zsp/parser/IMarkerListener.h"
#include "zsp/parser/INameResolver.h"
#include "zsp/parser/ISymbolTable.h"
#include "zsp/parser/ITaskFindElementByLocation.h"
#include "zsp/parser/IValFactory.h"

namespace zsp {
namespace parser {

class IAstBuilder;
class IMarkerListener;

class IFactory;
using IFactoryUP=std::unique_ptr<IFactory>;
class IFactory : public virtual IValFactory {
public:

    virtual ~IFactory() { }

    virtual void init(
        dmgr::IDebugMgr     *dmgr,
        ast::IFactory       *ast_factory) = 0;

    virtual ast::IFactory *getAstFactory() = 0;

    virtual dmgr::IDebugMgr *getDebugMgr() = 0;

    virtual void loadStandardLibrary(
        IAstBuilder             *ast_builder,
        ast::IGlobalScope       *global) = 0;

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

    virtual ITaskFindElementByLocation *mkTaskFindElementByLocation() = 0;

};

}
}
