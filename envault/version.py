"""Variable versioning — track multiple historic values for a key."""
from __future__ import annotations

import time
from typing import Any

_META_KEY = "__versions__"
_MAX_VERSIONS = 20


def _is_meta(key: str) -> bool:
    return key.startswith("__") and key.endswith("__")


def get_versions(variables: dict[str, Any], key: str) -> list[dict]:
    """Return the version history list for *key* (oldest first)."""
    meta = variables.get(_META_KEY, {})
    return list(meta.get(key, []))


def record_version(
    variables: dict[str, Any],
    key: str,
    value: str,
    *,
    max_versions: int = _MAX_VERSIONS,
) -> dict[str, Any]:
    """Push the current value of *key* onto its version stack.

    Returns a **new** variables dict; the original is not mutated.
    Raises ``KeyError`` if *key* is not present or is a meta key.
    """
    if _is_meta(key):
        raise KeyError(f"Cannot version meta key: {key}")
    if key not in variables:
        raise KeyError(f"Key not found: {key}")

    variables = dict(variables)
    meta = dict(variables.get(_META_KEY, {}))
    history: list[dict] = list(meta.get(key, []))

    entry = {"value": value, "timestamp": time.time()}
    history.append(entry)
    if len(history) > max_versions:
        history = history[-max_versions:]

    meta[key] = history
    variables[_META_KEY] = meta
    return variables


def rollback(
    variables: dict[str, Any],
    key: str,
    steps: int = 1,
) -> dict[str, Any]:
    """Restore *key* to the value *steps* versions ago.

    Returns a new variables dict.  Raises ``IndexError`` when there are
    not enough historic entries.
    """
    history = get_versions(variables, key)
    if len(history) < steps:
        raise IndexError(
            f"Not enough history for '{key}': "
            f"requested {steps} step(s), have {len(history)}."
        )

    target = history[-steps]
    variables = dict(variables)
    variables[key] = target["value"]
    return variables


def clear_versions(variables: dict[str, Any], key: str) -> dict[str, Any]:
    """Remove all version history for *key*. Returns a new dict."""
    variables = dict(variables)
    meta = dict(variables.get(_META_KEY, {}))
    meta.pop(key, None)
    if meta:
        variables[_META_KEY] = meta
    else:
        variables.pop(_META_KEY, None)
    return variables
