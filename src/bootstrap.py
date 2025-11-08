from __future__ import annotations

import os
from functools import cache
from pathlib import Path
from datetime import datetime
from typing import Mapping

import tomllib

@cache
def bootstrap_project() -> None:
    """Calls methods to set up the project for execution.
    """
    set_environment_variables()
    configure_logging()

@cache
def set_environment_variables() -> Mapping[str, str]:
    """Initialize environment variables holding metadata (runs only once).

    Reads some of the metadata from ``pyproject.toml``.
    """
    root_path = Path(__file__).resolve().parents[1]
    toml_path = root_path / "pyproject.toml"
    data = tomllib.loads(toml_path.read_text())

    # Add this to ``os.environ`` later. Return this for debugging.
    to_add = {}

    # Set main metadata attributes
    meta = data.get("tool", {}).get("poetry", {})
    to_add.setdefault("EXEC_TIME", datetime.now().isoformat())
    to_add.setdefault("PROJECT_ROOT", str(root_path))
    to_add.setdefault("PROJECT_NAME", meta.get("name", "unknown"))
    to_add.setdefault("PROJECT_VERSION", meta.get("version", "0.0.0"))

    # Set schema versions from custom attributes
    meta = data.get("tool", {}).get("turing_io", {}).get("test", {}).get("schema_versions", {})
    to_add.setdefault("GOLDEN_FILE_SCHEMA_VERSION", meta.get("base", "0"))
    to_add.setdefault("TOKEN_FILE_SCHEMA_VERSION", meta.get("token", "0"))

    for key in to_add.keys():
        assert key not in os.environ, f"Overriding `os.environ` key '{key}'!"

    os.environ.update(to_add)
    return to_add

@cache
def configure_logging() -> None:
    pass


if __name__ == "__main__":
    from pprint import pprint

    bootstrap_project()
    added = set_environment_variables()

    for key_, value_ in added.items():
        assert key_ in os.environ
        assert os.environ[key_] == value_

    pprint(added)
