"""TODO:
    - doc this
"""
from collections import deque
from functools import cached_property
from typing import Optional, List, Type, Dict, Generic

from compiler_tests.utils.files import GoldenFileSchema

from data_migrator.logic.engine.collector import get_collector, collect
from data_migrator.logic.engine.errors import NoMigrationPathError
from data_migrator.logic.engine.types_ import T_Schema, Migration
from utils.common import typed_cache, pre_call_hook, get_func_desc


@typed_cache
def _get_bfs_parent_map(schema_type: Type[GoldenFileSchema], src: str) -> Dict[str, str]:
    """Executes BFS from ``src`` in the version graph constructed for ``schema_type``, and returns a mapping of
    parents (``child:parent``) constructed in this process.

    Used for version path reconstruction from any destination.

    BFS is used since the graph is likely to be sparse and to avoid computation of unnecessary pathing.

    :param schema_type: Type of schema whose version graph is to be used.
    :param src:         Source versions representing root node for BFS.
    :return:            Mapping of ``version:parent_version`` generated from BFS.
                        The ``src`` version is not included in this map.
    """
    migrations = get_collector(schema_type).migrations
    queue = deque([src])
    parent = {src: "N/A"}

    while len(queue) > 0:
        curr = queue.popleft()

        for neighbor in migrations.get(curr, {}).keys():
            if neighbor not in parent:
                parent[neighbor] = curr
                queue.append(neighbor)

    parent.pop(src)
    return parent


class _MigrationExecutor(Generic[T_Schema]):
    """TODO - doc this.
    """
    def __init__(self, schema_type: Type[T_Schema], src: str, dst: str) -> None:
        self._schema_type: Type[T_Schema] = schema_type
        self._src: str = src
        self._dst: str = dst

    @cached_property
    def version_path(self) -> Optional[List[str]]:
        """Shortest path of versions from ``self._src`` to ``self._dst``, based on collected migrations for
        ``self._schema_type``.
        """
        parent = _get_bfs_parent_map(self._schema_type, self._src)

        if self._dst != self._src and self._dst not in parent:
            return None

        result = []
        curr = self._dst

        while curr != self._src:
            result.append(curr)
            curr = parent[curr]

        result.append(self._src)
        result.reverse()
        return result

    def needs_migration(self) -> bool:
        """Checks if the file needs migratable (file version does not match target version).
        """
        return self._src != self._dst

    def is_migratable(self) -> bool:
        """Checks if the file is migratable (has a migration path).\
        """
        return self.version_path is not None

    def get_path_str(self) -> str:
        """Return a string representation of a version path for migration of ``self.file``, or a fixed message
        if no such path exists or the file does not need migration.
        """
        if not self.is_migratable():
            return f"<no path {self._src} ~> {self._dst}>"
        elif not self.needs_migration():
            return "File does not need migration"

        return " -> ".join(self.version_path)

    @cached_property
    def scripts(self) -> Optional[List[Migration[T_Schema]]]:
        """Sequence of scripts (functions) to execute to migrate a schema, based on ``self.version_path``.

        Note that the number of scripts is always one less than the length of the version path.
        """
        path = self.version_path

        if path is None:
            return None

        migrations = get_collector(self._schema_type).migrations
        scripts: List[Migration[T_Schema]] = []

        for idx in range(1, len(path)):
            scripts.append(migrations[path[idx - 1]][path[idx]])

        return scripts

    def get_extended_path_desc(self) -> str:
        """Return a multiline string where each line is of the format::

            ({v1}->{v2}) calls:    {script_desc}

        and ``script_desc`` is a detailed description of the collected script which migrates the file from
        ``v1`` to ``v2`` (versions).

        Similarly to ``get_path_str``, if no migration path exists or migration is not needed, returns a fixed message.
        """
        if not self.is_migratable():
            return f"<no path {self._src} ~> {self._dst}>"
        elif not self.needs_migration():
            return "File does not need migration"

        path = self.version_path
        script_desc_list = [self.get_path_str()]

        for idx, script in enumerate(self.scripts):
            script_desc_list.append(f"({path[idx]} -> {path[idx + 1]}) calls:    {get_func_desc(script)}")

        return "\n\t".join(script_desc_list)

    def execute(self, schema: T_Schema) -> T_Schema:
        """Executes the sequence of migration scripts (could be empty, or just one) to migrate ``schema``.

        :param schema:  Schema to migrate.
        :return:        Resulted schema.

        :raises NoMigrationPathError:   If the schema cannot be migrated (no migration path).
        """
        scripts = self.scripts

        if scripts is None:
            NoMigrationPathError(f"Could not find a way to migrate a {self._schema_type.__qualname__} "
                                 f"from version '{self._src}' to version '{self._dst}'")

        for script in scripts:
            schema = script(schema)

        schema.schema_version = self._dst
        return schema

    def __call__(self, schema: T_Schema) -> T_Schema:
        return self.execute(schema)


@typed_cache
@pre_call_hook(collect)
def get_executor(schema_type: Type[T_Schema], src_version: str, dst_version: str) -> _MigrationExecutor[T_Schema]:
    return _MigrationExecutor(schema_type, src_version, dst_version)

