"""Compliance checks for environment variables (naming conventions, forbidden patterns)."""

from __future__ import annotations

import re
from typing import Dict, List, NamedTuple

_FORBIDDEN_PATTERNS: List[re.Pattern] = [
    re.compile(r"(?i)password\s*=\s*\S+"),
    re.compile(r"(?i)secret\s*=\s*\S+"),
    re.compile(r"(?i)token\s*=\s*\S+"),
]

_META_PREFIX = "__"


class ComplianceIssue(NamedTuple):
    key: str
    severity: str  # "error" | "warning"
    message: str


def _is_meta(key: str) -> bool:
    return key.startswith(_META_PREFIX)


def check_naming(key: str) -> List[ComplianceIssue]:
    """Return issues related to key naming conventions."""
    issues: List[ComplianceIssue] = []
    if not re.match(r"^[A-Z_][A-Z0-9_]*$", key):
        if re.match(r"^[a-z_][a-z0-9_]*$", key):
            issues.append(ComplianceIssue(key, "warning", "Key should be UPPER_SNAKE_CASE"))
        else:
            issues.append(ComplianceIssue(key, "error", "Key contains invalid characters or casing"))
    return issues


def check_value(key: str, value: str) -> List[ComplianceIssue]:
    """Return issues related to sensitive value exposure."""
    issues: List[ComplianceIssue] = []
    combined = f"{key}={value}"
    for pattern in _FORBIDDEN_PATTERNS:
        if pattern.search(combined):
            issues.append(
                ComplianceIssue(
                    key,
                    "warning",
                    f"Key '{key}' may contain a sensitive value stored in plain text",
                )
            )
            break
    if len(value) == 0:
        issues.append(ComplianceIssue(key, "warning", "Value is empty"))
    return issues


def run_compliance(variables: Dict[str, str]) -> List[ComplianceIssue]:
    """Run all compliance checks against a variables dict."""
    results: List[ComplianceIssue] = []
    for key, value in variables.items():
        if _is_meta(key):
            continue
        results.extend(check_naming(key))
        results.extend(check_value(key, value))
    return results


def format_compliance_results(issues: List[ComplianceIssue]) -> str:
    """Format compliance issues for display."""
    if not issues:
        return "No compliance issues found."
    lines = []
    for issue in issues:
        prefix = "[ERROR]" if issue.severity == "error" else "[WARN] "
        lines.append(f"{prefix} {issue.key}: {issue.message}")
    return "\n".join(lines)
