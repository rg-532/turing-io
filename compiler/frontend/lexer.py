from typing import Optional

from ply import lex


# noinspection PyPep8Naming
class Lexer:
    """Lexical analyzer for ``TMLang``.
    """
    reserved = {
        'machine' : 'MACHINE',
        # 'tape' : 'TAPE',
        # 'register' : 'REGISTER',
        'write' : 'WRITE',
        'left' : 'LEFT',
        'right' : 'RIGHT',
        'until' : 'UNTIL',
        'not' : 'NOT',
        'if' : 'IF',
        'do' : 'DO',
        'goto' : 'GOTO',
    }
    """Keywords of the language"""

    literals = [ '(', ')', '<', '>', '@', ':', ',' ]
    """Literals of the language"""

    tokens = [
        'IDENTIFIER',
        'INTEGER',
        'SYMBOL',
        'EOL',
        'INDENT',
        'DEDENT',
    ] + list(reserved.values())
    """Lexer token types (+ keywords)"""

    t_ignore_COMMENT = r'\#.*'
    """Ignore (single line) comments (formatted as ``#...``)"""


    def __init__(self):
        self.ply_lexer: Optional[lex.Lexer] = None


    @lex.Token(r'[a-zA-Z_][a-zA-Z_0-9]*')
    def t_IDENTIFIER(self, tok: lex.LexToken):
        tok.type = Lexer.reserved.get(tok.value, 'IDENTIFIER')
        return tok

    @lex.Token(r'[0-9]+')
    def t_INTEGER(self, tok: lex.LexToken):
        #noinspection PyTypeChecker
        tok.value = int(tok.value, base=10)
        return tok

    @lex.Token(r'\'[^\n]*\'')       # empty match = 'blank' symbol.
    def t_SYMBOL(self, tok: lex.LexToken):
        tok.value = tok.value[1:-1]
        return tok

    @lex.Token(r'(\r?\n)+')
    def t_EOL(self, tok: lex.LexToken):
        tok.lexer.lineno += tok.value.count('\n')
        return tok



    def build(self, **kwargs):
        self.ply_lexer = lex.lex(module=self, **kwargs)

    def tokenize(self, text: str, **kwargs):
        if not self.ply_lexer:
            self.build(**kwargs)

        self.ply_lexer.input(text)

        for tok in self.ply_lexer:
            yield tok
