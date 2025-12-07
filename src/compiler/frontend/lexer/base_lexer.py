"""Defines the base class of all lexers in the project.
"""
from abc import ABC, abstractmethod
from typing import Generator, Generic, TypeVar


T_Token = TypeVar("T_Token")

class BaseLexer(ABC, Generic[T_Token]):
    """Defines the baseline interface of a lexer in the program, as well as some useful utilities.

    The interface specified here is inspired by the ply.lex.Lexer() interrace.
    """
    @abstractmethod
    def input(self, text: str) -> None:
        """Sets input of the lexer.

        :param text:    Input.
        """
        ...

    @abstractmethod
    def token(self) -> T_Token:
        """Returns the next token, or ``None`` if there is no next token.

        :return:    Next token.
        """
        ...

    @abstractmethod
    def is_terminal_token(self, tok: T_Token) -> bool:
        """Determines whether the received token is considered a terminating token, which signals the end of the
        stream.

        :param tok: Token to test.
        :return:    ``True`` if the token is terminating, ``False`` otherwise.
        """
        ...

    def tokenize(self, text: str) -> Generator[T_Token, None, None]:
        """Unifies the ``input()`` and ``token()`` methods into one call that generates and yields the sequence of
        tokens found in `text`.

        :param text:    String to tokenize.
        :return:        Tokens generator of tokens.
        """
        self.input(text)
        tok = self.token()

        while not self.is_terminal_token(tok):
            yield tok
            tok = self.token()

