from typing import Optional

from ply import lex

from compiler.frontend.lexer.base_lexer import BaseLexer
from compiler.frontend.lexer.ply_impl import PLYLexerFacade, PLYLexerAdapter, PLYLexerReverseAdapter
from compiler.frontend.lexer.pipeline import ParenthesesBasedFilter, TypeBasedLookaheadFilter, TokenMerger, \
    EnsureEOLAtEnd, IndentationGenerator


def build_lexer() -> BaseLexer[Optional[lex.LexToken]]:
    """Builder method for the lexer.

    :return:    Lexer.
    """
    lexer = PLYLexerFacade()
    lexer = PLYLexerAdapter(lexer)
    lexer = ParenthesesBasedFilter(lexer)
    lexer = TypeBasedLookaheadFilter(lexer, "WHITESPACE", ["EOL", '@', None])
    lexer = TokenMerger(lexer, "EOL")
    lexer = EnsureEOLAtEnd(lexer)
    lexer = IndentationGenerator(lexer)
    lexer = PLYLexerReverseAdapter(lexer)

    return lexer

