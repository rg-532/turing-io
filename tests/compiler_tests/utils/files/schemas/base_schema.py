"""This module defines the base schema called :class:`EmptySchema` and a mixin which it inherits from.
"""
from collections.abc import Mapping, MutableMapping, Iterator
from typing import Dict, Any, Optional
from dataclasses import dataclass, InitVar, KW_ONLY, fields


class ExtraAttrsMixin(MutableMapping[str, Any]):
    """This mixin allows any object inheriting from it to store extra attribute, which are accessible via the
    ``__getitem__``, ``__setitem__`` and ``__delitem__`` methods, as well as other mapping methods like ``__iter__``,
    ``__len__`` and ``__contains__``.

    In other words, this mixin attaches a dictionary to its subclasses, and supplies the standard methods which
    access this dictionary.

    **IMPORTANT:**
        The methods provided by this class **do not** manage normal instance members. The reasoning behind this is
        that such attributes should be accessed as normal, and the purpose of this mixin is to allow storage of extra
        attributes specifically.
    """
    def __init__(self, *args, extra_attrs: Optional[Mapping[str, Any]] = None, **kwargs):
        if extra_attrs:
            self._extra_attrs = dict(extra_attrs)
        super().__init__(*args, **kwargs)

    def __getitem__(self, key: str) -> Any:
        if not hasattr(self, "_extra_attrs"):
            raise KeyError(f"'{key}'")
        return self._extra_attrs[key]

    def __setitem__(self, key: str, value: Any) -> None:
        if not hasattr(self, "_extra_attrs"):
            self._extra_attrs: Dict[str, Any] = {}
        self._extra_attrs[key] = value

    def __delitem__(self, key: str) -> None:
        if not hasattr(self, "_extra_attrs") or key not in self._extra_attrs:
            raise KeyError(f"'{key}'")
        del self._extra_attrs[key]

        if not self._extra_attrs:
            del self._extra_attrs

    def __iter__(self) -> Iterator[str]:
        if not hasattr(self, "_extra_attrs"):
            return
        for key in self._extra_attrs.keys():
            yield key

    def __len__(self) -> int:
        if not hasattr(self, "_extra_attrs"):
            return 0
        return len(self._extra_attrs)

    def __contains__(self, item: str) -> bool:
        if not hasattr(self, "_extra_attrs"):
            return False
        return item in self._extra_attrs

    def __repr__(self):
        if not hasattr(self, "_extra_attrs"):
            return ""
        return repr(self._extra_attrs)


@dataclass(repr=False, kw_only=True)
class EmptySchema(ExtraAttrsMixin):
    """This is the base dataclass for all schemas in this project. It inherits from :class:`ExtraAttrsMixin` to allow
    flexibility of the standard ``dataclass`` implementation.

    When any subclass of this dataclass is defined, it should be decorated with the ``dataclass`` decorator. It is
    also recommended to set ``repr=False`` to include the extra attributes in the ``repr`` output.
    """
    _: KW_ONLY
    extra_attrs: InitVar[Optional[Mapping[str, Any]]] = None

    def __post_init__(self, extra_attrs: Optional[Mapping[str, Any]] = None):
        super().__init__(extra_attrs=extra_attrs)

    def __getitem__(self, key: str) -> Any:
        if hasattr(self, key):
            return getattr(self, key)
        try:
            return super().__getitem__(key)
        except KeyError:
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{key}'")

    def __setitem__(self, key: str, value: Any) -> None:
        if hasattr(self, key):
            return setattr(self, key, value)
        return super().__setitem__(key, value)

    def __delitem__(self, key: str) -> None:
        if hasattr(self, key):
            return self.__delattr__(key)
        try:
            return super().__delitem__(key)
        except KeyError:
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{key}'")

    def __iter__(self):
        for fld in fields(self):
            yield fld
        return super().__iter__()

    def __len__(self):
        return len(fields(self)) + super().__len__()

    def __contains__(self, item: str) -> bool:
        return hasattr(self, item) or super().__contains__(item)

    def __repr__(self):
        fields_reprs = [f"{f.name}={getattr(self, f.name)}" for f in fields(self)]

        if hasattr(self, "_extra_attrs"):
            fields_reprs.append(f"_extra_attrs={super().__repr__()}")

        return f"{self.__class__.__qualname__}({', '.join(fields_reprs)})"

