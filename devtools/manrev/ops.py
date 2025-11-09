import logging
import os
import stat
import subprocess
import tempfile
from collections import OrderedDict
from collections.abc import Sequence
from glob import glob
from pathlib import Path
from typing import List

from tabulate import tabulate

from compiler_tests.utils.files import GoldenFileManager, TokenFileSchema, GoldenFileSchema
from compiler_tests.utils.metadata import TEST_DATADIR

_logger = logging.getLogger(__name__)
_golden_manager = GoldenFileManager(os.getcwd())


def find_files(
        root_dir: str = TEST_DATADIR,
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


def view_file(fpath: str) -> bool:
    """Views contents of a generated file based on its specified ``file_type`` (see :class:`GoldenFileSchema` for
    more details).

    Supported schemas: TokenFileSchema

    :param fpath:   Path to the file (absolute or relative to ``cwd``).
    :return:        Flag specifying whether file was viewed (or some error occured).
    """
    schema, cause = _golden_manager.safe_read(fpath)

    if schema is None:
        _logger.error(f"{type(cause).__qualname__}: {cause}")
        return False

    if schema.schema_version != type(schema).schema_version:
        _logger.warning(f"File may be outdated (Read schema_version='{schema.schema_version}'; "
                        f"Current: {type(schema).__qualname__}.schema_version='{type(schema).schema_version}')")

    if schema.file_type == TokenFileSchema.file_type:
        schema: TokenFileSchema
        tmp_pref = os.path.basename(fpath).replace('.', '_') + "_"
        table = tabulate({
            "Line": [tok.lineno for tok in schema.data.tokens],
            "Col": [tok.colno  for tok in schema.data.tokens],
            "Type": [tok.typ  for tok in schema.data.tokens],
            "Value": [repr(tok.value)  for tok in schema.data.tokens],
        }, headers="keys")

        with tempfile.NamedTemporaryFile(mode="w+", prefix=tmp_pref, suffix=".txt") as tmp:
            tmp.write(table)
            tmp.flush()
            os.chmod(tmp.name, 0o400)
            _logger.info(f"Viewing contents of {fpath} ({type(schema).__qualname__})...")
            subprocess.run(["gedit", "--standalone", tmp.name])

    return True

def accept_file(fpath: str) -> None:
    segments = list(Path(fpath).parts)

    try:
        segments.pop(segments.index('.golden'))
    except ValueError:
        _logger.warning(f"File {fpath} is not inside a '.golden' directory - Ignored.")
        return

    new_path = Path(*segments)
    _logger.info(new_path)

    try:
        _golden_manager.move(fpath, new_path)
    except FileNotFoundError as exc:
        _logger.error(f"{type(exc).__qualname__}: {exc}")


