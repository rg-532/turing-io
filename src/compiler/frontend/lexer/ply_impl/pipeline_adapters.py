"""This modules implements some pipeline adapters for ``PLY`` implementations.
"""
from copy import copy
from typing import Optional, Any, Self

from ply import lex

from compiler.frontend.lexer.base_lexer import T_Token, BaseLexer
from compiler.frontend.lexer.pipeline import ExternalLexerReverseAdapter
from compiler.frontend.lexer.pipeline.core import ExternalTokenAdapterProto, ExternalLexerAdapter
from compiler.frontend.lexer.ply_impl.ply_lexer import PLYLexerFacade

ENDMARKER_TYPE: str = "_ENDMARKER"
"""Type of a token which signals termination of the stream."""


class PLYLexTokenAdapter(ExternalTokenAdapterProto[Optional[lex.LexToken]]):
    """Adapter implementation for the outputs of a ``PLY`` lexer, which are ``lex.LexToken`` instances or ``None``
    to signal termination.

    This adapter is tied to the basic ``PLY`` lexer instance for the sake of properly updating the adapted token's
    attributes which are not specified under :class:`PipelineTokenProto` but belong to ``lex.LexToken``, such as
    ``lexer`` and ``lexpos``.
    """
    def __init__(self,
                 adapted_token: Optional[lex.LexToken],
                 e_lineno: int, e_colno: int,
                 ply_lexer: lex.Lexer) -> None:
        self._adapted = adapted_token
        self._ply_lexer = ply_lexer
        self._lexpos = ply_lexer.lexpos

        if adapted_token is None:
            self.type_ = ENDMARKER_TYPE
            self.value = None
            self.lineno = e_lineno
            self.colno = e_colno
        else:
            self.type_ = adapted_token.type
            self.value = adapted_token.value
            self.lineno = adapted_token.lineno
            self.colno = adapted_token.colno

        self.e_lineno = e_lineno
        self.e_colno = e_colno

    def clone(self) -> Self:
        return PLYLexTokenAdapter(copy(self.adapted_token), self.e_lineno, self.e_colno, self._ply_lexer)

    @property
    def adapted_token(self) -> Optional[lex.LexToken]:
        if self.type_ == ENDMARKER_TYPE:
            return None

        if self._adapted is None:
            self._adapted = lex.LexToken()
            self._adapted.lexpos = self._lexpos
            self._adapted.lexer = self._ply_lexer

        self._adapted.type = self.type_
        self._adapted.value = self.value
        self._adapted.lineno = self.lineno
        self._adapted.colno = self.colno

        return self._adapted


class PLYLexerAdapter(ExternalLexerAdapter[Optional[lex.LexToken], PLYLexerFacade]):
    """Adapter implementation for ``PLY`` lexers as classes.
    """
    def __init__(self, adapted_lexer: PLYLexerFacade) -> None:
        super().__init__(adapted_lexer)

    def token(self) -> PLYLexTokenAdapter:
        tok = self.adapted_lexer.token()
        pos_tok = self.adapted_lexer.get_pos_as_token()

        e_lineno = pos_tok.lineno
        e_colno = pos_tok.colno
        adapter_tok = PLYLexTokenAdapter(tok, e_lineno, e_colno, self.adapted_lexer.ply_lexer)

        return adapter_tok

    def is_terminal_token(self, tok: PLYLexTokenAdapter) -> bool:
        return tok.type_ == ENDMARKER_TYPE

    def new_token(
            self, type_: Optional[str] = None, value: Any = None,
            lineno: Optional[int] = None, colno: Optional[int] = None,
            e_lineno: Optional[int] = None, e_colno: Optional[int] = None
    ) -> PLYLexTokenAdapter:
        if type_ == ENDMARKER_TYPE:
            in_tok = None
        else:
            in_tok = lex.LexToken()

            in_tok.type = type_
            in_tok.value = value
            in_tok.lineno = lineno
            in_tok.colno = colno

            in_tok.lexpos = self.adapted_lexer.ply_lexer.lexpos
            in_tok.lexer = self.adapted_lexer.ply_lexer

        return PLYLexTokenAdapter(in_tok, e_lineno, e_colno, self.adapted_lexer.ply_lexer)


class PLYLexerReverseAdapter(ExternalLexerReverseAdapter[Optional[lex.LexToken]]):
    def __init__(self, reverse_adapted_lexer: BaseLexer[PLYLexTokenAdapter]) -> None:
        super().__init__(reverse_adapted_lexer)

    def is_terminal_token(self, tok: Optional[lex.LexToken]) -> bool:
        return tok is None