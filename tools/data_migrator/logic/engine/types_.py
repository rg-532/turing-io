from typing import TypeVar, TypeAlias, Callable, MutableMapping

from compiler_tests.utils.files import GoldenFileSchema

T_Schema = TypeVar("T_Schema", bound=GoldenFileSchema)

Migration: TypeAlias = Callable[[T_Schema], T_Schema]
MigrationsCollection: TypeAlias = MutableMapping[str, MutableMapping[str, Migration[T_Schema]]]
