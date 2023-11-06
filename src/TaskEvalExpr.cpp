/*
 * TaskEvalExpr.cpp
 *
 * Copyright 2023 Matthew Ballance and Contributors
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
#include "dmgr/impl/DebugMacros.h"
#include "TaskEvalExpr.h"


namespace zsp {
namespace parser {


TaskEvalExpr::TaskEvalExpr(IFactory *factory) : m_factory(factory) {
    DEBUG_INIT("zsp::parser::TaskEvalExpr", factory->getDebugMgr());
}

TaskEvalExpr::~TaskEvalExpr() {

}

IVal *TaskEvalExpr::eval(ast::IExpr *expr) {
    m_val.reset();
    expr->accept(m_this);
    return m_val.release();
}

void TaskEvalExpr::visitExprAggregateLiteral(ast::IExprAggregateLiteral *i) {
    DEBUG_ENTER("visitExprAggregateLiteral");
    DEBUG("TODO: visitExprAggregateLiteral");
    DEBUG_LEAVE("visitExprAggregateLiteral");
}

void TaskEvalExpr::visitExprBin(ast::IExprBin *i) {
    DEBUG_ENTER("visitExprBin");
    DEBUG("TODO: visitExprBin");
    DEBUG_LEAVE("visitExprBin");
}

void TaskEvalExpr::visitExprBitSlice(ast::IExprBitSlice *i) {
    DEBUG_ENTER("visitExprBitSlice");
    DEBUG("TODO: visitExprBitSlice");
    DEBUG_LEAVE("visitExprBitSlice");
}

void TaskEvalExpr::visitExprBool(ast::IExprBool *i) {
    DEBUG_ENTER("visitExprBool");
    DEBUG("TODO: visitExprBool");
    DEBUG_LEAVE("visitExprBool");
}

void TaskEvalExpr::visitExprCast(ast::IExprCast *i) {
    DEBUG_ENTER("visitExprCast");
    DEBUG("TODO: visitExprCast");
    DEBUG_LEAVE("visitExprCast");
}

void TaskEvalExpr::visitExprCompileHas(ast::IExprCompileHas *i) {
    DEBUG_ENTER("visitExprCompileHas");
    DEBUG("TODO: visitExprCompileHas");
    DEBUG_LEAVE("visitExprCompileHas");
}

void TaskEvalExpr::visitExprCond(ast::IExprCond *i) {
    DEBUG_ENTER("visitExprCond");
    DEBUG("TODO: visitExprCond");
    DEBUG_LEAVE("visitExprCond");
}

void TaskEvalExpr::visitExprDomainOpenRangeList(ast::IExprDomainOpenRangeList *i) {
    DEBUG_ENTER("visitExprDomainOpenRangeList");
    DEBUG("TODO: visitExprDomainOpenRangeList");
    DEBUG_LEAVE("visitExprDomainOpenRangeList");
}

void TaskEvalExpr::visitExprDomainOpenRangeValue(ast::IExprDomainOpenRangeValue *i) {
    DEBUG_ENTER("visitExprDomainOpenRangeValue");
    DEBUG("TODO: visitExprDomainOpenRangeValue");
    DEBUG_LEAVE("visitExprDomainOpenRangeValue");
}

void TaskEvalExpr::visitExprId(ast::IExprId *i) {
    DEBUG_ENTER("visitExprId");
    DEBUG("TODO: visitExprId");
    DEBUG_LEAVE("visitExprId");
}

void TaskEvalExpr::visitExprIn(ast::IExprIn *i) {
    DEBUG_ENTER("visitExprIn");
    DEBUG("TODO: visitExprIn");
    DEBUG_LEAVE("visitExprIn");
}

void TaskEvalExpr::visitExprOpenRangeList(ast::IExprOpenRangeList *i) {
    DEBUG_ENTER("visitExprOpenRangeList");
    DEBUG("TODO: visitExprOpenRangeList");
    DEBUG_LEAVE("visitExprOpenRangeList");
}

void TaskEvalExpr::visitExprOpenRangeValue(ast::IExprOpenRangeValue *i) {
    DEBUG_ENTER("visitExprOpenRangeValue");
    DEBUG("TODO: visitExprOpenRangeValue");
    DEBUG_LEAVE("visitExprOpenRangeValue");
}

void TaskEvalExpr::visitExprNull(ast::IExprNull *i) {
    DEBUG_ENTER("visitExprNull");
    DEBUG("TODO: visitExprNull");
    DEBUG_LEAVE("visitExprNull");
}

void TaskEvalExpr::visitExprSignedNumber(ast::IExprSignedNumber *i) {
    DEBUG_ENTER("visitExprSignedNumber");
    m_val = IValUP(m_factory->mkValInt(true, i->getWidth(), i->getValue()));
    DEBUG_LEAVE("visitExprSignedNumber");
}

void TaskEvalExpr::visitExprString(ast::IExprString *i) {
    DEBUG_ENTER("visitExprString");
    DEBUG("TODO: visitExprString");
    DEBUG_LEAVE("visitExprString");
}

void TaskEvalExpr::visitExprSubscript(ast::IExprSubscript *i) {
    DEBUG_ENTER("visitExprSubscript");
    DEBUG("TODO: visitExprSubscript");
    DEBUG_LEAVE("visitExprSubscript");
}

void TaskEvalExpr::visitExprUnary(ast::IExprUnary *i) {
    DEBUG_ENTER("visitExprUnary");
    DEBUG("TODO: visitExprUnary");
    DEBUG_LEAVE("visitExprUnary");
}

void TaskEvalExpr::visitExprUnsignedNumber(ast::IExprUnsignedNumber *i) {
    DEBUG_ENTER("visitExprUnsignedNumber");
    m_val = IValUP(m_factory->mkValInt(false, i->getWidth(), i->getValue()));
    DEBUG_LEAVE("visitExprUnsignedNumber");
}

dmgr::IDebug *TaskEvalExpr::m_dbg = 0;

}
}
