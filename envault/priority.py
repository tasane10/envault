"""Variable priority management for envault.

Allows assigning numeric priority levels to variables, useful for
ordering resolution and understanding override importance.
"""

from __future__ import annotations

META_PREFIX = "__"
PRIORITY_KEY = "__priority__"


def _is_meta(key: str) -> bool:
    return key.startswith(META_PREFIX)


def get_priority(variables: dict, key: str) -> int | None:
    """Return the priority level for *key*, or None if not set."""
    meta = variables.get(PRIORITY_KEY, {})
    if not isinstance(meta, dict):
        return None
    value = meta.get(key)
    return int(value) if value is not None else None


def set_priority(variables: dict, key: str, level: int) -> dict:
    """Return a new variables dict with *key* assigned priority *level*."""
    if _is_meta(key):
        raise ValueError(f"Cannot set priority on metadata key: {key!r}")
    if key not in variables:
        raise KeyError(f"Variable {key!r} does not exist")
    if not isinstance(level, int) or level < 0:
        raise ValueError("Priority level must be a non-negative integer")
    updated = dict(variables)
    meta = dict(updated.get(PRIORITY_KEY, {}))
    meta[key] = level
    updated[PRIORITY_KEY] = meta
    return updated


def remove_priority(variables: dict, key: str) -> dict:
    """Return a new variables dict with the priority for *key* removed."""
    updated = dict(variables)
    meta = dict(updated.get(PRIORITY_KEY, {}))
    meta.pop(key, None)
    if meta:
        updated[PRIORITY_KEY] = meta
    else:
        updated.pop(PRIORITY_KEY, None)
    return updated


def list_priorities(variables: dict) -> dict[str, int]:
    """Return a mapping of key -> priority for all prioritised variables."""
    meta = variables.get(PRIORITY_KEY, {})
    if not isinstance(meta, dict):
        return {}
    return {k: int(v) for k, v in meta.items()}


def sort_by_priority(variables: dict, descending: bool = True) -> list[str]:
    """Return variable keys sorted by priority (highest first by default).

    Keys without an explicit priority are placed at the end.
    """
    priorities = list_priorities(variables)
    keys = [k for k in variables if not _is_meta(k)]
    return sorted(
        keys,
        key=lambda k: priorities.get(k, -1 if descending else 10**9),
        reverse=descending,
    )
