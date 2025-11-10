import os
from typing import Tuple

import click

from compiler_tests.utils.files import GoldenFileManager
from manrev.logic import ops
from manrev.display import print_scan


@click.group('man-rev')
def manrev() -> None:
    pass


@manrev.command('scan', short_help='find golden files')
@click.option('--dir',    '-d', 'root_dir', default=os.getcwd(),
              metavar='<directory>', help="Directory path for the search process [defaults to cwd]")
@click.option('--suffix', '-s', 'suffixes', multiple=True, default=('.tm.tok',),
              metavar='<suffix>', show_default=True,
              help='Suffix of the files to be found. can be used multiple times for multiple suffixes')
def scan(root_dir: str, suffixes: Tuple['str']) -> None:
    """Find golden files to review."""
    scan_result = ops.find_files(root_dir, suffixes)
    print_scan(root_dir, scan_result)


@manrev.command('show', short_help='show a file based on type')
@click.argument('fpath', metavar='<file_path>')
def show(fpath: str) -> None:
    """Show the file at <file_path> (absolute or relative to `cwd`)."""
    manager = GoldenFileManager(os.getcwd())
    mod_time = os.path.getmtime(fpath)
    prompt = "Accept the file (move outside '.golden' directories)?"

    if ops.view_file(fpath, manager) and click.confirm(prompt):
        if mod_time != os.path.getmtime(fpath):
            click.secho('Warning: File has been modified!    ', nl=False, fg='yellow')

            if not click.confirm("Accept anyway?"):
                return

        ops.accept_file(fpath, manager)
