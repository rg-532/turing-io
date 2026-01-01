"""TODO - doc this
"""
import importlib
import os
import sys
from collections import OrderedDict
from collections.abc import Callable
from functools import cache
from pathlib import Path

from compiler_tests.utils.files import GoldenFileSchema
from data_migrator import TOOL_PATH
from data_migrator.logic.engine.types_ import Migration, MigrationsCollection
from data_migrator.logic.engine.errors import MigrationExistsError
from utils.common import typed_cache
from compiler.utils.globbing import multi_glob


class _MigrationsCollector[T_Schema: GoldenFileSchema](object):
    def __init__(self, schema_type: type[T_Schema]):
        self._schema_type: type[T_Schema] = schema_type  # For reporting.
        self.migrations: MigrationsCollection = OrderedDict()

    def add_script(self, src_v: str, dst_v: str, func: Migration[T_Schema]) -> None:
        self.migrations.setdefault(src_v, OrderedDict())

        if dst_v in self.migrations[src_v]:
            old_func = self.migrations[src_v][dst_v]
            raise MigrationExistsError.from_params(self._schema_type, src_v, dst_v, old_func, func)

        self.migrations[src_v][dst_v] = func


@typed_cache
def get_collector[T_Schema: GoldenFileSchema](schema_type: type[T_Schema]) -> _MigrationsCollector[T_Schema]:
    """Factory method of :class:`_MigrationsCollector`. Ensures that the same collector is returned for the same type
    (using ``functools.cache``).

    :param schema_type: Type of schema to get the collector for.
    :return:            Migrations collector for the given type.
    """
    return _MigrationsCollector(schema_type)


def migrates[T_Schema: GoldenFileSchema](
        schema_type: type[T_Schema], src_version: str, dst_version: str
) -> Callable[[Migration[T_Schema]], Migration[T_Schema]]:
    """Decorator factory for decorator which registers the decorated function into the singleton instance of
    :class:`MigrationsCollector` with key (``schema_type``, ``src_version``, ``dst_version``).

    If ``src_version`` == ``dst_version``, the decorated function is not registered.

    :param schema_type: Type of the schema.
    :param src_version: Source version of the schema.
    :param dst_version: Destination version of the schema.

    :return:            Decorator which registers the decorated function.
    """
    def decorator(func: Migration[T_Schema]) -> Migration[T_Schema]:
        if src_version != dst_version:
            get_collector(schema_type).add_script(src_version, dst_version, func)

        return func
    return decorator


@cache  # Ensure this runs at most once.
def collect() -> None:
    """Collection script which goes to ``scmvmig`` root directory and from there imports ALL migration scripts.

    The scripts must be contained in python files, nested at any level from root, with names matching one of:
        - ``migrate_*.py``
        - ``*_migration.py``
        - ``*_migrations.py``

    The script locates all such files and imports them dynamically with names relative to the root of the project
    (under "turing_io/tools/").

    All such scripts must be decorated with ``migrates``, so that importing these files causes the decorated functions
    to be added to the migrations' collection.
    """
    assert any([TOOL_PATH.is_relative_to(sp) for sp in sys.path])
    module_prefix = '.'.join(TOOL_PATH.relative_to(os.environ["PROJECT_ROOT"]).parts[1:])
    results: list[Path] = []

    # Collect paths to relevant files:
    for res in multi_glob("**/migrate_*.py", "**/*_migration.py", "**/*_migrations.py",
                          root_dir=TOOL_PATH, recursive=True):
        if (TOOL_PATH / res).is_file() and res.endswith(".py"):
            results.append(Path(res))

    # Import each file via importlib
    for res in results:
        while res.suffix:
            res = res.with_suffix('')

        module_name = '.'.join((module_prefix,) + res.parts)
        importlib.import_module(module_name)

