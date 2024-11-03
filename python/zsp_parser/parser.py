import zsp_parser.ast as zsp_ast
import zsp_parser.core as zspp
from typing import Dict, List, Tuple, TextIO

class ParseException(Exception):
    pass

class Parser(object):

    def __init__(self):
        self.ast_f = zsp_ast.Factory.inst()
        self.parser_f = zspp.Factory.inst()
        self._root = None
        self._filenames : Dict[int,str] = {}
        self._files : List[zsp_ast.GlobalScope] = []
        pass

    def parse(self, files : List[str]) -> bool:
        marker_l = self.parser_f.mkMarkerCollector()
        builder = self.parser_f.mkAstBuilder(marker_l)

        if len(self._files) == 0:
            stdlib = self.ast_f.mkGlobalScope(-1)
            self.parser_f.loadStandardLibrary(builder, stdlib)
            self._files.append(stdlib)

        for f in files:
            id = len(self._files)
            self._filenames[id] = f
            with open(f, "r") as fp:
                ast = self.ast_f.mkGlobalScope(id)
                builder.build(ast, fp)
            
            if marker_l.hasSeverity(zspp.MarkerSeverityE.Error):
                err = self._mkErrorMessage(marker_l)
                raise ParseException(err)

            self._files.append(ast)

        return True

    def parse_s(self, files : List[Tuple[str, TextIO]]) -> bool:
        marker_l = self.parser_f.mkMarkerCollector()
        builder = self.parser_f.mkAstBuilder(marker_l)

        if len(self._files) == 0:
            stdlib = self.ast_f.mkGlobalScope(-1)
            self.parser_f.loadStandardLibrary(builder, stdlib)
            self._files.append(stdlib)

        for f,sin in files:
            id = len(self._files)
            self._filenames[id] = f
            ast = self.ast_f.mkGlobalScope(id)
            builder.build(ast, sin)
            
            if marker_l.hasSeverity(zspp.MarkerSeverityE.Error):
                err = self._mkErrorMessage(marker_l)
                raise ParseException(err)

            self._files.append(ast)

        return True

    def _mkErrorMessage(self, marker_l):
        pass

    @property
    def root(self) -> zsp_ast.RootSymbolScope:
        return self._root
