"""This module supplies classes to manage file_managers (read, write, check existence, move, etc.).
"""
from typing import Union, TypeAlias
from collections.abc import Mapping, Sequence
from pathlib import Path
import json

from tests.compiler_tests.utils.file_managers.base_manager import FileManager

_T_Content: TypeAlias = Union[Mapping[str, "_T_Content"], Sequence["_T_Content"], str, int, float, bool, None]


class JsonFileManager(FileManager[Mapping[str, _T_Content]]):
    """Implements functionality to read/write JSON file_managers into/from python mappings which are compatible with ``json``
    (meaning they can only contain mappings, sequences and basic JSON field types).
    """
    def _read_core(self, fullpath: Path) -> Mapping[str, _T_Content]:
        with fullpath.open("r") as f:
            data = json.load(f)

        return data

    def _write_core(self, fullpath: Path, data: Mapping[str, _T_Content]) -> None:
        with fullpath.open("w") as f:
            json.dump(data, f)


