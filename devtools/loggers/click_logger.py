import logging

import click




class ClickFormatter(logging.Formatter):
    LEVEL_STYLES = {
        "error":    dict(fg='red', bold=True),
        "exception":    dict(fg='red', bold=True),
        "critical":     dict(bg='red'),
        "warning":      dict(fg='yellow'),
        "debug":        dict(fg='bright_blue')
    }

    def format(self, record: logging.LogRecord) -> str:

        level = record.levelname.lower()

        if level in self.LEVEL_STYLES:
            styles = self.LEVEL_STYLES[level]
        else:
            styles = dict()

        message = (
                click.style('', **styles, reset=False)
                + super().format(record)
                + click.style('')
        )

        return message


class ClickHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        click.echo(self.format(record))


def basic_config(fmt: str = "%(levelname)-8s|    %(message)s", level: str = "INFO") -> None:
    click_handler = ClickHandler(level=level)
    click_handler.setFormatter(ClickFormatter(fmt=fmt))

    logging.basicConfig(format=fmt, level=level, handlers=[click_handler])

