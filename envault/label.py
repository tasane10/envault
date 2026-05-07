"""Label management for environment variables.

Labels are free-form string tags that can be attached to variables
for human-readable categorisation (e.g. 'production', 'secret', 'legacy').
Unlike groups or tags, labels are lightweight and support multi-label queries.
"""
from __future__ import annotations

from typing import Any

_META_KEY = "__labels__"


def get_labels(variables: dict[str, Any]) -> dict[str, list[str]]:
    """Return the labels mapping stored in *variables* metadata."""
    meta = variables.get(_META_KEY, {})
    if not isinstance(meta, dict):
        return {}
    return {k: list(v) for k, v in meta.items()}


def set_labels(variables: dict[str, Any], key: str, labels: list[str]) -> dict[str, Any]:
    """Return a new variables dict with *labels* assigned to *key*.

    Raises KeyError if *key* does not exist as a real variable.
    """
    if key not in variables or key.startswith("__"):
        raise KeyError(f"Variable '{key}' not found.")
    updated = dict(variables)
    meta = dict(updated.get(_META_KEY, {}))
    if labels:
        meta[key] = sorted(set(labels))
    else:
        meta.pop(key, None)
    updated[_META_KEY] = meta
    return updated


def remove_labels(variables: dict[str, Any], key: str) -> dict[str, Any]:
    """Return a new variables dict with all labels removed from *key*."""
    return set_labels(variables, key, [])


def filter_by_label(variables: dict[str, Any], label: str) -> dict[str, str]:
    """Return variables whose label list contains *label*.

    Metadata keys are excluded from the result.
    """
    meta = variables.get(_META_KEY, {})
    return {
        k: v
        for k, v in variables.items()
        if not k.startswith("__")
        and label in meta.get(k, [])
    }


def list_labels(variables: dict[str, Any]) -> list[str]:
    """Return a sorted list of all unique labels used across all variables."""
    meta = variables.get(_META_KEY, {})
    seen: set[str] = set()
    for labels in meta.values():
        seen.update(labels)
    return sorted(seen)
