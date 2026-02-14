# pylint: disable=missing-docstring disable=unused-argument
from collections.abc import Callable
import re
from typing import Any, Optional


class Lexer:
    lineno: int
    lexpos: int

    def input(self, s: str) -> None:
        ...

    def token(self) -> Optional[LexToken]:
        ...

    def skip(self, n: int) -> None:
        ...


class LexToken:
    type: Optional[str]
    value: Any
    lineno: int
    colno: int
    lexpos: int
    lexer: Optional[Lexer]


def lex(
        module: Any = None,
        object: Any = None,
        debug: bool = False,

        optimize: bool = False,
        lextab: str = 'lextab',
        reflags: int = int(re.VERBOSE),
        nowarn: bool =False,
        outputdir: Any = None,
        debuglog: Any = None,
        errorlog: Any = None
) -> Lexer:
    ...


# pylint: disable=invalid-name
def Token[F](r: str) -> Callable[[F], F]:
    ...
