/*
 * MarkerCollector.cpp
 *
 *  Created on: Oct 10, 2020
 *      Author: ballance
 */

#include "MarkerCollector.h"

namespace zsp {
namespace parser {


MarkerCollector::MarkerCollector() {
	for (uint32_t i=0; i<static_cast<uint32_t>(MarkerSeverityE::NumLevels); i++) {
		m_count[i] = 0;
	}
}

MarkerCollector::~MarkerCollector() {
	// TODO Auto-generated destructor stub
}

void MarkerCollector::marker(const IMarker *m) {
    fprintf(stdout, "NOTE: Add marker \"%s\" with level %d\n", m->msg().c_str(), m->severity());
	m_markers.push_back(IMarkerUP(m->clone()));
	m_count[static_cast<uint32_t>(m->severity())]++;
    fflush(stdout);
}

bool MarkerCollector::hasSeverity(MarkerSeverityE s) {
	return m_count[static_cast<uint32_t>(s)];
}

}
} /* namespace zsp */
