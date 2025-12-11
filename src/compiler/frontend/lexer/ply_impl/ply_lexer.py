"""This module defines a ``PLY`` lexer class.
"""
from typing import Optional

from ply import lex

from compiler.frontend.lexer.base_lexer import BaseLexer
from compiler.frontend.lexer.errors import InvalidCharError


# noinspection PyPep8Naming
class PLYLexerFacade(BaseLexer[Optional[lex.LexToken]]):
    """Allows for a single point of integration with PLY's Lexer object.
        - Defines a specification of a PLY Lexer.
        - Implements column tracking, as was done in the docs.
        - Filters WHITESPACE token output - Only returns WHITESPACE if started a new line.

    :ivar ply_lexer:    Internal PLY Lexer object being managed.
    :type ply_lexer:    lex.Lexer
    """

    ### PLY Lexer specification ###
    keywords = {kw: kw.upper() for kw in [
        # IMPLEMENTED #
        'machine',                                                      # Declarations
        'write', 'left', 'right', 'until', 'accept', 'reject', 'halt',  # Basic Operations
        'not', 'if', 'do', 'goto',                                      # Basic Control

        # FUTURE #
        'tape', 'register',                                             # Future Declarations
        'on', 'is', 'and', 'or',                                        # Multi-tape Support
        'else', 'elif', 'while', 'for', 'break', 'continue', 'then',    # Advanced Control
    ]}
    """Keywords of the language"""

    literals = [ '(', ')', '=', '@', ':', ',' ]
    """Literals of the language"""

    tokens = [
        # Basic tokens:
        'IDENTIFIER',
        'INTEGER',
        'SYMBOL',
        'EOL',
        'WHITESPACE',
        # Tokens that are generated in the pipeline (for ``PLY`` parsers):
        'INDENT',
        'DEDENT',
    ] + list(keywords.values())
    """Lexer token types"""

    t_ignore_COMMENT = r"\#.*"
    """Ignore (single line) comments (formatted as ``#...``)"""

    @lex.Token(r"[a-zA-Z_][a-zA-Z_0-9]*")           # type: ignore[misc]
    def t_IDENTIFIER(self, tok: lex.LexToken) -> lex.LexToken:
        tok.type = PLYLexerFacade.keywords.get(tok.value, 'IDENTIFIER')
        return tok

    #noinspection PyTypeChecker
    @lex.Token(r"[0-9]+")                           # type: ignore[misc]
    def t_INTEGER(self, tok: lex.LexToken) -> lex.LexToken:
        tok.value = int(tok.value, base=10)
        return tok

    @lex.Token(r"'(?a:[^\x00-\x1F\x7F\s\"']*)'")    # type: ignore[misc]
    def t_SYMBOL(self, tok: lex.LexToken) -> lex.LexToken:
        tok.value = tok.value[1:-1]
        return tok

    @lex.Token(r"(\r?\n)+")                         # type: ignore[misc]
    def t_EOL(self, tok: lex.LexToken) -> lex.LexToken:
        tok.value = tok.value.count('\n')
        tok.lexer.lineno += tok.value
        return tok

    @lex.Token(r"[ \t]+")                           # type: ignore[misc]
    def t_WHITESPACE(self, tok: lex.LexToken) -> Optional[lex.LexToken]:
        if self._new_line:
            return tok

        return None

    #noinspection PyMethodMayBeStatic
    def t_error(self, tok: lex.LexToken) -> lex.LexToken:
        tok.type = "_ERR_INVALID_CHAR"
        tok.value = tok.value[0]

        tok.lexer.skip(1)       # Just so that PLY doesn't raise an exception itself...

        return tok


    def __init__(self) -> None:
        self.ply_lexer: Optional[lex.Lexer] = None

        # Column tracking + whitespace filtration:
        self._new_line: Optional[bool] = None
        self._line_lexpos: Optional[int] = None

    def _set_token_colno(self, tok: lex.LexToken) -> None:
        """Sets the token `tok` column number in attribute `tok.colno`.

        :param tok: Token to set attribute `tok.colno` for.
        """
        if self._new_line:
            self._line_lexpos = tok.lexpos

        tok.colno = tok.lexpos - self._line_lexpos + 1

    def input(self, text: str, reset: bool = True) -> None:
        if reset or not self.ply_lexer:
            self.ply_lexer = lex.lex(module=self)

        self._new_line = True
        self._line_lexpos = self.ply_lexer.lexpos

        self.ply_lexer.input(text)

    def token(self) -> Optional[lex.LexToken]:
        if self.ply_lexer is None:
            return None     # Assume empty input

        tok: lex.LexToken = self.ply_lexer.token()

        if tok is not None:
            self._set_token_colno(tok)
            self._new_line = (tok.type == "EOL")

            if tok.type == "_ERR_INVALID_CHAR":
                raise InvalidCharError.from_params(tok.value, tok.lineno, tok.colno)

        return tok

    def is_terminal_token(self, tok: Optional[lex.LexToken]) -> bool:
        return tok is None

    def get_pos_as_token(self) -> lex.LexToken:  # TODO - check for input call here
        tok = lex.LexToken()

        tok.type = tok.value = None

        if not self.ply_lexer:
            tok.lineno = tok.lexpos = 0     # Assume empty input
        else:
            tok.lineno = self.ply_lexer.lineno
            tok.lexpos = self.ply_lexer.lexpos

        self._set_token_colno(tok)
        tok.lexer = self.ply_lexer

        return tok

