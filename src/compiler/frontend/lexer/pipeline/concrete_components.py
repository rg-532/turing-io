"""This module supplies concrete classes of :class:`PipelineComponent`.
"""

from collections.abc import Iterable, Set, Callable
from typing import Optional, Literal

from compiler.frontend.lexer.errors import MixedIndentationError, InconsistentIndentationError
from compiler.frontend.lexer.pipeline.core import PipelineTokenProto, PipelineSource, PipelineComponent


class ParenthesesBasedFilter[T_PipelineToken: PipelineTokenProto](PipelineComponent[T_PipelineToken]):
    """Filters whitespace type tokens (namely, ``WHITESPACE`` and ``EOL``) whenever they are nested within parentheses.

    More specifically, whenever a token of type ``WHITESPACE`` or ``EOL`` is encountered after an opening parenthesis
    but before its matching closing parenthesis, this token is dumped.

    Example:
        Given a token stream::

            IF '(' EOL
            WHITESPACE IDENTIFIER(0) ',' EOL
            WHITESPACE IDENTIFIER(1) ',' EOL
            WHITESPACE IDENTIFIER(2) EOL
            ')' GOTO IDENTIFIER(3) EOL

        This filter can transform it into something like::

            IF '(' IDENTIFIER(0) ',' IDENTIFIER(1) ',' IDENTIFIER(2) ')' GOTO IDENTIFIER(3) EOL

    Currently, this component recognizes regular parentheses only ('(', ')').

    The set of token types to ignore can be altered by passing either a string representing a token type to filter or
    an iterable of strings representing multiple token types to filter to the optional ``to_filter`` init argument.
    If ``to_filter`` is specified, and parentheses tokens appear in it, they are always ignored.

    Attributes:
        to_filter:      A set of types of tokens to filter in parentheses.
        paren_count:    Counter for parentheses nesting level.
    """
    def __init__(self,
                 source_lexer: PipelineSource[T_PipelineToken],
                 to_filter: Optional[str | Iterable[str]] = None) -> None:
        super().__init__(source_lexer)
        self.to_filter: Set[str] = self._make_filter_set(to_filter)

        # Resets on any new input
        self.paren_count: int = 0

    @staticmethod
    def _make_filter_set(to_filter: Optional[str | Iterable[str]]) -> Set[str]:
        if to_filter is None:
            return {"WHITESPACE", "EOL"}
        elif isinstance(to_filter, str):
            return {to_filter}
        else:
            return set(to_filter)

    def input(self, text: str, reset: bool = True) -> None:
        super().input(text, reset=reset)
        self.paren_count = 0

    def process(self, tok: T_PipelineToken) -> None:
        if tok.type_ == "(":
            self.paren_count += 1
        elif tok.type_ == ")":
            self.paren_count -= 1
        elif self.paren_count > 0 and tok.type_ in self.to_filter:
            return      # Skip token

        self.output_queue.append(tok)


class TypeBasedLookaheadFilter[T_PipelineToken: PipelineTokenProto](PipelineComponent[T_PipelineToken]):
    """Uses one lookahead token to filters tokens of type ``filter_type`` if the lookahead token is of a type
    specified by ``lookahead_types``.

    Example:
        If we wish to filter ``WHITESPACE`` before ``EOL``, '@' and ``_ENDMARKER`` then the filter transforms::

            IF SYMBOL ':' EOL
            WHITESPACE '@' IDENTIFIER(0) EOL
            WHITESPACE  EOL
            WHITESPACE _ENDMARKER

        Into::

            IF SYMBOL ':' EOL
            '@' IDENTIFIER(0) EOL
            EOL
            _ENDMARKER

    Attributes:
        filter_type:        The type of tokens to filter out.
        lookahead_types:    The types for the lookahead tokens causing the filtered type to be filtered.
    """
    def __init__(self,
                 source_lexer: PipelineSource[T_PipelineToken],
                 filter_type: str,
                 lookahead_types: Iterable[Optional[str]]) -> None:
        super().__init__(source_lexer)

        self.filter_type: str = filter_type
        self.lookahead_types: Set[Optional[str]] = set(lookahead_types)

    def process(self, tok: T_PipelineToken) -> None:
        if tok.type_ == self.filter_type:
            next_tok = self.next_input_token()      # lookahead

            if next_tok.type_ not in self.lookahead_types:
                # don't filter case (inverse of filter condition).
                self.output_queue.append(tok)

            # Now we need to know what to do with ``next_tok``
            if next_tok.type_ == self.filter_type:
                self.feedback_queue.append(next_tok)    # May need to be filtered - reprocess it.
            else:
                self.output_queue.append(next_tok)      # Never filtered - send it out.
        else:
            self.output_queue.append(tok)


class TokenMerger[T_PipelineToken: PipelineTokenProto](PipelineComponent[T_PipelineToken]):
    """Merges two subsequent tokens of type ``merge_type`` and outputs them as one.

    By default, the merging strategy is to add the value of the second into the first, unless either value is
    ``_ENDMARKER``, in which case it is replaced (first) or ignored (second). This can be overridden by setting the
    ``merge_strategy`` init argument with a callable that receives two tokens and returns the result token (usually
    the first).

    Example:

        If we wish to merge subsequent ``EOL`` tokens with the default behavior, then the coalescer transforms::

            IF SYMBOL GOTO IDENTIFIER(0) EOL(2)
            EOL(1)
            EOL(1)
            '@' IDENTIFIER(0) EOL(1)
            EOL(1)
            _ENDMARKER

        Into::

            IF SYMBOL GOTO IDENTIFIER(0) EOL(4)
            '@' IDENTIFIER(0) EOL(2)
            _ENDMARKER

    Attributes:
        merge_type:     The type of tokens to be merged.
        merge_strategy: The merging strategy (callable of (token, token) -> token).
    """
    def __init__(self,
                 source_lexer: PipelineSource[T_PipelineToken],
                 merge_type: str,
                 merge_strategy: Optional[Callable[[T_PipelineToken, T_PipelineToken], T_PipelineToken]] = None) -> None:
        super().__init__(source_lexer)
        self.merge_type: str = merge_type

        if merge_strategy is not None:
            self.merge_strategy: Callable[[T_PipelineToken, T_PipelineToken], T_PipelineToken] = merge_strategy
        else:
            self.merge_strategy = self.default_merge_strategy

    @staticmethod
    def default_merge_strategy(tok1: T_PipelineToken, tok2: T_PipelineToken) -> T_PipelineToken:
        """Defines the default merging strategy."""
        if tok1.value is None:
            tok1.value = tok2.value
        elif tok2.value is not None:
            tok1.value += tok2.value

        return tok1

    def process(self, tok: T_PipelineToken) -> None:
        if tok.type_ == self.merge_type:
            next_tok = self.next_input_token()  # lookahead

            if next_tok.type_ == self.merge_type:
                merged_tok = self.merge_strategy(tok, next_tok)
                self.feedback_queue.append(merged_tok)      # May need further processing.
            else:
                self.output_queue.extend([tok, next_tok])   # Both do not need handling.
        else:
            self.output_queue.append(tok)


class EnsureEOLAtEnd[T_PipelineToken: PipelineTokenProto](PipelineComponent[T_PipelineToken]):
    """Simply ensures that there is an ``EOL`` token immediately before the terminating ``_ENDMARKER``, and inserts
    one with value 0 if not.
    """
    def __init__(self, source_lexer: PipelineSource[T_PipelineToken]) -> None:
        super().__init__(source_lexer)
        self.last_token_type: Optional[str] = None   # look-back (opposite of lookahead).

    def input(self, text: str, reset: bool = True) -> None:
        super().input(text, reset=reset)
        self.last_token_type = None

    def process(self, tok: T_PipelineToken) -> None:
        if self.is_terminal_token(tok):
            if self.last_token_type != "EOL":
                added_tok = tok.clone()
                added_tok.type_ = "EOL"
                added_tok.value = 0
                self.output_queue.append(added_tok)
        else:
            self.last_token_type = tok.type_

        self.output_queue.append(tok)


class IndentationGenerator[T_PipelineToken: PipelineTokenProto](PipelineComponent[T_PipelineToken]):
    """Generates a sequence of ``INDENT/DEDENT`` tokens after encountering ``EOL`` and based on the token after it.

    If the processed token is of type ``WHITESPACE``, it is replaced with ``INDENT/DEDENTs`` based on its length.
    Otherwise, the token is kept and if it is of any type other than "EOL" or '@' it is also prefixed by ``DEDENTs``.

    Additionally, an attribute ``is_new_line`` is set on each token encountered, based on whether its ``type_`` is
    ``EOL``, and this is done after processing the token into indentation.


    Because of this way of operation, it is important to filter out instances of ``WHITESPACE`` which precede lines
    that do not declare proper statements (statements starting with the '@' sign, or within a parentheses closed
    sequence).

    For the same reason, it is also important to ensure there is an ``EOL`` token before the terminating
    ``_ENDMARKER``, otherwise the final ``DEDENT`` tokens will not be outputted.

    Please see :class:`ParenthesesBasedFilter`, :class:`TypeBasedLookaheadFilter` and :class:`EnsureEOLAtEnd` on
    how to achieve this.


    This component only allows for one character for indentation, meaning that if two different whitespace characters
    (For instance, '\t' and ' ') appear in some ``WHITESPACE`` which follows an ``EOL``, then this
    component raises a :class:`MixedIndentationError`.

    Additionally, if an inconsistent indentation level (less than the current, but does not match any previous level)
    is encountered, this component raises a :class:`InconsistentIndentationError`.


    Attributes:
        indent_char:        Character used for indentation, determined by the first occurrence of INDENT generation.
        indent_char_line:   Line number where ``indent_char`` was determined for error reporting.
        indent_stack:       Stack of indentation level, which also carries line numbers for error reporting.
        is_new_line:        Boolean flag specifying whether the lexer is positioned at the beginning of a new line.

    Raises:
        MixedIndentationError:
            If text uses a mixture of characters for indentation.
        InconsistentIndentationError:
            If after exiting indented segment the resulting level does not match previous indentation levels.
    """
    def __init__(self, source_lexer: PipelineSource[T_PipelineToken]):
        super().__init__(source_lexer)

        self.indent_char: Optional[str] = None
        self.indent_char_line: Optional[int] = None
        self.indent_stack: list[tuple[int, int]] = [(0, 0)]
        self.is_new_line: bool = True

    def input(self, text: str, reset: bool = True) -> None:
        super().input(text, reset=reset)

        self.indent_char = None
        self.indent_char_line = None
        self.indent_stack = [(0, 0)]
        self.is_new_line = True

    @staticmethod
    def clone_to_indentation(anchor: T_PipelineToken, type_: Literal["INDENT", "DEDENT"]) -> T_PipelineToken:
        """Static helper method which clones ``anchor`` and transforms it into a single INDENT/DEDENT token. The
        ``anchor`` sets the positional attributes of the returned token.

        :param anchor:  Anchor token for positional values.
        :param type_:   Type of token (INDENT/DEDENT).
        :return:        INDENT/DEDENT token.
        """
        indent_tok = anchor.clone()
        indent_tok.type_ = type_
        indent_tok.value = None

        return indent_tok

    def insert_dedents(self, anchor: T_PipelineToken, indent_level: int) -> None:
        """Helper method which pushes ``DEDENT`` tokens with the same position as ``anchor`` into ``output_queue``,
        based on the given ``indent_level`` and current ``indent_stack`` contents.

        Can push nothing into ``output_queue`` if ``indent_level`` is the same as the top of ``indent_stack``.

        Does not perform a check for inconsistent indentation (since it is not always necessary).

        :param indent_level:    Indentation level to process.
        :param anchor:          Anchor token for positional values.
        """
        while indent_level < self.indent_stack[-1][0]:
            self.indent_stack.pop()
            self.output_queue.append(self.clone_to_indentation(anchor, "DEDENT"))

    def handle_whitespace(self, whitespace: T_PipelineToken) -> None:
        """Helper method which transforms a ``WHITESPACE`` token ``whitespace`` into ``INDENT/DEDENT`` tokens, with
        the same position, based on its length (which determines the indentation level).

        This method is responsible for setting ``indent_char`` and ``indent_char_line`` for error checking and
        reporting, and check for various indentation errors.

        :param whitespace:  ``WHITESPACE`` token.

        :raises MixedIndentationError:
            If text uses a mixture of characters for indentation.
        :raises InconsistentIndentationError:
            If after exiting indented segment the resulting level does not match previous indentation levels.
        """
        if self.indent_char is None or self.indent_char_line is None:
            assert self.indent_char is None and self.indent_char_line is None
            self.indent_char = whitespace.value[0]
            self.indent_char_line = whitespace.lineno

        indent_level = len(whitespace.value)

        # Check for mixed indentation:
        if whitespace.value != self.indent_char * indent_level:
            raise MixedIndentationError.from_params(
                self.indent_char, self.indent_char_line, whitespace.value, whitespace.lineno)

        if indent_level > self.indent_stack[-1][0]:     # Need to indent
            self.indent_stack.append((indent_level, whitespace.lineno))
            self.output_queue.append(self.clone_to_indentation(whitespace, "INDENT"))
        else:                                           # Need to dedent
            self.insert_dedents(whitespace, indent_level)

            # Check for inconsistent indentation:
            if indent_level > self.indent_stack[-1][0]:
                raise InconsistentIndentationError.from_params(
                    *self.indent_stack[-1], indent_level, whitespace.lineno)

    def process(self, tok: T_PipelineToken) -> None:
        if self.is_new_line:
            if tok.type_ == "WHITESPACE":
                self.handle_whitespace(tok)
            else:
                if tok.type_ not in ["EOL", '@']:
                    self.insert_dedents(tok, 0)

                self.output_queue.append(tok)
        else:
            self.output_queue.append(tok)

        self.is_new_line = (tok.type_ == "EOL")

