"""This module defines the base class for all file managers.
"""
from typing import Generic, Literal, Self, TypeVar, TypeAlias, Union
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
import os

T_Path: TypeAlias = Union[str, os.PathLike]
_T = TypeVar("_T")


@dataclass
class _Permissions(object):
    read: bool = True
    write: bool = True


class FileManager(ABC, Generic[_T]):
    """Abstract class defining an interface to manage file_managers in the directory at ``dirpath``. If given as a relative
    path (without leading '/' or 'D:\'), the path is relative from the root of execution. This class is generic in
    terms of the type of data being read from and written to file_managers.

    :ivar dirpath:      Path to directory of file_managers from running root.
    :ivar perms:        Permissions on file_managers in the directory (read + write by default).
    """
    def __init__(self, dirpath: T_Path):
        self.dirpath: Path = Path(dirpath)
        self.perms = _Permissions

    @abstractmethod
    def _read_core(self, fullpath: Path) -> _T:
        """Abstract method, defining how to read a file with path ``filepath``.

        When overriding this method, note that:
            - The path was already joined with ``self.dirpath``, and stored into a :class:``pathlib.Path`` instance.
            - Permissions were already checked.
            - File existence was already checked.

        :param fullpath:    :class:``pathlib.Path`` instance of the path to the file to read.
        :return:            Contents of the file
        """
        ...

    @abstractmethod
    def _write_core(self, fullpath: Path, data: _T) -> None:
        """Abstract method, defining how to write generic ``data`` into file with path ``filepath``.

        When overriding this method, note that:
            - The path was already joined with ``self.dirpath``, and stored into a :class:``pathlib.Path`` instance.
            - Permissions were already checked.
            - Compliance with ``allow_overwrite`` was already checked.

        :param fullpath:    :class:``pathlib.Path`` instance of the path to the file to write.
        :param data:        Generic data to write into the file.
        """
        ...

    def set_perms(self, perms: Literal["r", "w", "rw", "wr"]) -> Self:
        """Sets permissions of the FileManager, and returns self (for chaining calls).

        :param perms:   Permissions to set (as string containing characters 'r' and 'w').
        :return:        Self (call chaining).
        """
        self.perms.read = "r" in perms
        self.perms.write = "w" in perms
        return self

    def read(self, relpath: T_Path) -> _T:
        """Reads and returns the contents of a file with path ``relpath`` relative to this directory.

        :param relpath:     Relative path to file under this directory.
        :return:            Contents of the file.

        :raises FileNotFoundError:  If the file does not exist under this directory.
        :raises PermissionError:    If the manager does not have read permissions.
        """
        if not self.perms.read:
            raise PermissionError(f"Directory '{self.dirpath}' does not have read permission.")

        filepath = self.dirpath / relpath

        if not filepath.exists():
            raise FileNotFoundError(f"No file '{relpath}' under directory '{self.dirpath}'")

        return self._read_core(filepath)


    def write(self, relpath: T_Path, data: _T, allow_overwrite: bool = False) -> None:
        """Writes ``data`` into a file with path ``relpath`` relative to this directory.

        By default, guards against overwriting existing file_managers (set ``allow_overwrite = True`` to allow overwriting).

        :param relpath:         Relative path to file under this directory.
        :param data:            Data to write.
        :param allow_overwrite: Boolean flag indicating whether overwriting existing file is allowed.

        :raises FileExistsError:    If the file exists and ``allow_overwrite = False``.
        :raises PermissionError:    If the manager does not have write permission.
        """
        if not self.perms.write:
            raise PermissionError(f"Directory {self.dirpath} does not have write permission.")

        filepath = self.dirpath / relpath

        if not allow_overwrite and filepath.exists():
            raise FileExistsError(f"File '{relpath}' exists under '{self.dirpath}'")

        filepath.parent.mkdir(parents=True, exist_ok=True)

        return self._write_core(filepath, data)

    def exists(self, relpath: T_Path) -> bool:
        """Checks if a file with path ``filepath`` exists relative to this directory.

        :param relpath:    Relative path to a file under this directory.
        :return:            Boolean representing the result of the check.
        """
        relpath = self.dirpath / relpath
        return relpath.exists()

    def move(self, curr_relpath: T_Path, new_relpath: T_Path) -> None:
        """Moves a file/subdirectory with path ``current_path`` under this directory to ``new_path`` under this
        directory.

        :param curr_relpath:    Path of existing file/subdirectory under this directory.
        :param new_relpath:        New path of the file/subdirectory under this directory.

        :raises FileNotFoundError:  If the file/subdirectory at ``current_path`` under this directory does not exist.
        """
        curr_relpath = self.dirpath / curr_relpath
        new_relpath = self.dirpath / new_relpath
        new_relpath.parent.mkdir(parents=True, exist_ok=True)
        curr_relpath.rename(new_relpath)


