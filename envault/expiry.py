"""Variable expiry policy: set, check, and list variables with expiry dates."""

from __future__ import annotations

import time
from typing import Any

_META_PREFIX = "__"
_EXPIRY_KEY = "__expiry__"


def _is_meta(key: str) -> bool:
    return key.startswith(_META_PREFIX)


def get_expiry(variables: dict[str, Any], key: str) -> float | None:
    """Return the expiry timestamp for *key*, or None if not set."""
    expiry_map: dict[str, float] = variables.get(_EXPIRY_KEY, {})
    return expiry_map.get(key)


def set_expiry(variables: dict[str, Any], key: str, expires_at: float) -> dict[str, Any]:
    """Return a new variables dict with an expiry timestamp set for *key*.

    Raises ValueError if *key* does not exist or is a meta key.
    Raises ValueError if *expires_at* is in the past.
    """
    if _is_meta(key):
        raise ValueError(f"Cannot set expiry on meta key: {key!r}")
    if key not in variables:
        raise ValueError(f"Variable {key!r} does not exist")
    if expires_at <= time.time():
        raise ValueError("expires_at must be a future timestamp")

    updated = dict(variables)
    expiry_map = dict(updated.get(_EXPIRY_KEY, {}))
    expiry_map[key] = expires_at
    updated[_EXPIRY_KEY] = expiry_map
    return updated


def remove_expiry(variables: dict[str, Any], key: str) -> dict[str, Any]:
    """Return a new variables dict with the expiry for *key* removed."""
    updated = dict(variables)
    expiry_map = dict(updated.get(_EXPIRY_KEY, {}))
    expiry_map.pop(key, None)
    if expiry_map:
        updated[_EXPIRY_KEY] = expiry_map
    else:
        updated.pop(_EXPIRY_KEY, None)
    return updated


def is_expired(variables: dict[str, Any], key: str) -> bool:
    """Return True if *key* has an expiry timestamp that has passed."""
    expiry = get_expiry(variables, key)
    if expiry is None:
        return False
    return time.time() >= expiry


def list_expiring(variables: dict[str, Any]) -> list[dict[str, Any]]:
    """Return a list of dicts describing all keys with expiry set, sorted soonest first."""
    expiry_map: dict[str, float] = variables.get(_EXPIRY_KEY, {})
    now = time.time()
    results = []
    for key, ts in expiry_map.items():
        results.append({"key": key, "expires_at": ts, "expired": now >= ts})
    results.sort(key=lambda r: r["expires_at"])
    return results


def purge_expired(variables: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    """Remove all expired variables. Returns (updated_vars, removed_keys)."""
    removed: list[str] = []
    updated = dict(variables)
    for key in list(updated.keys()):
        if not _is_meta(key) and is_expired(updated, key):
            del updated[key]
            updated = remove_expiry(updated, key)
            removed.append(key)
    return updated, removed
