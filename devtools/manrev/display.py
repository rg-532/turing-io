from collections import OrderedDict
from typing import List

import click


def print_scan(root_dir: str, scan_result: OrderedDict[str, List[str]]) -> None:
    """Helper to print results collected in ``scan`` command.
    """
    total = sum(len(res) for res in scan_result.values())

    if total == 0:
        click.echo(click.style(
            "No files to review under "
            + click.style('', underline=True, reset=False)
            + f"{root_dir}"
            + click.style('', underline=False, reset=False),
            fg='green'))
        return

    click.echo(click.style('', fg='yellow', reset=False))
    click.echo(
        f"Found "
        + click.style('', bold=True, underline=True, reset=False)
        + f"{total} file{"s" if total != 1 else ""}"
        + click.style('', bold=False, underline=False, reset=False)
        + f" to review under "
        + click.style('', underline=True, reset=False)
        + f"{root_dir}\n"
        + click.style('', underline=False, reset=False))

    for suffix, results in scan_result.items():
        click.echo(
            f"Files ending with '"
            + click.style('', bold=True, reset=False)
            + suffix
            + click.style('', bold=False, reset=False)
            + f"'  (total = {len(results)})")

        for idx, res in enumerate(results):
            click.echo(
                click.style('', bold=True, reset=False)
                + str(idx)
                + click.style('', bold=False, reset=False)
                + f"   {res}")

    click.echo(click.style('', reset=True))
