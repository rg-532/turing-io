from collections import OrderedDict

import click


def _glob_list_to_str(match_list: list[str], start_idx: int) -> str:
    segments = []

    for res in match_list:
        segments.append(f"{str(start_idx)}   {str(res)}")
        start_idx += 1

    return "\n".join(segments)


def glob_result_to_str(
        root_dir: str,
        matches: OrderedDict[str, list[str]]) -> str:
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
