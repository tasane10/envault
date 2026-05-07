"""Retention policy: automatically delete variables older than N days."""

from __future__ import annotations

import time
from typing import Dict, List, Optional, Tuple

META_KEY = "__meta__"
_RETENTION_KEY = "_retention"


def _is_meta(key: str) -> bool:
    return key.startswith("__") and key.endswith("__")


def get_retention(variables: dict, key: str) -> Optional[int]:
    """Return retention days for *key*, or None if not set."""
    meta = variables.get(META_KEY, {})
    return meta.get(key, {}).get(_RETENTION_KEY)


def set_retention(variables: dict, key: str, days: int) -> dict:
    """Return a new variables dict with retention policy set for *key*."""
    if key not in variables or _is_meta(key):
        raise KeyError(f"Variable '{key}' does not exist.")
    if days <= 0:
        raise ValueError("Retention days must be a positive integer.")

    import copy
    variables = copy.deepcopy(variables)
    meta = variables.setdefault(META_KEY, {})
    entry = meta.setdefault(key, {})
    entry[_RETENTION_KEY] = days
    # Record the creation/set timestamp if not already present
    entry.setdefault("_created_at", time.time())
    return variables


def remove_retention(variables: dict, key: str) -> dict:
    """Return a new variables dict with the retention policy removed for *key*."""
    import copy
    variables = copy.deepcopy(variables)
    meta = variables.get(META_KEY, {})
    if key in meta:
        meta[key].pop(_RETENTION_KEY, None)
    return variables


def find_expired(variables: dict) -> List[str]:
    """Return list of keys whose retention period has elapsed."""
    now = time.time()
    expired: List[str] = []
    meta = variables.get(META_KEY, {})
    for key, info in meta.items():
        if _is_meta(key):
            continue
        days = info.get(_RETENTION_KEY)
        created_at = info.get("_created_at")
        if days is not None and created_at is not None:
            if now - created_at > days * 86400:
                expired.append(key)
    return sorted(expired)


def purge_expired(variables: dict) -> Tuple[dict, List[str]]:
    """Remove all variables whose retention period has elapsed.

    Returns (new_variables, list_of_purged_keys).
    """
    import copy
    expired = find_expired(variables)
    variables = copy.deepcopy(variables)
    meta = variables.get(META_KEY, {})
    for key in expired:
        variables.pop(key, None)
        meta.pop(key, None)
    return variables, expired
