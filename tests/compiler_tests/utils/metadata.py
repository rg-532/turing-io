"""This module provides functions to parse testing metadata read from a JSON file.

The parsing result, obtained by :func:``
"""
import logging
import os
from functools import cache, cached_property
from typing import Literal, cast

from compiler_tests.utils.files import JsonFileManager, T_JsonContent
from compiler.utils.globbing import multi_glob

_logger = logging.getLogger(__name__)

TEST_DATADIR: str = os.path.join(os.environ.get("PROJECT_ROOT", "."), "tests/data/")
"""Absolute path to testing data directory."""
_reader = JsonFileManager(TEST_DATADIR).set_perms("r")


class _LazyMetadata(object):
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
    def __init__(self, fpath: str | os.PathLike[str]) -> None:
        self._fpath: str | os.PathLike[str] = fpath
        _logger.debug(f"Made {repr(self)}")

    @property
    def fpath(self) -> str | os.PathLike[str]:
        """Path to this file from constructor call.
        """
        return self._fpath

    # This is here because of the lack of schema for read metadata files.
    def _validate_metadata(self, metadata: T_JsonContent) -> None:
        expected_keys = ["input_dir", "output_dir", "input_patterns"]
        missing_keys = [key for key in expected_keys if key not in metadata]

        if missing_keys:
            raise ValueError(f"Keys {missing_keys} are missing from {self._fpath}")

        if not isinstance(metadata["input_dir"], str):
            raise ValueError(f"`input_dir` needs to be `str` (Got `{type(metadata["input_dir"])}`).")

        if not isinstance(metadata["output_dir"], str):
            raise ValueError(f"`output_dir` needs to be `str` (Got `{type(metadata["output_dir"])}`).")

        if not isinstance(metadata["input_patterns"], list):
            raise ValueError(f"`input_patterns` needs to be `list[str]`) (Got `{type(metadata["input_patterns"])}`).")

        for idx, pat in enumerate(metadata["input_patterns"]):
            if not isinstance(pat, str):
                raise ValueError(f"`input_patterns[{idx}]` str) (Got `{type(pat)}`).")

    @cached_property
    def _metadata(self) -> T_JsonContent:
        metadata = _reader.read(self._fpath)
        self._validate_metadata(metadata)

        _logger.debug(f"Read metadata for {repr(self)}")
        return metadata

    def _get_dir(self, dir_key: Literal["input_dir", "output_dir"]) -> str:
        return os.path.join(TEST_DATADIR, str(self._metadata[dir_key]))

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
    def input_paths(self) -> list[str]:
        """Sequence of all input paths specified by globbing patterns under "input_patterns" in the metadata file.
        """
        # This is here because of the lack of schema for read metadata files.
        patterns = cast(list[str], self._metadata["input_patterns"])
        assert isinstance(patterns, list)
        assert all(isinstance(pat, str) for pat in patterns)
        
        paths = multi_glob(
            *patterns,
            root_dir=self.input_dir,
            recursive=True)
        # This is because `globbing.py` implementation is weird.
        assert isinstance(paths, list)

        _logger.debug(f"Computed input_paths for {repr(self)}")
        return paths

    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}(fpath={str(self._fpath)})"


@cache
def lazy_metadata(fpath: str | os.PathLike[str]) -> _LazyMetadata:
    return _LazyMetadata(fpath)

