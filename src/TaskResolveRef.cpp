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

ast::IScopeChild *TaskResolveRef::resolve(
        ISymbolTableIterator            *scope,
        ast::ITypeIdentifier            *type_id) {
    ast::IScopeChild *ret = 0;
    DEBUG_ENTER("resolve");
	ISymbolTableIteratorUP it(scope->clone());

	// Find the first element

	fprintf(stdout, "Searching for %s\n", type_id->getElems().at(0)->getId()->getId().c_str());
	for (std::vector<ast::ITypeIdentifierElemUP>::const_iterator
		ti_it=type_id->getElems().begin();
		ti_it!=type_id->getElems().end(); ti_it++) {

		if (ti_it == type_id->getElems().begin()) {
			while (it->hasScopes()) {
                if ((ret=it->findSymbol((*ti_it)->getId()->getId()))) {
                    DEBUG("Found");

                    if (ti_it+1 != type_id->getElems().end()) {
        				if (!it->pushNamedScope((*ti_it)->getId()->getId())) {
                            DEBUG("Error: found a symbol, but it's not a scope");
                            ret = 0;
                        }
                    }
					break;
				} else {
					DEBUG("Uplevel");
					it->popScope();
				}
			}

			if (!ret) {
				DEBUG("Error: Failed to find first type elem %s\n",
                    (*ti_it)->getId()->getId().c_str());
                break;
			}
		} else {
            if ((ret=it->findSymbol((*ti_it)->getId()->getId()))) {
                DEBUG("Found");
                if (ti_it+1 != type_id->getElems().end()) {
     				if (!it->pushNamedScope((*ti_it)->getId()->getId())) {
                        DEBUG("Error: found a symbol, but it's not a scope");
                        ret = 0;
                    }
                }
            } else {
				DEBUG("... failed to find subsequent element");
				break;
			}
		}
	}

    DEBUG_LEAVE("resolve %p", ret);
    return ret;
}

}
