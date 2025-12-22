"""This module defines base classes for adapters for lexer pipelines.
"""
from abc import ABC, abstractmethod
from typing import Protocol, Any

from compiler.frontend.lexer.base_lexer import BaseLexer
from compiler.frontend.lexer.pipeline.core.component import PipelineSource
from compiler.frontend.lexer.pipeline.core.token_ import PipelineTokenProto


class ExternalTokenAdapterProto[T_Token](PipelineTokenProto, Protocol):
    """Helper adapter protocol for integration with external libraries' token objects (PLY, for instance).

    This extends the basic :class:`PipelineTokenProto` and adds a read-only property ``adapted_token`` which allows
    fetching the inner adapted token when done with the pipeline.
    """
    @property
    def adapted_token(self) -> T_Token:
        ...


class ExternalLexerAdapter[T_Token, T_Lexer: BaseLexer[Any]](PipelineSource[ExternalTokenAdapterProto[T_Token]], ABC):
    """Base adapter class for integration with external libraries lexer objects (PLY, for instance).

    The generic type ``T_InToken`` represents the class of token the adapted lexer produces, and implementations of
    this adapter are meant to transform these tokens into tokens satisfying :class:`ExternalTokenAdapterProto` on
    the generic type ``T_OutToken`` so that they could be used as sources for the pipeline.

    The reasoning for the double generic type is to allow

    Attributes:
        adapted_lexer:  External lexer which is being adapted.
    """
    def __init__(self, adapted_lexer: T_Lexer) -> None:
        self.adapted_lexer: T_Lexer = adapted_lexer

    def input(self, text: str, reset: bool = True) -> None:
        self.adapted_lexer.input(text, reset=reset)

    @abstractmethod
    def token(self) -> ExternalTokenAdapterProto[T_Token]:
        ...

    @abstractmethod
    def is_terminal_token(self, tok: ExternalTokenAdapterProto[T_Token]) -> bool:
        ...


class ExternalLexerReverseAdapter[T_Token](BaseLexer[T_Token], ABC):
    """Base adapter class for integration with external libraries lexer objects (PLY, for instance).

    The generic type "T_Token" represents the class of token the adapted lexer produces, and implementations of
    this adapter are meant to transform these tokens into tokens satisfying :class:`ExternalTokenAdapterProto` so
    that they could be used as sources for the pipeline.

    Attributes:
        reverse_adapted_lexer:  External lexer which is being adapted.
    """
    def __init__(self, reverse_adapted_lexer: BaseLexer[ExternalTokenAdapterProto[T_Token]]) -> None:
        self.reverse_adapted_lexer = reverse_adapted_lexer

    def input(self, text: str, reset: bool = True) -> None:
        self.reverse_adapted_lexer.input(text, reset=reset)

    def token(self) -> T_Token:
        return self.reverse_adapted_lexer.token().adapted_token

    @abstractmethod
    def is_terminal_token(self, tok: T_Token) -> bool:
        ...

