/*
 * Marker.h
 *
 *  Created on: Oct 8, 2020
 *      Author: ballance
 */

#pragma once
#include <memory>
#include <string>
#include "zsp/IMarker.h"
#include "zsp/ast/Location.h"

namespace zsp {

class Marker : public IMarker {
public:
	Marker(
			const std::string	&msg,
			MarkerSeverityE		severity,
			const ast::Location	&loc);

	virtual ~Marker();

	virtual const std::string &msg() const override { 
		return m_msg; 
	}

    virtual void setMsg(const std::string &m) override {
		m_msg = m;
	}

	virtual MarkerSeverityE severity() const override { 
		return m_severity; 
	}

    virtual void setSeverity(MarkerSeverityE s) override {
		m_severity = s;
	}

	virtual const ast::Location &loc() const override { 
		return m_loc; 
	}

    virtual void setLocation(const ast::Location &l) override {
		m_loc = l;
	}

	virtual IMarker *clone() const override;
	

private:
	std::string			m_msg;
	MarkerSeverityE		m_severity;
	ast::Location		m_loc;

};

typedef std::unique_ptr<Marker> MarkerUP;

} /* namespace pls */

