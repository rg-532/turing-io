"""TODO - refactor -> doc
"""
import os
from collections import OrderedDict
from collections.abc import Callable
from glob import glob
from typing import Optional


def multi_glob(*patterns: str,
               remove_repeats: bool = True,
               flatten: bool = True,
               filter_callback: Optional[Callable[[str], bool]] = None,
               root_dir: Optional[str | bytes | os.PathLike[str] | os.PathLike[bytes]] = None,
               dir_fd: Optional[int] = None,
               recursive: bool = False,
               include_hidden: bool = False) -> list[str] | OrderedDict[str, list[str]]:
    """Invokes ``glob.glob`` for multiple patterns. Can also remove duplicates if necessary (Does so by default).
    If invoked with 0 patterns, returns an empty result (OrderedDict or List).

    :param patterns:        Patterns for ``glob.glob`` (0 or more).

    :param remove_repeats:  Flag specifying whether to remove repeat matches (defaults to ``True``).
    :param flatten:         Flag specifying whether to flatten all matches to one list, or return them in a dictionary
                            with entries of the form ``pattern:list_of_results`` (Defaults to ``True``).
                            Note that if ``flatten=False``, the returned dictionary won't contain patterns with no
                            matches as keys.
    :param filter_callback: Optional callable accepting ``AnyStr`` and returning ``True/False``.
                            If provided, matches only get added if calling this on them returns ``True``.

    :param root_dir:        ``glob.glob`` parameter ``root_dir``.
    :param dir_fd:          ``glob.glob`` parameter ``dir_fd``.
    :param recursive:       ``glob.glob`` parameter ``recursive``.
    :param include_hidden:  ``glob.glob`` parameter ``include_hidden``.

    :return:                Either a dictionary or list of matches.
    """
    seen = set()
    matches: OrderedDict[str, list[str]] = OrderedDict()

    for pat in patterns:
        for match in glob(pat, root_dir=root_dir, dir_fd=dir_fd, recursive=recursive, include_hidden=include_hidden):
            if remove_repeats and match in seen:
                continue

            seen.add(match)

            if filter_callback is None or filter_callback(match):
                matches.setdefault(pat, [])
                matches[pat].append(match)

    if flatten:
        return sum(matches.values(), start=[])

    return matches

