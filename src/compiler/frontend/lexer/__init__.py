"""This package allows to build and type-annotate basic lexers.
"""
from compiler.frontend.lexer.build_lexer import build_lexer
from compiler.frontend.lexer.base_lexer import BaseLexer
from compiler.frontend.lexer.errors import LexerInputError

__all__ = [
    'build_lexer',
    'BaseLexer',
    'LexerInputError'
]
