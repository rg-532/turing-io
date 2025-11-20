import os
from collections import OrderedDict
from typing import Tuple, List

import click
from docutils.nodes import description
from tabulate import tabulate

from compiler_tests.utils.files import GoldenFileManager

from data_migrator.logic import ops
from utils.globbing import glob_result_to_str


@click.group('data-mig', chain=True)
@click.option('--dir', '-d', 'root_dir', default=os.getcwd(),
              metavar='<dir>', help="Changes directory to operate under from current directory.")
@click.pass_context
def data_migrator_cli(ctx: click.Context, root_dir: str) -> None:
    ctx.ensure_object(dict)
    ctx.obj["manager"] = GoldenFileManager(root_dir)


def display_scan_result(results: OrderedDict[str, List[Tuple[str,  str]]], root_dir: str):
    described_matches: OrderedDict[str, List[str]] = OrderedDict()

    for pattern, result_list in results.items():
        result_table = tabulate(result_list, tablefmt='plain')
        described_matches[pattern] = result_table.split("\n")

    click.echo(glob_result_to_str(root_dir, described_matches))


@data_migrator_cli.command('scan', short_help='find files to migrate')
@click.option('--suffix', '-s', 'suffixes', multiple=True, default=('.tm.tok',),
              metavar='<suffix>', show_default=True,
              help='Suffix of the files to be found. can be used multiple times for multiple suffixes')
@click.pass_context
def scan(ctx: click.Context, suffixes: Tuple[str, ...]) -> None:
    """Find files which need migration."""
    data = ctx.obj
    data["scan_results"] = ops.find_files(data["manager"], suffixes)
    display_scan_result(data["scan_results"], str(data["manager"].dirpath))


@data_migrator_cli.command('migrate', short_help='migrate a file')
@click.argument('files', metavar='[file_paths]', nargs=-1, required=False)
@click.option('--show-only', 'show_only', is_flag=True,
              help="Shows a detailed description of migration and exit.")
@click.option('--backup/--no-backup', 'backup', default=True,
              help="Shows a detailed description of migration and exit.")
@click.pass_context
def migrate(ctx: click.Context, files: Tuple[str, ...], show_only: bool, backup: bool) -> None:
    """Migrate files at [file_paths] to latest version.

    Can be chained after 'scan' to migrate all results, but requires [file_paths] to be empty.
    """
    data = ctx.obj
    files = list(files)

    if "scan_results" in data:
        click.echo()
        scanned_files = [v[0] for vals in data["scan_results"].values() for v in vals if v[0] not in files]
        files += scanned_files

    if len(files) == 0:
        click.secho("No files to migrate...", fg='green', bold=True)
        ctx.exit(code=0)

    if show_only:
        descriptions = []

        for file in files:
            desc = ops.get_file_migration(file, data["manager"])

            if desc is not None:
                descriptions.append(f"{file}\npath:  {desc}")

        click.echo('\n\n'.join(descriptions))
    else:
        if "scan_results" in data:
            click.confirm("You are about to migrate ALL above files - proceed?", abort=True)
            data.pop("scan_results")
            click.echo()

        for file in files:
            ops.execute_file_migration(file, data["manager"], backup)


