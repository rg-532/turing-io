from __future__ import annotations
import os
from functools import cache
from pathlib import Path
from datetime import datetime

import toml


@cache
def setup_environment() -> None:
    """Initialize environment variables holding metadata (runs only once).

    Reads some of the metadata from ``pyproject.toml``.
    """
    root_path = Path(__file__).resolve().parents[1]
    toml_path = root_path / "pyproject.toml"
    data = toml.loads(toml_path.read_text())

    meta = data.get("tool", {}).get("poetry", {})
    os.environ.setdefault("EXEC_TIME", datetime.now().isoformat())
    os.environ.setdefault("PROJECT_ROOT", str(root_path))
    os.environ.setdefault("PROJECT_NAME", meta.get("name", "unknown"))
    os.environ.setdefault("PROJECT_VERSION", meta.get("version", "0.0.0"))

