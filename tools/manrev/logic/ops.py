import logging
import os
from collections.abc import Sequence
from pathlib import Path
from typing import List, AnyStr, OrderedDict

from compiler_tests.utils.files import GoldenFileManager

from manrev.logic.viewers import get_tempfile, get_viewer
from utils.globbing import multi_glob

_logger = logging.getLogger(__name__)


def find_files(
        root_dir: str = os.getcwd(),
        suffixes: Sequence[str] = ('.tm.tok',)
) -> OrderedDict[AnyStr, List[AnyStr]]:
    """Scans for files to review starting from ``root_dir`` and filters for those ending with any ``suffixes``.
    The files needing review are those under an inner directory named ``.golden`` (can be nested in more directories).

    :param root_dir:    Root directory (absolute or relative) to start search from.
    :param suffixes:    A sequence of suffixes which are allowed for the returned files.
    :return:            A dictionary of entries ``(pattern,list_of_matches)``.
    """
    if len(suffixes) == 0:
        patterns = ["**/.golden/**"]
    else:
        patterns = [f"**/.golden/**{suf}" for suf in suffixes]

    return multi_glob(
        *patterns, root_dir=root_dir, recursive=True, include_hidden=True, flatten=False,
        filter_callback=lambda m: os.path.isfile(os.path.join(root_dir, m)))


def view_file(file: str, manager: GoldenFileManager) -> bool:
    """Views contents of a generated file based on its specified ``file_type`` (see :class:`GoldenFileSchema` for
    more details).

    Supported schemas: TokenFileSchema

    :param file:    Path to the file (absolute or relative to ``cwd``).
    :param manager: Golden file manager to use.
    :return:        Flag specifying whether file was viewed (or some error occurred).
    """
    schema, cause = manager.safe_read(file)
    mod_time = os.path.getmtime(file)

    if schema is None:
        _logger.error(f"{type(cause).__qualname__}: {cause}")
        return False

    if schema.schema_version != type(schema).schema_version:
        _logger.warning(f"File may be outdated (Read schema_version='{schema.schema_version}'; "
                        f"Current: {type(schema).__qualname__}.schema_version='{type(schema).schema_version}')")

    viewer = get_viewer(schema)

    with get_tempfile(fpath=file, mode="w+t") as tmp:
        _logger.debug(f"Viewing contents of '{file}' ({type(schema).__qualname__})...")
        viewer.view(tmp)

    if mod_time != os.path.getmtime(file):
        _logger.warning(f"File '{file}' has been modified!")

    return True


def accept_file(file: str, manager: GoldenFileManager) -> None:
    """Accepts a generated file by moving it outside `.golden` directories its nested in.

    :param file:    Path to file to accept.
    :param manager: Golden file manager to use.
    """
    segments = list(Path(file).parts)
    g_dir_count = segments.count(".golden")

    if g_dir_count == 0:
        _logger.error(f"File {file} is not inside a '.golden' directory - Ignored.")
        return
    elif g_dir_count > 2:
        _logger.warning(f"File {file} is nested inside multiple '.golden' directories ({g_dir_count}).")

    new_path = Path(*[seg for seg in segments if seg != ".golden"])

    try:
        manager.move(file, new_path)
    except FileNotFoundError as exc:
        _logger.error(f"{type(exc).__qualname__}: {exc}")

