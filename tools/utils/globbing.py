"""TODO - refactor -> doc
"""
import os
from collections import OrderedDict
from collections.abc import Callable
from glob import glob
from typing import AnyStr, Optional, List

import click


def multi_glob(*patterns: AnyStr,
               remove_repeats: bool = True,
               flatten: bool = True,
               filter_callback: Optional[Callable[[AnyStr], bool]] = None,
               root_dir: Optional[str | bytes | os.PathLike[str] | os.PathLike[bytes]] = None,
               dir_fd: Optional[int] = None,
               recursive: bool = False,
               include_hidden: bool = False) -> List[AnyStr] | OrderedDict[AnyStr, List[AnyStr]]:
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
    matches: OrderedDict[AnyStr, List[AnyStr]] = OrderedDict()

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


def _glob_list_to_str(match_list: List[AnyStr], start_idx: int) -> str:
    segments = []

    for res in match_list:
        segments.append(f"{str(start_idx)}   {res}")
        start_idx += 1

    return "\n".join(segments)

def glob_result_to_str(
        root_dir: str,
        matches: List[AnyStr] | OrderedDict[AnyStr, List[AnyStr]]) -> str:
    """Helper to transform matches collected via ``multi_glob`` to string.

    :param root_dir:
    :param matches:
    :return:
    """
    total = sum(len(res) for res in matches.values())
    root_dir_msg = ("under "
                    + click.style('', underline=True, reset=False)
                    + f"{root_dir}"
                    + click.style('', underline=False, reset=False))

    if total == 0:
        return click.style(f"\nNo files were found {root_dir_msg}", fg='green')

    start_idx = 0
    segments = [
        click.style('\nFound ', fg='yellow', reset=False)
        + click.style('', bold=True, underline=True, reset=False)
        + f"{total} file{"s" if total != 1 else ""}"
        + click.style('', bold=False, underline=False, reset=False)
        + f" {root_dir_msg}"]

    for pattern, match_list in matches.items():
        segments.append(
            f"Files matching '"
            + click.style('', bold=True, reset=False)
            + pattern
            + click.style('', bold=False, reset=False)
            + f"'  (total = {len(match_list)})\n"
            + _glob_list_to_str(match_list, start_idx))
        start_idx += len(match_list)

    return "\n\n".join(segments) + click.style('', reset=True)


