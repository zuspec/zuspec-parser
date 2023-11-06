/**
 * TaskEvalExpr.h
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
#pragma once
#include "dmgr/IDebugMgr.h"
#include "zsp/ast/impl/VisitorBase.h"
#include "zsp/parser/IFactory.h"
#include "zsp/parser/IVal.h"

namespace zsp {
namespace parser {



class TaskEvalExpr : public virtual ast::VisitorBase {
public:
    TaskEvalExpr(IFactory *factory);

    virtual ~TaskEvalExpr();

    IVal *eval(ast::IExpr *expr);

    template <class T> T *evalT(ast::IExpr *expr) {
        return dynamic_cast<T *>(eval(expr));
    }

    virtual void visitExprAggregateLiteral(ast::IExprAggregateLiteral *i) override;

    virtual void visitExprBin(ast::IExprBin *i) override;

    virtual void visitExprBitSlice(ast::IExprBitSlice *i) override;

    virtual void visitExprBool(ast::IExprBool *i) override;

    virtual void visitExprCast(ast::IExprCast *i) override;

    virtual void visitExprCompileHas(ast::IExprCompileHas *i) override;

    virtual void visitExprCond(ast::IExprCond *i) override;

    virtual void visitExprDomainOpenRangeList(ast::IExprDomainOpenRangeList *i) override;

    virtual void visitExprDomainOpenRangeValue(ast::IExprDomainOpenRangeValue *i) override;

    virtual void visitExprId(ast::IExprId *i) override;

    virtual void visitExprIn(ast::IExprIn *i) override;

    virtual void visitExprOpenRangeList(ast::IExprOpenRangeList *i) override;

    virtual void visitExprOpenRangeValue(ast::IExprOpenRangeValue *i) override;

    virtual void visitExprNull(ast::IExprNull *i) override;

    virtual void visitExprSignedNumber(ast::IExprSignedNumber *i) override;

    virtual void visitExprString(ast::IExprString *i) override;

    virtual void visitExprSubscript(ast::IExprSubscript *i) override;

    virtual void visitExprUnary(ast::IExprUnary *i) override;

    virtual void visitExprUnsignedNumber(ast::IExprUnsignedNumber *i) override;

private:
    static dmgr::IDebug                *m_dbg;
    IFactory                           *m_factory;
    IValUP                             m_val;

};

}
}


