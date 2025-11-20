from typing import Optional, List, Tuple, Generator

from ply import lex

from compiler.frontend.lexer.errors import MixedIndentationError, InconsistentIndentationError
from compiler.frontend.lexer.ply_lexer import PLYLexerFacade


class TMLexer:
    """Lexer for ``.tm`` files.

    Wraps a ``PLY`` Lexer, and transforms WHITESPACE into INDENT/DEDENT tokens in the process.

    Also, responsible for raising errors when indentation is ambiguous (See `errors.py` for more details).
    """
    def __init__(self) -> None:
        self._ply_lexer: PLYLexerFacade = PLYLexerFacade()


    def _init_indentation_context(self) -> None:
        """Initializes parameters for managing indentation - when and how to transform WHITESPACE into INDENT/DEDENT
        """
        self._paren_count: int = 0                      # If greater than 0, no need to transform.
        self._indent_char: Optional[str] = None         # For mixed indentation. Set on first indentation detected.
        self._indent_char_line: Optional[int] = None    # For mixed indentation reporting.
                                                        # Holds line in which `_indent_char` was set.

        # Stack for holding indentation levels and their lines.
        self._indent_stack: List[Tuple[int, int]] = [(0, 0)]     # (0, 0) = Dummy value


    def _whitespace_to_indentation_tokens(self, tok: lex.LexToken) -> Generator[lex.LexToken, None, None]:
        """Receives a WHITESPACE token which should be dumped, transformed into a single INDENT token or
        transformed into a sequence of DEDENT token, based on its length and previous indentations' lengths.

        Can raise :class: MixedIndentationError` or :class:`InconsistentIndentationError` (See these classes'
        docs for more info).

        :param tok: WHITESPACE type token to process.
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
            raise MixedIndentationError.from_params(self._indent_char, self._indent_char_line, tok.value, tok.lineno)

        # Determine if this is a DEDENT / INDENT case
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
                raise InconsistentIndentationError.from_params(*self._indent_stack[-1], indent_length, tok.lineno)

            self._indent_stack[-1] = (indent_length, tok.lineno)    # Override line value


    def _generate_final_indentation_tokens(self) -> Generator[lex.LexToken, None, None]:
        """Generates final DEDENT tokens based on stack contents (If the stack has entries generated in the
        tokenization process, it means that there are some INDENT tokens without matching DEDENT tokens, so
        we generate these DEDENT tokens here).

        :return: Iterator of DEDENT tokens, with their position set to the end of the file.
        """
        lineno, colno = self._ply_lexer.get_current_position()

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
        """Makes a copy of token `tok`, and updates its type to be `tok_type`.
        Does not copy inner attribute ``lexpos``.

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
        """Unifies the ``input()`` and ``token()`` methods of the original API into one call that generates
        the sequence of tokens found in `text`, with WHITESPACE transformation (into INDENT/DEDENT).

        :param text:    String to tokenize.
        :type text:     str
        :return:        Iterator (Generator) of tokens.
        :rtype:         Generator[lex.LexToken, None, None]
        """
        self._init_indentation_context()
        self._ply_lexer.input(text)

        tok = self._ply_lexer.token()

        while tok:
            next_tok = self._ply_lexer.token()   # Lookahead of 1.

            if tok.type == "WHITESPACE":
                if next_tok and next_tok.type not in ["EOF", "@"] and self._paren_count == 0:
                    # Transform into INDENT / DEDENT tokens
                    for indent_tok in self._whitespace_to_indentation_tokens(tok):
                        yield indent_tok
            else:
                if tok.type in "<(":
                    self._paren_count += 1
                elif tok.type in ">)":
                    self._paren_count -= 1

                yield tok

            tok = next_tok

        for dedent_tok in self._generate_final_indentation_tokens():
            yield dedent_tok


