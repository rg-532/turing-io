"""This module supplies extended dataclasses (schemas) which are used to load/store contents of JSON or JSON-like
files. These schemas are generally meant to serve as inputs/outputs of file managers.
"""
from compiler_tests.utils.files.schemas.base_schema import EmptySchema
from compiler_tests.utils.files.schemas.golden_schema import GoldenFileSchema, GoldenFileOriginSchema
from compiler_tests.utils.files.schemas.token_schema import TokenFileSchema, TokenFileDataSchema
