"""This tool supplies commands for updating outdated golden files.
"""
from pathlib import Path

from bootstrap import bootstrap_project

from loggers import click_logger

TOOL_PATH: Path = Path(__file__).parent

bootstrap_project()
click_logger.basic_config()
