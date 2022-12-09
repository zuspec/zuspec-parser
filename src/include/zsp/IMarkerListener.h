/*
 * IMarkerListener.h
 *
 *  Created on: Sep 13, 2020
 *      Author: ballance
 */

#pragma once
#include "zsp/IMarker.h"

namespace zsp {

class IMarkerListener {
public:
	virtual ~IMarkerListener() { }

	virtual void marker(const IMarker *m) = 0;

	virtual bool hasSeverity(MarkerSeverityE s) = 0;

};

}
