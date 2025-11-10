import logging
import os
from collections import OrderedDict
from collections.abc import Sequence
from glob import glob
from pathlib import Path
from typing import List

from compiler_tests.utils.files import GoldenFileManager

from manrev.logic.viewers import get_tempfile, get_viewer

_logger = logging.getLogger(__name__)


def find_files(
        root_dir: str = os.getcwd(),
        suffixes: Sequence[str] = ('.tm.tok',)
) -> OrderedDict[str, List[str]]:
    """Scans for files to review starting from ``root_dir`` and filters for those ending with any ``suffix``.
    The files needing review are those under an inner directory named ``.golden`` (can be nested in more directories).

    :param root_dir:    Root directory (absolute or relative) to start search from.
    :param suffixes:    A sequence of suffixes which are allowed for the returned files.
    :return:            A dictionary of entries ``(suffix,list_of_matches)``.
    """
    goldens = OrderedDict()
    seen = set()

    for match in glob("**/.golden/**", root_dir=root_dir, recursive=True):
        if match in seen:
            continue

        seen.add(match)

        if os.path.isfile(os.path.join(root_dir, match)):
            for suf in suffixes:
                if match.endswith(suf):
                    goldens.setdefault(suf, [])
                    goldens[suf].append(match)
                    break

    return goldens


def view_file(fpath: str, manager: GoldenFileManager) -> bool:
    """Views contents of a generated file based on its specified ``file_type`` (see :class:`GoldenFileSchema` for
    more details).

    Supported schemas: TokenFileSchema

    :param fpath:   Path to the file (absolute or relative to ``cwd``).
    :param manager: Golden file manager to use.
    :return:        Flag specifying whether file was viewed (or some error occurred).
    """
    schema, cause = manager.safe_read(fpath)

    if schema is None:
        _logger.error(f"{type(cause).__qualname__}: {cause}")
        return False

    if schema.schema_version != type(schema).schema_version:
        _logger.warning(f"File may be outdated (Read schema_version='{schema.schema_version}'; "
                        f"Current: {type(schema).__qualname__}.schema_version='{type(schema).schema_version}')")

    viewer = get_viewer(schema)

    with get_tempfile(fpath=fpath, mode="w+t") as tmp:
        _logger.debug(f"Viewing contents of '{fpath}' ({type(schema).__qualname__})...")
        viewer.view(tmp)

    return True


def accept_file(fpath: str, manager: GoldenFileManager) -> None:
    """Accepts a generated file by moving it outside `.golden` directories its nested in.

    :param fpath:   Path to file to accept.
    :param manager: Golden file manager to use.
    """
    segments = list(Path(fpath).parts)
    g_dir_count = segments.count(".golden")

    if g_dir_count == 0:
        _logger.error(f"File {fpath} is not inside a '.golden' directory - Ignored.")
        return
    elif g_dir_count > 2:
        _logger.warning(f"File {fpath} is nested inside multiple '.golden' directories ({g_dir_count}).")

    new_path = Path(*[seg for seg in segments if seg != ".golden"])

    try:
        manager.move(fpath, new_path)
        _logger.info(f"Moved {fpath} to {new_path}")
    except FileNotFoundError as exc:
        _logger.error(f"{type(exc).__qualname__}: {exc}")

