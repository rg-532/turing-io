"""This module provides functions to parse testing metadata read from a JSON file.

The parsing result, obtained by :func:``
"""
import logging
import os
from functools import cache, cached_property
from glob import glob
from typing import List

from compiler_tests.utils.files import JsonFileManager

_logger = logging.getLogger(__name__)

TEST_DATADIR: str = "tests/data/"
_reader = JsonFileManager(TEST_DATADIR).set_perms("r")


@cache
class LazyMetadata(object):
    """This class is used to lazily-load testing metadata from a JSON file.

    This class heavily relies on caching to implement its lazy loading:
        - Class instances are stored in a cache, so any file loaded with this class, and any data read/computed from
          said file, are all only loaded once, even if multiple instances are created.
        - All contents of the metadata file, and anything that is computed from contents of the file, are decorated
          with ``cached_property``, so they too are only loaded/computed once and only if necessary.

    This class is mainly used to support ``pytest``'s test/fixture metadata-based parametrization, since fixtures
    cannot be referenced in any of ``pytest``'s parametrization techniques. The lazy loading is inspired from
    ``pytest``'s way of managing fixtures, computing their values only when needed by some test.
    """
    def __init__(self, fpath: str | bytes | os.PathLike) -> None:
        self._fpath = fpath
        _logger.debug(f"Made {repr(self)}")

    @property
    def fpath(self):
        """Path to this file from constructor call.
        """
        return self._fpath

    @cached_property
    def _metadata(self):
        metadata = _reader.read(self._fpath)

        _logger.debug(f"Read metadata for {repr(self)}")
        return metadata

    def _get_dir(self, dir_key: str) -> str:
        return os.path.join(TEST_DATADIR, self._metadata[dir_key])

    @cached_property
    def input_dir(self) -> str:
        """Directory path for input files.
        """
        return self._get_dir("input_dir")

    @cached_property
    def output_dir(self) -> str:
        """Directory path for expected output files.
        """
        return self._get_dir("output_dir")

    @cached_property
    def golden_dir(self) -> str:
        """Directory path for golden files.
        """
        return self._get_dir("golden_dir")

    @cached_property
    def input_paths(self) -> List[str | bytes | os.PathLike]:
        """Sequence of all input paths specified by globbing patterns under "input_patterns" in the metadata file.
        """
        paths = []
        seen = set()

        for pattern in self._metadata["input_patterns"]:
            for path in glob(pattern, root_dir=self.input_dir, recursive=True):
                if path not in seen:
                    paths.append(path)
                    seen.add(path)

        _logger.debug(f"Computed input_paths for {repr(self)}")
        return paths

    def __repr__(self):
        return f"{self.__class__.__qualname__}(fpath={self._fpath})"


if __name__ == "__main__":
    logging.basicConfig(level="DEBUG")
    lm = LazyMetadata("lexer/lexer.json")
    LazyMetadata("lexer/lexer.json")
    LazyMetadata("lexer/lexer.json")

    for path_path in LazyMetadata("lexer/lexer.json").input_paths:
        print(f"\t{path_path}")




