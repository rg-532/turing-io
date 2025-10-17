import re


def unescape_chars(s: str):
    """Replaces the usual escaped characters in `string` with their raw versions for printing.

    :param s:   String that potentially has escape characters.
    :type s:    str
    :return:    String with raw versions of escaped characters.
    :rtype:     str
    """
    fixed_s = s.replace('\t', r'\t')
    fixed_s = fixed_s.replace('\r', r'\r')
    fixed_s = fixed_s.replace('\n', r'\n')

    return fixed_s


class InvalidCharError(ValueError):
    """A lexer error to raise when the lexer could not tokenize some portion of the text.
    """
    def __init__(self, inv_char: str, inv_line: int, inv_col: int) -> None:
        inv_char = unescape_chars(inv_char)
        super().__init__(f"Could not tokenize character {inv_char} (line {inv_line} column {inv_col}).")


class MixedIndentationError(ValueError):
    """A lexer error to raise when the scanned text uses a mixture of characters for indentation.

    For example, the following code:
    ::
        1 some code                 # not indented
        2     indented code         # indented with one tab (\\t) character
        3     more indented code    # indented with four space characters
    Should raise `MixedIndentationError` when line 3 is scanned.
    """
    def __init__(self, exp_char: str,  exp_line: int, inv_value: str, inv_line: int) -> None:
        match = re.search(fr'[^{exp_char}]', inv_value)

        assert match, "If error detected, match cannot be None."

        exp_char = unescape_chars(exp_char)
        inv_char = unescape_chars(match.string)
        message = (f"Indentation has both '{exp_char}' (line {exp_line}), and {inv_char}"
                   f"(line {inv_line}, column {match.start()}).")

        super().__init__(message)


class InconsistentIndentationError(ValueError):
    """A lexer error to raise when the scanned text has a line with an indentation level which is less
    than the preceding line but does not match any of the previous indentation levels.

    For example, the following code:
    ::
        1 some code                 # not indented
        2     indented code         # indented with four space characters
        3   badly indented code     # indented with two space characters
    Should raise `InconsistentIndentationError` when line 3 is scanned.
    """
    def __init__(self, exp_length: int, exp_line: int, got_length: int, got_line: int) -> None:
        message = (f"Got indentation of {got_length} (line {got_line}), but closest previous level has "
                   f"indentation of {exp_length} (line {exp_line}).")
        super().__init__(message)
