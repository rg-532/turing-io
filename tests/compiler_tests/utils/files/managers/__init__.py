"""This module supplies classes to manage files (read, write, check existence, move, etc.).
"""
from compiler_tests.utils.files.managers.text_manager import TextFileManager
from compiler_tests.utils.files.managers.json_manager import JsonFileManager, T_JsonContent
from compiler_tests.utils.files.managers.golden_manager import GoldenFileManager

__all__ = [
    'TextFileManager',
    'JsonFileManager',
    'T_JsonContent',
    'GoldenFileManager'
]
