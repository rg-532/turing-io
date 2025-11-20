from datetime import datetime
import logging
import os
from collections.abc import Sequence
from json import JSONDecodeError
from pathlib import Path
from typing import List, OrderedDict, Optional, Tuple

from compiler_tests.utils.files import GoldenFileManager, ClassNotFoundError, GoldenFileSchema

from data_migrator.logic.engine.errors import NoMigrationPathError
from data_migrator.logic.engine.executor import get_executor

from utils.globbing import multi_glob

_logger = logging.getLogger(__name__)


def find_files(
        manager: GoldenFileManager[GoldenFileSchema],
        suffixes: Sequence[str] = ('.tm.tok',)
) -> OrderedDict[str, List[Tuple[str, str]]]:
    """Fetches all files that need migration (based on their ``schema_version`` and the current one for their class)
    under directory at ``manager.dirpath``. Filters for those ending with any ``suffixes``, and returns a dictionary
    of entries ``(pattern,result_list)`` with each result being a tuple of ``(file,version_path)``.

    Excludes files under hidden directory, including unreviewed golden files and backup files from old migrations.

    :param manager:     Golden file manager whose directory should be searched.
    :param suffixes:    A sequence of suffixes which are allowed for the returned files.
    :return:            The result dictionary.
    """
    patterns = [f"**/*{suf}" for suf in suffixes]

    found_files = multi_glob(
        *patterns, root_dir=str(manager.dirpath), recursive=True, flatten=False,
        filter_callback=lambda m: os.path.isfile(manager.get_path(m)))

    results: OrderedDict[str, List[Tuple[str, str]]] = OrderedDict()

    for pattern, file_list in list(found_files.items()):
        result_list: List[Tuple[str, str]] = []

        for file in file_list:
            try:
                schema = manager.read(file)
                executor = get_executor(type(schema), schema.schema_version, type(schema).schema_version)

                if executor.needs_migration():
                    result_list.append((file, executor.get_path_str()))
            except (JSONDecodeError, UnicodeDecodeError) as cause:
                _logger.info(f"Decode error - {file} is probably not golden (Got {type(cause).__qualname__}: {cause})")
            except ClassNotFoundError as cause:
                _logger.error(f"{type(cause).__qualname__}: {cause}")

        if result_list:
            results[pattern] = result_list

    return results


def get_file_migration(
        file: str,
        manager: GoldenFileManager[GoldenFileSchema]
) -> Optional[str]:
    """Returns a detailed description of how `file` is to be migrated, returns ``None`` if some error occurred.

    :param file:    File to show migration for.
    :param manager: Golden file manager for read.
    :return:        Detailed description of ``file`` migration, or ``None`` on error.
    """
    try:
        schema = manager.read(file)
        executor = get_executor(type(schema), schema.schema_version, type(schema).schema_version)
        return executor.get_extended_path_desc()
    except (JSONDecodeError, UnicodeDecodeError, ClassNotFoundError, IOError) as cause:
        _logger.error(f"READ FAIL ({file}) - {type(cause).__qualname__}: {cause}")

    return None


def _make_backup_path(file: str) -> str:
    """Helper method to make a backup path of ``file`` for backing up old files during migration.

    The generated backup path is the same as ``file`` where the file name is prefixed by ``.backup/current_date``.

    :param file:    File to base the backup path for.
    :return:        Backup path for the file.
    """
    parts = list(Path(file).parts)
    parts.insert(-1, f".backup/{datetime.now().strftime("%Y_%m_%d_%H_%M_%S")}")
    return str(Path(*parts))


def execute_file_migration(
        file: str,
        manager: GoldenFileManager[GoldenFileSchema],
        backup: bool = False
) -> None:
    """Reads schema from ``file``, then migrates and writes it to the same location.

    :param file:    File to migrate and write
    :param manager: Golden file manager for read and write.
    :param backup:  Whether to create a back-up copy of old files.
    """
    try:
        schema = manager.read(file)
        executor = get_executor(type(schema), schema.schema_version, type(schema).schema_version)

        if executor.needs_migration():
            _logger.info(f"Migrating {file} ({executor.get_path_str()})...")
            schema = executor(schema)

            if backup:
                manager.copy_file(file, _make_backup_path(file))

            manager.write(file, schema, allow_overwrite=True)
    except (JSONDecodeError, UnicodeDecodeError, ClassNotFoundError, IOError) as cause:
        _logger.error(f"READ FAIL ({file}) - {type(cause).__qualname__}: {cause}")
    except NoMigrationPathError as cause:
        _logger.error(f"MIGRATE FAIL ({file}) - {type(cause).__qualname__}: {cause}")

