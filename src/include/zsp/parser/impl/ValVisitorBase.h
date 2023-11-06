/**
 * ValVisitorBase.h
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
#include "zsp/parser/IValVisitor.h"
#include "zsp/parser/IValInt.h"
#include "zsp/parser/IValStr.h"
#include "zsp/parser/IValStruct.h"
#include "zsp/parser/IValArray.h"

namespace zsp {
namespace parser {



class ValVisitorBase : public virtual IValVisitor {
public:

    virtual ~ValVisitorBase() { }

    virtual void visitVal(IVal *v) override { }
    
    virtual void visitValInt(IValInt *v) override {
        visitVal(v);
    }

    virtual void visitValStr(IValStr *v) override {
        visitVal(v);
    }

    virtual void visitValStruct(IValStruct *v) override {

    }

    virtual void visitValArray(IValArray *v) override {

    }

};

} /* namespace parser */
} /* namespace zsp */


