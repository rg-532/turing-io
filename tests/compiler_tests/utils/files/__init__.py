"""Defines the :class:``FileManager`` base class which encapsulates file operations, and derivatives of this class
for handling different types of files.
"""

from compiler_tests.utils.files.managers import TextFileManager, JsonFileManager, T_JsonContent, GoldenFileManager
from compiler_tests.utils.files.schemas import EmptySchema, GoldenFileOriginSchema, GoldenFileSchema, \
    TokenFileDataSchema, TokenFileSchema
from compiler_tests.utils.files.errors import ClassNotFoundError

__all__ = [
    'TextFileManager',
    'JsonFileManager',
    'T_JsonContent',
    'GoldenFileManager',
    'EmptySchema',
    'GoldenFileOriginSchema',
    'GoldenFileSchema',
    'TokenFileDataSchema',
    'TokenFileSchema',
    'ClassNotFoundError'
]
