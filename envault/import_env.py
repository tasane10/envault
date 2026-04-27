"""Import environment variables from external sources into the vault."""

import json
import os
import re
from pathlib import Path
from typing import Dict, Optional


def parse_dotenv(content: str) -> Dict[str, str]:
    """Parse a .env file content into a dictionary of key-value pairs."""
    variables: Dict[str, str] = {}
    for line in content.splitlines():
        line = line.strip()
        # Skip empty lines and comments
        if not line or line.startswith("#"):
            continue
        # Handle export prefix (e.g. `export KEY=VALUE`)
        if line.startswith("export "):
            line = line[len("export "):].strip()
        if "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip()
        # Strip surrounding quotes (single or double)
        if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
            value = value[1:-1]
        if key:
            variables[key] = value
    return variables


def parse_json_env(content: str) -> Dict[str, str]:
    """Parse a JSON object into a dictionary of string key-value pairs."""
    data = json.loads(content)
    if not isinstance(data, dict):
        raise ValueError("JSON env file must contain a top-level object")
    result: Dict[str, str] = {}
    for key, value in data.items():
        if not isinstance(key, str):
            raise ValueError(f"JSON env key must be a string, got: {type(key).__name__}")
        result[key] = str(value)
    return result


def import_variables(file_path: str, fmt: Optional[str] = None) -> Dict[str, str]:
    """Read and parse an env file, auto-detecting format when not specified.

    Supported formats: 'dotenv', 'json'.
    Auto-detection is based on the file extension.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    content = path.read_text(encoding="utf-8")

    if fmt is None:
        if path.suffix.lower() == ".json":
            fmt = "json"
        else:
            fmt = "dotenv"

    if fmt == "json":
        return parse_json_env(content)
    elif fmt == "dotenv":
        return parse_dotenv(content)
    else:
        raise ValueError(f"Unsupported import format: {fmt}")
