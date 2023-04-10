'''
Created on Mar 24, 2021

@author: mballance
'''
from unittest.case import TestCase
from _io import StringIO

class TestLoad(TestCase):
    
    def test_smoke(self):
        from zsp_parser import core as zspp_core

        factory = zspp_core.Factory.inst()
        
        marker_l = factory.mkMarkerCollector()
        
        parser = factory.mkAstBuilder(marker_l)
        ast_f = factory.getAstFactory()

        glbl = ast_f.mkGlobalScope(0)
        

        input = StringIO(
            """
            /**
             * Just a comment
             */
             component pss_top {
             }
            
            // Before
            // Before
             
             /**
              * Free-standing comment
              */
              
              
              
              component pss_top2 {
              }
             
              // SLC1
              // SLC2
              // SLC3
              //
              component pss_top3 {
              }
            """)
        print("--> parse")
        parser.build(glbl, input)
        print("<-- parse")

        self.assertFalse(marker_l.hasSeverity(zspp_core.MarkerSeverityE.Error))        

#        pssparser.core.doit(2)