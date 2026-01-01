import os

import click

from compiler_tests.utils.files import GoldenFileManager

from manrev.logic import ops
from utils.globbing import glob_result_to_str


@click.group('man-rev')
def manrev_cli() -> None:
    pass


@manrev_cli.command('scan', short_help='find golden files')
@click.option('--dir',    '-d', 'root_dir', default=os.getcwd(),
              metavar='<directory>', help="Directory path for the search process [defaults to cwd]")
@click.option('--suffix', '-s', 'suffixes', multiple=True, default=('.tm.tok',),
              metavar='<suffix>', show_default=True,
              help='Suffix of the files to be found. can be used multiple times for multiple suffixes')
def scan(root_dir: str, suffixes: tuple[str]) -> None:
    """Find golden files to review."""
    matches = ops.find_files(root_dir, suffixes)
    click.echo(glob_result_to_str(root_dir, matches))


@manrev_cli.command('show', short_help='show a file based on type')
@click.argument('file', metavar='<file_path>')
def show(file: str) -> None:
    """Show the file at <file_path> (absolute or relative to `cwd`)."""
    manager = GoldenFileManager(os.getcwd())
    prompt = "Accept the file (move outside '.golden' directories)?"

    if ops.view_file(file, manager) and click.confirm(prompt):
        ops.accept_file(file, manager)
