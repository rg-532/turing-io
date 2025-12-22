"""This package defines core modules for lexer pipelines as abstract base classes.
"""
from compiler.frontend.lexer.pipeline.core.token_ import PipelineTokenProto
from compiler.frontend.lexer.pipeline.core.component import PipelineSource, PipelineComponent
from compiler.frontend.lexer.pipeline.core.adapters import (
    ExternalTokenAdapterProto, ExternalLexerAdapter, ExternalLexerReverseAdapter)

__all__ = [
    'PipelineTokenProto',
    'PipelineSource',
    'PipelineComponent',
    'ExternalTokenAdapterProto',
    'ExternalLexerAdapter',
    'ExternalLexerReverseAdapter'
]
