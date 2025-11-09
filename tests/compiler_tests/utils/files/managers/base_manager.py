"""This module defines the base class for all file managers.
"""
import logging
from typing import Literal, Self, Optional
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
import os


@dataclass
class _Permissions(object):
    read: bool = True
    write: bool = True


class FileManager[T](ABC):
    """Abstract class defining an interface to manage files in the directory at ``dirpath``. If given as a relative
    path (without leading '/' or 'D:\'), the path is relative from the root of execution. This class is generic in
    terms of the type of data being read from and written to files.

    :ivar dirpath:      Path to directory of files from running root.
    :ivar perms:        Permissions on files in the directory (read + write by default).
    """
    def __init__(self, dirpath: Optional[str | os.PathLike] = None):
        if dirpath is None:
            dirpath = os.environ.get("PROJECT_ROOT", ".")

        self.dirpath: Path = Path(dirpath)
        self.perms = _Permissions()

    @abstractmethod
    def _read_core(self, fullpath: Path, **kwargs) -> T:
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
    def _write_core(self, fullpath: Path, data: T, **kwargs) -> None:
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
    
    def _get_path(self, filepath: str | os.PathLike) -> Path:
        if os.path.isabs(filepath):
            return Path(filepath)

        return self.dirpath / filepath
    
    def read(self, filepath: str | os.PathLike, **kwargs) -> T:
        """Reads and returns the contents of a file with path ``relpath`` relative to this directory.

        :param filepath:    Relative path to file under this directory.
        :return:            Contents of the file.

        :raises FileNotFoundError:  If the file does not exist under this directory.
        :raises PermissionError:    If the manager does not have read permissions.
        """
        if not self.perms.read:
            raise PermissionError(f"Directory '{self.dirpath}' does not have read permission.")

        filepath = self._get_path(filepath)

        if not filepath.exists():
            raise FileNotFoundError(f"No such file '{filepath}'")

        return self._read_core(filepath, **kwargs)


    def write(self, filepath: str | os.PathLike, data: T, allow_overwrite: bool = False, **kwargs) -> None:
        """Writes ``data`` into a file with path ``relpath`` relative to this directory.

        By default, guards against overwriting existing files (set ``allow_overwrite = True`` to allow overwriting).

        :param filepath:         Relative path to file under this directory.
        :param data:            Data to write.
        :param allow_overwrite: Boolean flag indicating whether overwriting existing file is allowed.

        :raises FileExistsError:    If the file exists and ``allow_overwrite = False``.
        :raises PermissionError:    If the manager does not have write permission.
        """
        if not self.perms.write:
            raise PermissionError(f"Directory {self.dirpath} does not have write permission.")

        filepath = self._get_path(filepath)

        if not allow_overwrite and filepath.exists():
            raise FileExistsError(f"File '{filepath}' already exists")

        filepath.parent.mkdir(parents=True, exist_ok=True)

        self._write_core(filepath, data, **kwargs)
        logging.info(f"Wrote file at {self.dirpath / filepath} (type = {type(data).__qualname__}).")

    def exists(self, relpath: str | os.PathLike) -> bool:
        """Checks if a file with path ``filepath`` exists relative to this directory.

        :param relpath:    Relative path to a file under this directory.
        :return:            Boolean representing the result of the check.
        """
        relpath = self.dirpath / relpath
        return relpath.exists()

    def move(self, curr_relpath: str | os.PathLike, new_relpath: str | os.PathLike) -> None:
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


