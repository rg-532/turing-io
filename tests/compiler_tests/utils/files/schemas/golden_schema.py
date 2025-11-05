import os
from dataclasses import dataclass, field
from typing import Optional

from compiler_tests.utils.files.schemas.base_schema import EmptySchema


@dataclass(repr=False, kw_only=True)
class GoldenFileOriginSchema(EmptySchema):
    """Schema which captures details about the origin of generation of a JSON file.
    Used by :class:`GoldenFileSchema`.

    :ivar creator:      Name of the module/class/description which created the file.
    :ivar reason:       Short string describing reason of the file's creation.
    :ivar timestamp:    Date and time of execution which created this schema (non-overridable in ``__init__``).
    """
    creator: Optional[str] = None
    reason: Optional[str] = None
    timestamp: str = os.environ.get("EXEC_TIME", "0000-00-00 00:00:00.00000")


@dataclass(repr=False, kw_only=True)
class GoldenFileSchema(EmptySchema):
    """Most basic schema for JSON files which are generated automatically.

    :ivar file_type:        Type of the file (token list from lexer tests, AST nodes from parser tests etc.).
    :ivar origin:           Description of how/why this schema was generated (see :class:`GoldenFileOriginSchema`).
    :ivar project_version:  Version of the project (non-overridable in ``__init__``).
    :ivar schema_version:   Version of the schema (defaults to schema version ``base`` from ``pyproject.toml``).

    :ivar metadata:         Optional additional metadata on the file (defaults to empty nested schema).
    :ivar data:             Dictionary containing stored data (also defaults to empty nested schema).
    """
    file_type: str = "GENERIC_GOLDEN_FILE"
    origin: GoldenFileOriginSchema = field(default_factory=GoldenFileOriginSchema)
    project_version: str = os.environ.get("PROJECT_VERSION", "0.0.0")
    schema_version: str = os.environ.get("GOLDEN_FILE_SCHEMA_VERSION", "0")

    metadata: EmptySchema = field(default_factory=EmptySchema)
    data: EmptySchema = field(default_factory=EmptySchema)
