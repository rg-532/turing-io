import re
from typing import Self

from compiler.utils.string import normal_str_to_raw

__all__ = [
    "LexerError",
    "InvalidCharError",
    "MixedIndentationError",
    "InconsistentIndentationError"
]


class LexerError(ValueError):
    """Base class for all lexer errors. Inherits from :class:`ValueError` as the lexer receives inputs as strings.
    """
    def __eq__(self, other):
        if type(other) is not type(self):   # Strict type equality check.
            return False

        return other.args == self.args


class InvalidCharError(LexerError):
    """A lexer error to raise when the lexer could not tokenize some portion of the text.
    """
    @classmethod
    def from_params(cls, inv_char: str, inv_line: int, inv_col: int) -> Self:
        inv_char = normal_str_to_raw(inv_char)
        message = f"Could not tokenize character '{inv_char}' (line {inv_line} column {inv_col})."

        return cls(message)


class MixedIndentationError(LexerError):
    """A lexer error to raise when the scanned text uses a mixture of characters for indentation.

    For example, the following code:
    ::
        1 some code                 # not indented
        2     indented code         # indented with one tab (\\t) character
        3     more indented code    # indented with four space characters
    Should raise `MixedIndentationError` when line 3 is scanned.
    """
    @classmethod
    def from_params(cls, exp_char: str, exp_line: int, inv_value: str, inv_line: int) -> Self:
        match = re.search(fr'[^{exp_char}]', inv_value)

        assert match, "If error detected, match cannot be None."

        exp_char = normal_str_to_raw(exp_char)
        inv_char = normal_str_to_raw(match.string[match.start()])
        message = (f"Indentation has both '{exp_char}' (line {exp_line}), and '{inv_char}'"
                   f"(line {inv_line}, column {match.start() + 1}).")

        return cls(message)


class InconsistentIndentationError(LexerError):
    """A lexer error to raise when the scanned text has a line with an indentation level which is less
    than the preceding line but does not match any of the previous indentation levels.

    For example, the following code:
    ::
        1 some code                 # not indented
        2     indented code         # indented with four space characters
        3   badly indented code     # indented with two space characters
    Should raise `InconsistentIndentationError` when line 3 is scanned.
    """
    @classmethod
    def from_params(cls, exp_length: int, exp_line: int, got_length: int, got_line: int) -> Self:
        message = (f"Got indentation of {got_length} (line {got_line}), but closest previous level has "
                   f"indentation of {exp_length} (line {exp_line}).")

        return cls(message)
