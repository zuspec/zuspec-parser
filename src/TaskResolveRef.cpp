/*
 * TaskResolveRef.cpp
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
#include "TaskResolveRef.h"
#include "Marker.h"

#define DEBUG_ENTER(fmt, ...) \
	fprintf(stdout, "--> TaskResolveRef::"); \
	fprintf(stdout, fmt, ##__VA_ARGS__); \
	fprintf(stdout, "\n");

#define DEBUG(fmt, ...) \
	fprintf(stdout, "TaskResolveRef: "); \
	fprintf(stdout, fmt, ##__VA_ARGS__); \
	fprintf(stdout, "\n");

#define DEBUG_LEAVE(fmt, ...) \
	fprintf(stdout, "<-- TaskResolveRef::"); \
	fprintf(stdout, fmt, ##__VA_ARGS__); \
	fprintf(stdout, "\n");

namespace zsp {


TaskResolveRef::TaskResolveRef(
    IFactory                        *factory,
    IMarkerListener                 *marker_l) 
        : m_factory(factory), m_marker_l(marker_l) {

}

TaskResolveRef::~TaskResolveRef() {

}

ast::ISymbolRefPath *TaskResolveRef::resolve(
        const ISymbolTableIterator      *scope,
        ast::ITypeIdentifier            *type_id) {
    ast::ISymbolRefPath *ret = 0;
    DEBUG_ENTER("resolve");
	ISymbolTableIteratorUP it(scope->clone());

	// Find the first element

	fprintf(stdout, "Searching for %s\n", type_id->getElems().at(0)->getId()->getId().c_str());
	for (std::vector<ast::ITypeIdentifierElemUP>::const_iterator
		ti_it=type_id->getElems().begin();
		ti_it!=type_id->getElems().end(); ti_it++) {

		if (ti_it == type_id->getElems().begin()) {
			while (it->hasScopes()) {
                if ((ret=it->findLocalSymbolPath((*ti_it)->getId()->getId()))) {
                    DEBUG("Found");

                    if (ti_it+1 != type_id->getElems().end()) {
        				if (it->pushNamedScope((*ti_it)->getId()->getId()) == -1) {
							std::string msg = "Found a symbol named ";
							msg += (*ti_it)->getId()->getId() + ", but it is not a scope";

							Marker m(
								msg,
								MarkerSeverityE::Error,
								(*ti_it)->getId()->getLocation());
							m_marker_l->marker(&m);
                            DEBUG("Error: found a symbol, but it's not a scope");
                            ret = 0;
                        }
                    }
					break;
				} else {
					// Must now check imports
					ast::ISymbolScope *scope = it->getScope();

					if (scope->getImports()) {
						std::map<std::string,ast::ISymbolRefPathUP>::const_iterator imp_sym;

						imp_sym = scope->getImports()->getSymtab().find((*ti_it)->getId()->getId());
						if (imp_sym != scope->getImports()->getSymtab().end()) {
							if (imp_sym->second.get()) {
								DEBUG("Found in the import cache");
								ret = m_factory->getAstFactory()->mkSymbolRefPath();
								ret->getPath().insert(
									ret->getPath().begin(),
									imp_sym->second->getPath().begin(),
									imp_sym->second->getPath().end());
							} else {
								DEBUG("Symbol is not present in imports");
							}
						} else {
							// Need to search through imports
							ast::ISymbolRefPath *ret_t = 0;
							for (std::vector<ast::IPackageImportStmt *>::const_iterator
								imp_it=scope->getImports()->getImports().begin();
								imp_it!=scope->getImports()->getImports().end(); imp_it++) {
								if ((ret_t=searchImport(it.get(), *imp_it, (*ti_it)->getId()->getId()))) {
									// Found it.
									if (ret) {
										// Uh-oh. We have ambiguity...
										std::string msg = "Ambiguous symbol resolution when looking up ";
										msg += (*ti_it)->getId()->getId();
										Marker m(
											msg,
											MarkerSeverityE::Error,
											(*ti_it)->getId()->getLocation()
										);
										m_marker_l->marker(&m);
										delete ret_t;
										break;
									} else {
										ret = ret_t;
									}
								} 
							}

							if (ret) {
								// Stuff this in the cache for faster lookup later
								ast::ISymbolRefPath *c_ret = m_factory->getAstFactory()->mkSymbolRefPath();
								c_ret->getPath().insert(
									c_ret->getPath().begin(),
									ret->getPath().begin(),
									ret->getPath().end());
								scope->getImports()->getSymtab().insert({
									(*ti_it)->getId()->getId(), 
									ast::ISymbolRefPathUP(c_ret)
								});
							} else {
								// Don't bother searching imports for this symbol again
								scope->getImports()->getSymtab().insert({
									(*ti_it)->getId()->getId(), 
									ast::ISymbolRefPathUP(nullptr)
								});
							}
						}
					}

					if (ret) {
						// Found via imports
						break;
					} else {
						DEBUG("Uplevel");
						it->popScope();
					}
				}
			}

			if (!ret) {
				std::string msg = "Failed to find first type elem ";
				msg += (*ti_it)->getId()->getId().c_str();
				Marker m(
					msg,
					MarkerSeverityE::Error,
					(*ti_it)->getId()->getLocation());
				m_marker_l->marker(&m);
				DEBUG("Error: Failed to find first type elem %s",
                    (*ti_it)->getId()->getId().c_str());
                break;
			}
		} else {
			int32_t idx;
            if ((idx=it->findLocalSymbol((*ti_it)->getId()->getId())) != -1) {
                DEBUG("Found");
				ret->getPath().push_back(idx);
                if (ti_it+1 != type_id->getElems().end()) {
     				if (!it->pushNamedScope((*ti_it)->getId()->getId())) {
                        DEBUG("Error: found a symbol, but it's not a scope");
                        ret = 0;
                    }
                }
            } else {
				DEBUG("... failed to find subsequent element");
				if (ret) {
					delete ret;
					ret = 0;
				}
				break;
			}
		}
	}

	DEBUG("[%s] ret.path.size=%d", 
		type_id->getElems().at(0)->getId()->getId().c_str(),
		(ret)?ret->getPath().size():-1);
	if (ret) {
		for (uint32_t i=0; i<ret->getPath().size(); i++) {
			DEBUG("  Elem[%d] %d", i, ret->getPath().at(i));
		}
	}

    DEBUG_LEAVE("resolve %p", ret);
    return ret;
}

ast::ISymbolRefPath *TaskResolveRef::searchImport(
        ISymbolTableIterator            *scope,
        ast::IPackageImportStmt         *imp,
        const std::string               &sym) {
	DEBUG_ENTER("searchImport %s", sym.c_str());
	ast::ISymbolRefPath *ret = 0;
	if (!imp->getPath()->getTarget()) {
		DEBUG("Skipping, due to unset import target");
		return 0;
	}
	for (uint32_t i=0; i<imp->getPath()->getTarget()->getPath().size(); i++) {
		DEBUG("Imp Path[%d] %d", i, imp->getPath()->getTarget()->getPath().at(i));
	}
	ast::IScopeChild *target_c = scope->resolveAbsPath(imp->getPath()->getTarget());
	ast::ISymbolScope *target_s = dynamic_cast<ast::ISymbolScope *>(target_c);
	DEBUG("target_c: %p ; target_s: %p", target_c, target_s);

	if (target_s) {
		DEBUG("Have a symbol scope (%s)", target_s->getName().c_str());
		std::map<std::string, int32_t>::const_iterator it;
		it = target_s->getSymtab().find(sym);

		if (it != target_s->getSymtab().end()) {
			DEBUG("Found the symbol (%s)", sym.c_str());
			ret = m_factory->getAstFactory()->mkSymbolRefPath();
			ret->getPath().insert(
				ret->getPath().begin(),
				imp->getPath()->getTarget()->getPath().begin(),
				imp->getPath()->getTarget()->getPath().end());
			ret->getPath().push_back(it->second);
		}
	}

	DEBUG_LEAVE("searchImport %s", sym.c_str());
	return ret;
}

}
