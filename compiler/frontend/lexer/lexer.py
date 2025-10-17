from typing import Optional, List, Tuple, Generator, Any

from ply import lex

from compiler.frontend.lexer.errors import MixedIndentationError, InconsistentIndentationError
from compiler.frontend.lexer._ply_lexer import _PLYLexerFacade


# noinspection PyPep8Naming
class TMLexer:
    """Lexical analyzer for ``TMLang``. Utilizes `PLY` library's lexer.

    TODO:
        - Fix doc.
        - Add whitespace filter for when it is irrelevant potentially.
        - Add support for illegal characters via ``t_error``.
    """
    def __init__(self) -> None:
        self._lexer_facade: _PLYLexerFacade = _PLYLexerFacade()


    def _init_indentation_context(self) -> None:
        """Initializes parameters for managing indentation - when and how to transform WS into INDENT/DEDENT
        """
        self._paren_count: int = 0                      # If greater than 0, no need to transform.
        self._indent_char: Optional[str] = None         # For mixed indentation. Set on first indentation detected.
        self._indent_char_line: Optional[int] = None    # For mixed indentatio reporting.
                                                        # Holds line in which `_indent_char` was set.

        # Stack for holding indentatio levels and their lines.
        self._indent_stack: List[Tuple[int, int]] = [(0, 0)]     # (0, 0) = Dummy value


    def _ws_to_indent(self, tok: lex.LexToken) -> Generator[lex.LexToken, None, None]:
        """Receives a whitespace token (WS) which should be dumped, transformed into a single INDENT token or
        transformed into a sequence of DEDENT token, based on its length and previous indentations' lengths.

        Can raise :class: MixedIndentationError` or :class:`InconsistentIndentationError` (See these classes'
        docs for more info).

        :param tok: WS type token to process.
        :type tok:  lex.LexToken
        :return:    An iterator of ``INDENT/DEDENT`` tokens (can be empty).
        :rtype:     Iterator[lex.LexToken]

        :raise MixedIndentationError:
            If text uses a mixture of characters for indentation.
        :raise InconsistentIndentationError:
            If after exiting indented segment the resulting level does not match previous indentation levels.
        """
        if not self._indent_char:       # Set indentation character for the rest of the process.
            self._indent_char = tok.value[0]
            self._indent_char_line = tok.lineno

        indent_length = len(tok.value)

        # Check if text has mixed indentation
        if tok.value != self._indent_char * indent_length:
            raise MixedIndentationError(self._indent_char, self._indent_char_line, tok.value, tok.lineno)

        # Determine if this is a DEDENT / INDENT / omission case
        if indent_length > self._indent_stack[-1][0]:
            self._indent_stack.append((indent_length, tok.lineno))
            yield self.copy_token(tok, "INDENT")

        elif indent_length < self._indent_stack[-1][0]:
            # Yield DEDENT until a previous level is reached
            while indent_length < self._indent_stack[-1][0]:
                self._indent_stack.pop()
                yield self.copy_token(tok, "DEDENT")

            # Check if text has inconsistent indentation
            if indent_length > self._indent_stack[-1][0]:
                raise InconsistentIndentationError(*self._indent_stack[-1], indent_length, tok.lineno)

            self._indent_stack[-1] = (indent_length, tok.lineno)    # Override line value


    def _final_indent_tokens(self) -> Generator[lex.LexToken, None, None]:
        # TODO - doc this and clean up the token generation in `tokenize`.
        lineno, colno = self._lexer_facade.get_current_position()

        temp = lex.LexToken()
        temp.type = None
        temp.value = None
        temp.lineno = lineno
        temp.colno = colno

        while self._indent_stack[-1][0] > 0:
            self._indent_stack.pop()
            yield self.copy_token(temp, "DEDENT")


    @staticmethod
    def copy_token(tok: lex.LexToken, new_type: Optional[str] = None) -> lex.LexToken:
        """Makes a copy of token `tok`, and updates its type to be `tok_type`. Does not copy inner attribute lexpos.

        :param tok:         Token to copy.
        :param new_type:    Type of the returned token.
        :return:            A copy of `tok` with type `tok_type`.
        """
        new_tok = lex.LexToken()
        new_tok.type = new_type if new_type else tok.type
        new_tok.value = tok.value
        new_tok.lineno = tok.lineno
        new_tok.colno = tok.colno

        return new_tok


    def tokenize(self, text: str) -> Generator[lex.LexToken, None, None]:
        self._init_indentation_context()
        self._lexer_facade.input(text)

        tok = self._lexer_facade.token()

        while tok:
            next_tok = self._lexer_facade.token()   # Lookahead of 1.

            if tok.type == "WS":
                if next_tok and next_tok.type not in ["EOF", "@"] \
                        and tok.colno == 1 and self._paren_count == 0:   # Transform into INDENT / DEDENT tokens
                    for indent_tok in self._ws_to_indent(tok):
                        yield indent_tok
            else:
                if tok.type in "<(":
                    self._paren_count += 1
                elif tok.type in ">)":
                    self._paren_count -= 1

                yield tok

            tok = next_tok

        for term_tok in self._final_indent_tokens():
            yield term_tok


# TODO - delete this.
if __name__ == "__main__":
    with open("../../test/data/tmlang/inc_scoped.tm") as f:
        read_text = f.read()

    lexer = TMLexer()

    for read_tok in lexer.tokenize(read_text):
        print(f"Token {repr(read_tok.type)} {repr(read_tok.value)} ({read_tok.lineno} {read_tok.colno})")

