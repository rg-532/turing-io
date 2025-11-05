import os
from dataclasses import dataclass, field
from typing import Sequence

from compiler_tests.utils.files.schemas.golden_schema import GoldenFileSchema
from compiler_tests.utils.files.schemas.base_schema import EmptySchema
from compiler_tests.utils.objects.tokens import LexerToken


@dataclass(repr=False, kw_only=True)
class TokenFileDataSchema(EmptySchema):
    """Schema which captures the data of a tokens file.
    Used by :class:`TokenFileSchema`.

    :ivar tokens:   Sequence of tokens (objects) in the file.
    """
    tokens: Sequence[LexerToken] = field(default_factory=list)


@dataclass(repr=False, kw_only=True)
class TokenFileSchema(GoldenFileSchema):
    """Extends the basic schema to define automatically-generated files containing Lexer outputs (Tokens).

    Overrides ``file_type`` to be "LEXER_TOKENS", the schema version to be specific to this schema and the type
    of data to be the specific type ``TokenFileDataSchema``.
    """
    file_type: str = "LEXER_TOKENS"
    schema_version: str = (GoldenFileSchema.schema_version + "." +
                           os.environ.get("TOKEN_FILE_SCHEMA_VERSION", "0"))
    data: TokenFileDataSchema = field(default_factory=TokenFileDataSchema)
