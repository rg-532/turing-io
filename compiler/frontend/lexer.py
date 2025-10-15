from typing import Optional, List, Tuple, Generator
import re

from ply import lex

class MixedIndentationError(ValueError):
    # TODO - When column support is added, change this to support it as well.
    def __init__(
            self,
            exp_char: str,  exp_line: int, exp_pos: int,
            inv_value: str, inv_line: int, inv_pos: int
    ) -> None:
        match = re.search(fr'[^{exp_char}]', inv_value)

        assert match, "If error detected, match cannot be None."

        message = (f"Indentation has both {repr(exp_char)} (line {exp_line}, pos {exp_pos}), and "
                   f"{repr(match.string)} (line {inv_line}, pos {inv_pos + match.start()}).")
        super().__init__(message)


class InconsistentIndentationError(ValueError):
    # TODO - When column support is added, change this to support it as well.
    def __init__(
            self,
            exp_length: int, exp_line: int, exp_pos: int,
            got_length: int, got_line: int, got_pos: int
    ) -> None:
        message = (f"Got indentation of {got_length} (line {got_line}, pos {got_pos}), but closest previous "
                   f"level has indentation of {exp_length} (line {exp_line}, pos {exp_pos}).")
        super().__init__(message)



# noinspection PyPep8Naming
class Lexer:
    """Lexical analyzer for ``TMLang``. Utilizes `PLY` library's lexer.
    """

    ### PLY Lexer specification ###
    reserved = {
        # 'machine' : 'MACHINE',
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
        'WS',       # Whitespace
        'INDENT',
        'DEDENT',
    ] + list(reserved.values())
    """Lexer token types"""

    t_ignore_COMMENT = r'\#.*'
    """Ignore (single line) comments (formatted as ``#...``)"""

    @lex.Token(r'[a-zA-Z_][a-zA-Z_0-9]*')
    def t_IDENTIFIER(self, tok: lex.LexToken):
        tok.type = Lexer.reserved.get(tok.value, 'IDENTIFIER')
        return tok

    #noinspection PyTypeChecker
    @lex.Token(r'[0-9]+')
    def t_INTEGER(self, tok: lex.LexToken):
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

    @lex.Token(r'[ \t]+')
    def t_WS(self, tok: lex.LexToken):
        return tok


    ### Added implementations ###
    def __init__(self) -> None:
        # Internal lexer:
        self._ply_lexer: Optional[lex.Lexer] = None

        # Specifies whether whitespace should be translated to indentation
        self._new_line: bool = True
        self._in_sequence: bool = False

        # Tracks the character of indentation (Detected from first indentation)
        self._indent_char: Optional[str] = None
        self._indent_char_first_line: Optional[int] = None
        self._indent_char_first_pos: Optional[int] = None

        # Stack for managing indentation tokens (INDENT/DEDENT).
        # Holds entries of the form (indent length, line, pos) TODO - rename here when column support is added.
        self._indent_stack: List[Tuple[int, int, int]] = [(0, 0, 0)]     # Dummy value


    def _ws_to_indent(self, tok: lex.LexToken) -> Generator[lex.LexToken, None, None]:
        """Receives a whitespace token (WS) which should be transformed into either nothing, a single
        INDENT token or a sequence of DEDENT token, based on its length and previous indentations' lengths.

        Can raise :class:`MixedIndentationError` when a mixture of characters are being used to indentation.

        For instance, if a file has a single tab (\t) character at the start of line 1 and eight spaces at
        the start of line 8, `MixedIndentationError` will be raised when scanning the beginning of line 8.

        :param tok: WS type token to process.
        :type tok:  lex.LexToken
        :return: Nothing (Generator).

        :raises MixedIndentationError:  If file uses a mixture of characters for indentation.
        """
        if not self._indent_char:
            self._indent_char = tok.value[0]
            self._indent_char_first_line = tok.lineno
            self._indent_char_first_pos = tok.lexpos

        indent_length = len(tok.value)

        # Check if indentation was written with a mixture of characters
        if tok.value != self._indent_char * indent_length:
            raise MixedIndentationError(
                self._indent_char, self._indent_char_first_line, self._indent_char_first_pos,
                tok.value, tok.lineno, tok.lexpos
            )

        # TODO - When column support is added, change this to support it as well.
        # Check whether this is a DEDENT / INDENT / omission case
        if indent_length < self._indent_stack[-1][0]:
            # Yield DEDENT until a previous level is reached
            while indent_length < self._indent_stack[-1][0]:
                self._indent_stack.pop()

                dedent = lex.LexToken()
                dedent.type = "DEDENT"
                dedent.lineno = tok.lineno
                dedent.lexpos = tok.lexpos

                yield dedent

            # Check if indentation is inconsistent
            if indent_length > self._indent_stack[-1][0]:
                raise InconsistentIndentationError(*self._indent_stack[-1], indent_length, tok.lineno, tok.lexpos)
        elif indent_length > self._indent_stack[-1][0]:
            self._indent_stack.append((indent_length, tok.lineno, tok.lexpos))

            indent = lex.LexToken()
            indent.type = "INDENT"
            indent.lineno = tok.lineno
            indent.lexpos = tok.lexpos

            yield indent

    def tokenize(self, text: str) -> Generator[lex.LexToken, None, None]:
        if not self._ply_lexer:
            self._ply_lexer = lex.lex(module=self)

        # indent_stack: List[int] = [0]

        self._ply_lexer.input(text)
        tok = self._ply_lexer.next()

        while tok:
            if tok.type == "WHITESPACE":
                # Check next token.
                next_tok = self._ply_lexer.next()

                if not next_tok:
                    # End reached - terminate immediately
                    return
                elif next_tok.type not in ["EOF", "@"]:
                    # Cases where whitespace is not ignored
                    if self._new_line and not self._in_sequence:
                        # Whitespace transforms into INDENT / DEDENT(s):
                        for indent_tok in self._ws_to_indent(tok):
                            yield indent_tok
                    else:
                        # Whitespace remains as is, but clear its value
                        tok.value = None
                        yield tok

                tok = next_tok

            self._new_line = (tok.type == "EOL")

            if tok.type in "<(":
                assert not self._in_sequence        # TODO - this and the next asserts are invalid
                self._in_sequence = True
            elif tok.type in ">)":
                assert self._in_sequence
                self._in_sequence = False

            yield tok
            tok = self._ply_lexer.next()





