"""This tool supplies commands for updating outdated golden files.
"""
from pathlib import Path

from loggers import click_logger

TOOL_PATH: Path = Path(__file__).parent

click_logger.basic_config()
