from __future__ import annotations

from typing import Any


class SafeMapping(dict[str, Any]):
    """A mapping class for string formatting, which is used as a parameter by ``str.format_map()``.

    When the formatted string requires some key which is not present in the arguments within some ``SafeMapping``
    object, the key and surrounding braces are left as is.

    Source: https://stackoverflow.com/a/19800610/22069431

    Example usage::

        template = "x = {x} and y = {y}"
        print(template.format_map(SafeMapping(x=5)))
        # x = 5 and y = {y}

    Notes:
        - Does not work with positional arguments. For example::

            template = "{} x = {x} y = {y}"

          is not formattable with this class.
        - Does not allow syntax of the form::

            `template = "{x=} {y=}"`

          This is also not supported by the existing ``str.format()`` and ``str.format_map()`` methods.
    """
    def __missing__(self, key: str) -> str:
        return '{' + key + '}'


def normal_str_to_raw(normal_str: str) -> str:
    """Transforms a normal string into a raw version for printing escaped characters as is.

    :param normal_str:  Normal python string that potentially has escape characters.
    :return:            Raw string version of ``normal_str``, with escaped characters included as is.

    source: https://stackoverflow.com/a/2428132/22069431
    """
    return normal_str.encode("unicode-escape").decode()


def raw_str_to_normal(raw_str: str) -> str:
    """Transforms a raw string into a normal version so that escaped characters apply.

    :param raw_str: Raw string that potentially has escape characters presented as is.
    :type raw_str:  str
    :return:        Normal string version of ``raw_str``, which has its escaped characters apply as expected.
    :rtype:         str
    """
    return raw_str.encode().decode("unicode-escape")
