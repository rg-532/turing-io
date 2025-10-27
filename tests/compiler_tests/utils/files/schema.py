"""TODO:
    - Doc this.
    - Define the schema (Determine which of the following is globally relevant):
        - file type (token, ast, etc.)
        - versioning (project, schema, optionally language)
        - timestamp
        - generating component + source file
        - metadata (empty for base):
            - testing config (test name)
            - version of golden file maybe
            -
"""
import os
from dataclasses import dataclass, field
from typing import Dict, Any


@dataclass
class BaseJsonSchema:
    file_type: str
    generated_by: str

    project_version: str = os.environ.get("PROJECT_VERSION", "0.0.0")
    schema_version: str = "1"
    tmlang_version: str = "1.0"
    timestamp: str = os.environ.get("EXEC_START_TIME", "0000-00-00 00:00:00.00000")

    metadata: Dict[str, Any] = field(default_factory=dict)

    data: Dict[str, Any] = field(default_factory=dict)


