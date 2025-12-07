"""This module defines a protocol which serves as a basis for any token processable in the pipeline.
"""
from typing import Optional, Any, Protocol, Self


class PipelineTokenProto(Protocol):
    """Defines a basis of attributes any token passing through the pipeline should have.
    """
    type_: Optional[str]
    value: Any
    lineno: Optional[int]
    colno: Optional[int]
    e_lineno: Optional[int]
    e_colno: Optional[int]

    def clone(self) -> Self:
        ...

