"""This module defines a file manager for basic JSON files (which do not contain objects).
"""
from typing import TypeAlias
from collections.abc import Mapping, Sequence
from pathlib import Path
import json

from compiler_tests.utils.files.managers.base_manager import FileManager

_T_Content: TypeAlias = Mapping[str, "_T_Content"] | Sequence["_T_Content"] | str | int | float | bool | None


class JsonFileManager(FileManager[Mapping[str, _T_Content]]):
    """Implements functionality to read/write JSON files into/from python mappings which are compatible with ``json``
    (meaning they can only contain mappings, sequences and basic JSON field types).

    Keyword arguments to ``read()`` and ``write()`` are passed to the ``json`` library.
    """
    def _read_core(self, fullpath: Path, **kwargs) -> Mapping[str, _T_Content]:
        with fullpath.open("r") as f:
            data = json.load(f)

        return data

    def _write_core(self, fullpath: Path, data: Mapping[str, _T_Content], **kwargs) -> None:
        defaults = dict(indent = 2)
        defaults.update(kwargs)

        with fullpath.open("w") as f:
            json.dump(data, f, **defaults)

