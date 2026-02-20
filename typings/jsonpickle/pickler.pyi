from collections.abc import Callable
from typing import Any, Optional

from jsonpickle.backend import JSONBackend

class Pickler:
    pass


def encode(
    value: Any,
    unpicklable: bool = True,
    make_refs: bool = True,
    keys: bool = False,
    max_depth: Optional[int] = None,
    reset: bool = True,
    backend: Optional[JSONBackend] = None,
    warn: bool = False,
    context: Optional[Pickler] = None,
    max_iter: Optional[int] = None,
    use_decimal: bool = False,
    numeric_keys: bool = False,
    use_base85: bool = False,
    fail_safe: Optional[Callable[..., Any]] = None,
    indent: Optional[int] = None,
    separators: Optional[tuple[str, str]] = None,
    include_properties: bool = False,
    handle_readonly: bool = False,
) -> str:
    ...