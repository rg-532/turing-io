import click

from devtools.manrev import cli


@click.group('man-rev')
def manrev() -> None:
    pass

manrev.add_command(cli.scan)
manrev.add_command(cli.show)
manrev()
