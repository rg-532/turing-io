"""This module holds the definition of the ``LexerToken`` class, which is constructible from ``ply.lex.Token``
instances and adds on top of them some utilities useful for testing.
"""
from __future__ import annotations

from typing import ClassVar, List, Optional, Any
from dataclasses import dataclass
import copy

from ply.lex import LexToken as PLYToken

from compiler.frontend.lexer.ply_impl.ply_lexer import PLYLexerFacade
from compiler.utils.string import SafeMapping, normal_str_to_raw


@dataclass
class LexerToken(object):
    """Transforms a ``ply.lex.LexToken`` instance into an instance of this class for testing.

    This class properly defines class attributes, and allows for equality / equivalency checking.

    :ivar typ:    Type of the token (``None`` if unset).
    :ivar value:    Value of the token if applicable, or ``None`` if not or unset.
    :ivar lineno:   Line number of the token's beginning in the original file (``None`` if not set).
    :ivar colno:    Column number of the token's beginning in the original file (``None`` if unset).
    """
    _VALUELESS_TOKEN_TYPES: ClassVar[List[str]] = (
            list(PLYLexerFacade.keywords.values())      # When stable, change this to literal list maybe?
            + list(PLYLexerFacade.literals)             # Same as above
            + ["INDENT", "DEDENT", "WHITESPACE"]
    )
    """Defines the types of objects which have no value"""

    typ: Optional[str]
    value: Any
    lineno: Optional[int]
    colno: Optional[int]

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, LexerToken):
            if isinstance(other, PLYToken):
               other: LexerToken = LexerToken.from_tok(other)
            else:
                return NotImplemented

        return (self.typ == other.typ and
                self.value == other.value and
                self.lineno == other.lineno and
                self.colno == other.colno)

    def to_formatted_string(self, template: str = "{typ} ({value})  pos=({lineno}, {colno})") -> str:
        """Returns a string representing the token with format ``template``.

        Uses ``SafeMapping``, so if the provided ``template`` has some field that does not exist in ``LexerToken``,
        this field is left as is (with surrounding braces).

        :param template:    Template to format the resulting string by.
        :return:            Formatted string of this token.
        """
        value = self.value

        if value is not None:
            value = normal_str_to_raw(self.value)

        return template.format_map(SafeMapping(
            type=self.typ,
            value=value,
            lineno=self.lineno,
            colno=self.colno
        ))


    @staticmethod
    def from_tok(tok: PLYToken | LexerToken) -> LexerToken:
        """Static method to initialize a ``LexerToken`` from a ``ply.lex.LexToken`` instance or another ``LexerToken``
        instance.

        If a ``ply.lex.LexToken`` instance is provided, this method accesses its attributes in a safe manner, setting
        any non-existing attribute to ``None``.

        Additionally, filters the returned token's ``value`` attribute based on ``tok.type`` - If the type of the
        received token a keyword, literal, WHITESPACE, INDENT or DEDENT, the value is set to ``None``. This is done
        to avoid comparisons of values that do not matter.

        If a ``LexerToken`` instance is provided instead, this method simply makes a deep copy of the token.

        :param tok: Token to initialize a ``LexerToken`` instance from.
        :return:    A new ``LexerToken`` instance.
        """
        if isinstance(tok, LexerToken):
            return copy.deepcopy(tok)

        type_: str = tok.type

        value = getattr(tok, "value", None)

        if type_ and type_ in LexerToken._VALUELESS_TOKEN_TYPES:
            value = None

        lineno: int = getattr(tok, "lineno", None)
        colno: int = getattr(tok, "colno", None)

        return LexerToken(type_, value, lineno, colno)

    @staticmethod
    def is_equiv(tok1: PLYToken | LexerToken, tok2: PLYToken | LexerToken, compare_pos: bool = True) -> bool:
        """Static method to check equivalency between ``tok1`` and ``tok2``.

        Note that the additional parameter ``compare_pos`` allows this comparison method to ignore positional
        attributes (``lineno`` and ``colno``).

        :param tok1:        First token of comparison.
        :param tok2:        Second token of comparison.
        :param compare_pos: Boolean flag specifying whether to also compare attributes.
        :return:            True if the objects are equivalent, and False otherwise.
        """
        if isinstance(tok1, PLYToken):
            tok1 = LexerToken.from_tok(tok1)

        if not compare_pos:
            tok2 = LexerToken.from_tok(tok2)
            tok2.lineno = tok1.lineno
            tok2.colno = tok1.colno
        elif isinstance(tok2, PLYToken):
            tok2 = LexerToken.from_tok(tok2)

        return tok1 == tok2

