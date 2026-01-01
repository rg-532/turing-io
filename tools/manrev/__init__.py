"""This tool supplies commands to aid with manual review of golden files.
"""
from bootstrap import bootstrap_project

from loggers import click_logger

bootstrap_project()
click_logger.basic_config()
