"""Defines the :class:``FileManager`` base class which encapsulates file operations, and derivatives of this class
for handling different types of file_managers.
"""
from tests.compiler_tests.utils.file_managers.text_manager import TextFileManager
from tests.compiler_tests.utils.file_managers.json_manager import JsonFileManager
from tests.compiler_tests.utils.file_managers.golden_manager import GoldenFileManager, GoldenFileSchema

