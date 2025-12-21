"""This module defines a file manager for basic text files.
"""
from pathlib import Path
from typing import Any

from compiler_tests.utils.files.managers.base_manager import FileManager


class TextFileManager(FileManager[str]):
    """Implements simple functionality to read/write text files (into/from strings).

    Keyword arguments to ``read()`` and ``write()`` are ignored.
    """
    def _read_core(self, fullpath: Path, **kwargs: Any) -> str:
        return fullpath.read_text()

    def _write_core(self, fullpath: Path, data: str, **kwargs: Any) -> None:
        fullpath.write_text(data)
