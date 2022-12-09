/*
 * Marker.cpp
 *
 *  Created on: Oct 8, 2020
 *      Author: ballance
 */

#include "Marker.h"

namespace zsp {

Marker::Marker(
		const std::string	&msg,
		MarkerSeverityE		severity,
		const ast::Location	&loc) :
				m_msg(msg), m_severity(severity), m_loc(loc) {
	// TODO Auto-generated constructor stub

}

Marker::~Marker() {
	// TODO Auto-generated destructor stub
}

IMarker *Marker::clone() const {
	return new Marker(m_msg, m_severity, m_loc);
}

} /* namespace pls */
