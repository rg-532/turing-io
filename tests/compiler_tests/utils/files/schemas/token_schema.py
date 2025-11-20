import os
from dataclasses import dataclass, field
from typing import Sequence, Optional

from compiler.frontend.lexer.errors import LexerError
from compiler_tests.utils.files.schemas.golden_schema import GoldenFileSchema
from compiler_tests.utils.files.schemas.base_schema import EmptySchema
from compiler_tests.utils.objects.tokens import LexerToken


@dataclass(repr=False, kw_only=True)
class TokenFileDataSchema(EmptySchema):
    """Schema which captures the data of a tokens file.
    Used by :class:`TokenFileSchema`.

    :ivar tokens:   Sequence of tokens (objects) in the file.
    :ivar exit_exc: Exception thrown by Lexer on exit (``None`` if no exception thrown).
    """
    tokens: Sequence[LexerToken] = field(default_factory=list)
    exit_exc: Optional[LexerError] = None


@dataclass(repr=False, kw_only=True)
class TokenFileSchema(GoldenFileSchema):
    """Extends the basic schema to define automatically-generated files containing Lexer outputs (Tokens).

    Overrides ``file_type`` to be "TokenFileSchema", the schema version to be specific to this schema and the type
    of data to be the specific type ``TokenFileDataSchema``.
    """
    file_type: str = "TokenFileSchema"
    schema_version: str = (GoldenFileSchema.schema_version + "." +
                           os.environ.get("TOKEN_FILE_SCHEMA_VERSION", "0"))
    data: TokenFileDataSchema = field(default_factory=TokenFileDataSchema)
