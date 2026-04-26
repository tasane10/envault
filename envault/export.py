"""Export vault contents to various shell-compatible formats."""

from __future__ import annotations

from typing import Dict

SUPPORTED_FORMATS = ("dotenv", "bash", "json")


def export_dotenv(variables: Dict[str, str]) -> str:
    """Export variables in .env format (KEY=VALUE)."""
    lines = []
    for key, value in sorted(variables.items()):
        escaped = value.replace('"', '\\"')
        lines.append(f'{key}="{escaped}"')
    return "\n".join(lines) + ("\n" if lines else "")


def export_bash(variables: Dict[str, str]) -> str:
    """Export variables as bash export statements."""
    lines = []
    for key, value in sorted(variables.items()):
        escaped = value.replace('"', '\\"')
        lines.append(f'export {key}="{escaped}"')
    return "\n".join(lines) + ("\n" if lines else "")


def export_json(variables: Dict[str, str]) -> str:
    """Export variables as a JSON object."""
    import json
    return json.dumps(variables, indent=2, sort_keys=True) + "\n"


def export_variables(variables: Dict[str, str], fmt: str) -> str:
    """Dispatch export to the correct formatter.

    Args:
        variables: Mapping of variable names to values.
        fmt: One of 'dotenv', 'bash', or 'json'.

    Returns:
        Formatted string representation of the variables.

    Raises:
        ValueError: If *fmt* is not a supported format.
    """
    if fmt == "dotenv":
        return export_dotenv(variables)
    elif fmt == "bash":
        return export_bash(variables)
    elif fmt == "json":
        return export_json(variables)
    else:
        raise ValueError(
            f"Unsupported format '{fmt}'. Choose from: {', '.join(SUPPORTED_FORMATS)}"
        )
