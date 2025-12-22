from collections.abc import Callable, MutableMapping

from compiler_tests.utils.files import GoldenFileSchema

type Migration[T_Schema: GoldenFileSchema] = Callable[[T_Schema], T_Schema]
type MigrationsCollection[T_Schema: GoldenFileSchema] = MutableMapping[str, MutableMapping[str, Migration[T_Schema]]]
