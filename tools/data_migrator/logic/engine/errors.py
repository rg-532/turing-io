from typing import Type

from data_migrator.logic.engine.types_ import T_Schema, Migration
from utils.common import get_func_desc


class MigrationExistsError(RuntimeError):
    """Raised when attempting to collect a migration function with migration parameters which already exist.

    In other words, this error is raised when two migrations functions migrate the same type of schema with the same
    source and destination versions, and collection of both is attempted.
    """
    def __init__(self,
                 schema_type: Type[T_Schema], src_version: str, dst_version: str,
                 old_func: Migration[T_Schema], new_func: Migration[T_Schema]) -> None:
        key = schema_type.__qualname__, src_version, dst_version
        message = (f"Migration exists for {key} already exists "
                   f"(existing: '{get_func_desc(old_func)}', "
                   f"new: '{get_func_desc(new_func)}')")
        super().__init__(message)


class NoMigrationPathError(RuntimeError):
    """Raised when a migration path (sequence of scripts) was not found."""
    pass
