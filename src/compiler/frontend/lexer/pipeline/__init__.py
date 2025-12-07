"""This package defines a pipeline for processing basic implementations of lexer, transforming their basic token
stream into something that is easier to parse.
"""
from compiler.frontend.lexer.pipeline.core import (
    PipelineTokenProto, PipelineComponent, ExternalTokenAdapterProto, ExternalLexerAdapter,
    ExternalLexerReverseAdapter)
from compiler.frontend.lexer.pipeline.concrete_components import (
    ParenthesesBasedFilter, TypeBasedLookaheadFilter, TokenMerger, EnsureEOLAtEnd, IndentationGenerator)
