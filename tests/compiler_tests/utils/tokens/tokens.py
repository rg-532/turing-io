"""This module holds the definition of the ``TestToken`` class, which is constructible from ``ply.lex.Token``
instances and adds on top of them some utilities useful for testing.
"""
from __future__ import annotations

from typing import ClassVar, List, Optional, Any, Union
from dataclasses import dataclass
import copy

from ply import lex
from ply.lex import LexToken as PLYToken

from compiler.frontend.lexer.ply_lexer import PLYLexerFacade
from compiler.utils.string import SafeMapping, normal_str_to_raw


@dataclass
class TestToken:
    """Transforms a ``ply.lex.LexToken`` instance into an instance of this class for testing.

    This class properly defines class attributes, and allows for equality / equivalency checking.

    :ivar type_:    Type of the token (``None`` if unset).
    :type type_:    Optional[str]
    :ivar value:    Value of the token if applicable, or ``None`` if not or unset.
    :type value:    Any
    :ivar lineno:   Line number of the token's beginning in the original file (``None`` if not set).
    :type lineno:   Optional[int]
    :ivar colno:    Column number of the token's beginning in the original file (``None`` if unset).
    :type colno:    Optional[int]
    """
    _VALUELESS_TOKEN_TYPES: ClassVar[List[str]] = (
            list(PLYLexerFacade.keywords.values())      # When stable, change this to literal list maybe?
            + list(PLYLexerFacade.literals)             # Same as above
            + ["INDENT", "DEDENT", "WHITESPACE"]
    )
    """Defines the types of tokens which have no value"""

    type_:  Optional[str]
    value:  Any
    lineno: Optional[int]
    colno:  Optional[int]

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, TestToken):
            if isinstance(other, lex.LexToken):
               other: TestToken = TestToken.from_tok(other)
            else:
                return NotImplemented

        return (self.type_ == other.type_ and
                self.value == other.value and
                self.lineno == other.lineno and
                self.colno == other.colno)

    def to_list(self):
        """Returns the attributes of this token in the order: (``type_``, ``value``, ``lineno``, ``colno``).

        Used for dumping into a file.

        :return: List of attributes of this token
        """
        return [self.type_, self.value, self.lineno, self.colno]

    def to_formatted_string(self, template: str = "{type} ({value})  pos=({lineno}, {colno})") -> str:
        """Returns a string representing the token with format ``template``.

        Uses ``SafeMapping``, so if the provided ``template`` has some field that does not exist in ``TestToken``,
        this field is left as is (with surrounding braces).

        :param template:    Template to format the resulting string by.
        :type template:     str
        :return:            Formatted string of this token.
        :rtype:             str
        """
        value = self.value

        if value is not None:
            value = normal_str_to_raw(self.value)

        return template.format_map(SafeMapping(
            type=self.type_,
            value=value,
            lineno=self.lineno,
            colno=self.colno
        ))


    @staticmethod
    def from_tok(tok: Union[PLYToken, TestToken]) -> TestToken:
        """Static method to initialize a ``TestToken`` from a ``ply.lex.LexToken`` instance or another ``TestToken``
        instance.

        If a ``ply.lex.LexToken`` instance is provided, this method accesses its attributes in a safe manner, setting
        any non-existing attribute to ``None``.

        Additionally, filters the returned token's ``value`` attribute based on ``tok.type`` - If the type of the
        received token a keyword, literal, WHITESPACE, INDENT or DEDENT, the value is set to ``None``. This is done
        to avoid comparisons of values that do not matter.

        If a ``TestToken`` instance is provided instead, this method simply makes a deep copy of the token.

        :param tok: Token to initialize a ``TestToken`` instance from.
        :type tok:  ply.lex.LexToken | TestToken
        :return:    A new ``TestToken`` instance.
        :rtype:     TestToken
        """
        if isinstance(tok, TestToken):
            return copy.deepcopy(tok)

        type_: str = tok.type

        value = getattr(tok, "value", None)

        if type_ and type_ in TestToken._VALUELESS_TOKEN_TYPES:
            value = None

        lineno: int = getattr(tok, "lineno", None)
        colno: int = getattr(tok, "colno", None)

        return TestToken(type_, value, lineno, colno)

    @staticmethod
    def is_equiv(tok1: Union[PLYToken, TestToken], tok2: Union[PLYToken, TestToken], compare_pos: bool = True) -> bool:
        """Static method to check equivalency between ``tok1`` and ``tok2``.

        Note that the additional parameter ``compare_pos`` allows this comparison method to ignore positional
        attributes (``lineno`` and ``colno``).

        :param tok1:        First token of comparison.
        :type tok1:         ply.lex.LexToken | TestToken
        :param tok2:        Second token of comparison.
        :type tok2:         ply.lex.LexToken | TestToken
        :param compare_pos: Boolean flag specifying whether to also compare attributes.
        :type compare_pos:  bool

        :return:            True if the tokens are equivalent, and False otherwise.
        :rtype:             bool
        """
        if isinstance(tok1, PLYToken):
            tok1 = TestToken.from_tok(tok1)

        if not compare_pos:
            tok2 = TestToken.from_tok(tok2)
            tok2.lineno = tok1.lineno
            tok2.colno = tok1.colno
        elif isinstance(tok2, PLYToken):
            tok2 = TestToken.from_tok(tok2)

        return tok1 == tok2



import abc

s = "a\\nb"

print(s.encode().decode("unicode-escape"))



