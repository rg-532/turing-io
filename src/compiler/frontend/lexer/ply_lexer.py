from typing import Optional, Tuple

from ply import lex

from compiler.frontend.lexer.errors import InvalidCharError


# noinspection PyPep8Naming
class PLYLexerFacade:
    """Allows for a single point of integration with PLY's Lexer object.
        - Defines a specification of a PLY Lexer.
        - Implements column tracking, as was done in the docs.
        - Filters WHITESPACE token output - Only returns WHITESPACE if started a new line.

    :ivar ply_lexer:    Internal PLY Lexer object being managed.
    :type ply_lexer:    lex.Lexer
    """

    ### PLY Lexer specification ###
    keywords = {
        'machine' : 'MACHINE',
        # 'tape' : 'TAPE',
        # 'register' : 'REGISTER',
        'write' :   'WRITE',
        'left' :    'LEFT',
        'right' :   'RIGHT',
        'until' :   'UNTIL',
        'not' :     'NOT',
        'if' :      'IF',
        'do' :      'DO',
        'goto' :    'GOTO',
        'accept' :  'ACCEPT',
        'reject' :  'REJECT',
        'halt' :    'HALT',
    }
    """Keywords of the language"""

    literals = [ '(', ')', '<', '>', '@', ':', ',' ]
    """Literals of the language"""

    tokens = [
        'IDENTIFIER',
        'INTEGER',
        'SYMBOL',
        'EOL',
        'WHITESPACE',       # Whitespace
        'INDENT',
        'DEDENT',
    ] + list(keywords.values())
    """Lexer token types"""

    t_ignore_COMMENT = r'\#.*'
    """Ignore (single line) comments (formatted as ``#...``)"""

    @lex.Token(r'[a-zA-Z_][a-zA-Z_0-9]*')
    def t_IDENTIFIER(self, tok: lex.LexToken) -> lex.LexToken:
        tok.type = PLYLexerFacade.keywords.get(tok.value, 'IDENTIFIER')
        return tok

    #noinspection PyTypeChecker
    @lex.Token(r'[0-9]+')
    def t_INTEGER(self, tok: lex.LexToken) -> lex.LexToken:
        tok.value = int(tok.value, base=10)
        return tok

    @lex.Token(r'\'\S*\'')       # empty match = 'blank' symbol.
    def t_SYMBOL(self, tok: lex.LexToken) -> lex.LexToken:
        tok.value = tok.value[1:-1]
        return tok

    @lex.Token(r'(\r?\n)+')
    def t_EOL(self, tok: lex.LexToken) -> lex.LexToken:
        tok.value = tok.value.count('\n')
        tok.lexer.lineno += tok.value
        return tok

    @lex.Token(r'[ \t]+')
    def t_WHITESPACE(self, tok: lex.LexToken) -> Optional[lex.LexToken]:
        if self._new_line:
            return tok

        return None

    #noinspection PyMethodMayBeStatic
    def t_error(self, tok) -> lex.LexToken:
        tok.type = "_ERR_INVALID_CHAR"
        tok.value = tok.value[0]

        tok.lexer.skip(1)       # Just so that PLY doesn't raise an exception itself...

        return tok


    def __init__(self) -> None:
        self.ply_lexer: Optional[lex.Lexer] = None

        self._new_line: Optional[bool] = None
        self._line_lexpos: Optional[int] = None

    def _set_token_colno(self, tok: lex.LexToken) -> None:
        """Sets the token `tok` column number in attribute `tok.colno`.

        :param tok: Token to set attribute `tok.colno` for.
        """
        if self._new_line:
            self._line_lexpos = tok.lexpos

        tok.colno = tok.lexpos - self._line_lexpos + 1

    def get_current_position(self) -> Tuple[int, int]:
        """Returns the internal ``ply_lexer`` positioning (line, column).

        :return: Tuple containing line number and column number.
        """
        lineno: int = self.ply_lexer.lineno
        colno: int = self.ply_lexer.lexpos - self._line_lexpos + 1

        return lineno, colno

    def input(self, text: str) -> None:
        """Wraps ``self.ply_lexer.input(text)``.

        Initializes the internal Lexer object, as well as parameters for column tracking.

        :param text:    Text to scan with the Lexer object.
        """
        if not self.ply_lexer:
            self.ply_lexer = lex.lex(module=self)

        self._new_line: bool = True
        self._line_lexpos = self.ply_lexer.lexpos

        return self.ply_lexer.input(text)

    def token(self) -> Optional[lex.LexToken]:
        """Wraps ``self.ply_lexer.token()`` and adds column tracking.

        Returns the next token, or ``None`` if no next token exists.

        :return:    Next token with its ``colno`` attribute set.
        """
        tok: lex.LexToken = self.ply_lexer.token()

        if tok is not None:
            self._set_token_colno(tok)
            self._new_line = (tok.type == "EOL")

            if tok.type == "_ERR_INVALID_CHAR":
                raise InvalidCharError(tok.value, tok.lineno, tok.colno)

        return tok


