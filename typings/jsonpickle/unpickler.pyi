from collections.abc import Callable
from typing import Any, Literal, Optional

from jsonpickle.backend import JSONBackend


class Unpickler:
    pass


def decode(
    string: str,
    backend: Optional[JSONBackend] = None,
    context: Optional[Unpickler] = None,
    keys: bool = False,
    reset: bool = True,
    safe: bool = True,
    classes: Optional[type | dict[str, type]] = None,
    v1_decode: bool = False,
    on_missing: Literal['error', 'warn', 'ignore'] | Callable[..., Any] = 'ignore',
    handle_readonly: bool = False,
) -> Any:
    pass
