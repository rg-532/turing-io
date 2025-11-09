from collections import OrderedDict
from typing import Tuple, TYPE_CHECKING, List

import click

from compiler_tests.utils.metadata import TEST_DATADIR
from manrev import ops

if TYPE_CHECKING:
    scan: click.Command
    show: click.Command


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

    click.echo(click.style(
        f"Found "
        + click.style('', bold=True, underline=True, reset=False)
        + f"{total} file{"s" if total != 1 else ""}"
        + click.style('', bold=False, underline=False, reset=False)
        + f" to review under "
        + click.style('', underline=True, reset=False)
        + f"{root_dir}\n"
        + click.style('', underline=False, reset=False),
        fg='yellow'))

    for suffix, results in scan_result.items():
        click.echo(click.style(
            f"Files ending with '"
            + click.style('', bold=True, reset=False)
            + suffix
            + click.style('', bold=False, reset=False)
            + f"'  (total = {len(results)})",
            fg='yellow'))

        for idx, res in enumerate(results):
            click.echo(click.style(
                click.style('', bold=True, reset=False)
                + str(idx)
                + click.style('', bold=False, reset=False)
                + f"   {res}",
                fg='yellow'))


@click.command('scan', short_help='find golden files')
@click.option('--dir',    '-d', 'root_dir', default=TEST_DATADIR,
              metavar='<directory>', show_default=True,
              help="Directory path for the search process")
@click.option('--suffix', '-s', 'suffixes', multiple=True, default=('.tm.tok',),
              metavar='<suffix>', show_default=True,
              help='Suffix of the files to be found. can be used multiple times for multiple suffixes')
def scan(root_dir: str, suffixes: Tuple['str']) -> None:
    """Find golden files to review."""
    print_scan(root_dir, ops.find_files(root_dir, suffixes))


@click.command('show', short_help='show a file based on type')
@click.argument('fpath', metavar='<file_path>')
def show(fpath: str) -> None:
    """Show the file at <file_path> (absolute or relative to `cwd`)."""
    prompt = "Should the file be accepted (moved outside '.golden' directory)?"

    if ops.view_file(fpath) and click.confirm(prompt):
        ops.accept_file(fpath)


