"""Lint/validate environment variable names and values."""

import re
from typing import Any

# POSIX-compliant env var name: letters, digits, underscores, not starting with digit
_VALID_NAME_RE = re.compile(r'^[A-Za-z_][A-Za-z0-9_]*$')

WARN_LOWERCASE = "name is lowercase (convention is UPPER_CASE)"
WARN_EMPTY_VALUE = "value is empty"
WARN_WHITESPACE_VALUE = "value has leading or trailing whitespace"
ERROR_INVALID_NAME = "name contains invalid characters or starts with a digit"
ERROR_EMPTY_NAME = "name is empty"


def lint_name(name: str) -> list[dict[str, str]]:
    """Return a list of issue dicts for the given variable name."""
    issues = []
    if not name:
        issues.append({"level": "error", "message": ERROR_EMPTY_NAME})
        return issues
    if not _VALID_NAME_RE.match(name):
        issues.append({"level": "error", "message": ERROR_INVALID_NAME})
    if name != name.upper():
        issues.append({"level": "warning", "message": WARN_LOWERCASE})
    return issues


def lint_value(value: Any) -> list[dict[str, str]]:
    """Return a list of issue dicts for the given variable value."""
    issues = []
    if value == "" or value is None:
        issues.append({"level": "warning", "message": WARN_EMPTY_VALUE})
        return issues
    if isinstance(value, str) and value != value.strip():
        issues.append({"level": "warning", "message": WARN_WHITESPACE_VALUE})
    return issues


def lint_variables(variables: dict[str, Any]) -> dict[str, list[dict[str, str]]]:
    """Lint all variables in a dict. Returns {name: [issues]} for entries with issues."""
    results: dict[str, list[dict[str, str]]] = {}
    for name, value in variables.items():
        issues = lint_name(name) + lint_value(value)
        if issues:
            results[name] = issues
    return results


def format_lint_results(results: dict[str, list[dict[str, str]]]) -> str:
    """Format lint results into a human-readable string."""
    if not results:
        return "No issues found."
    lines = []
    for name, issues in sorted(results.items()):
        for issue in issues:
            level = issue["level"].upper()
            lines.append(f"  [{level}] {name}: {issue['message']}")
    return "\n".join(lines)
