"""TTL (time-to-live) support for environment variables."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

META_KEY = "__meta__"
TTL_KEY = "ttl"


def set_ttl(variables: dict, key: str, seconds: int) -> dict:
    """Set a TTL (in seconds from now) on a variable."""
    variables = dict(variables)
    meta = dict(variables.get(META_KEY, {}))
    key_meta = dict(meta.get(key, {}))
    expires_at = datetime.now(timezone.utc).timestamp() + seconds
    key_meta[TTL_KEY] = expires_at
    meta[key] = key_meta
    variables[META_KEY] = meta
    return variables


def get_ttl(variables: dict, key: str) -> Optional[float]:
    """Return the expiry timestamp for a variable, or None if no TTL is set."""
    meta = variables.get(META_KEY, {})
    return meta.get(key, {}).get(TTL_KEY)


def is_expired(variables: dict, key: str) -> bool:
    """Return True if the variable's TTL has passed."""
    expires_at = get_ttl(variables, key)
    if expires_at is None:
        return False
    return datetime.now(timezone.utc).timestamp() > expires_at


def remove_ttl(variables: dict, key: str) -> dict:
    """Remove the TTL from a variable."""
    variables = dict(variables)
    meta = dict(variables.get(META_KEY, {}))
    key_meta = dict(meta.get(key, {}))
    key_meta.pop(TTL_KEY, None)
    if key_meta:
        meta[key] = key_meta
    else:
        meta.pop(key, None)
    if meta:
        variables[META_KEY] = meta
    else:
        variables.pop(META_KEY, None)
    return variables


def purge_expired(variables: dict) -> tuple[dict, list[str]]:
    """Remove all variables whose TTL has expired. Returns (updated_vars, removed_keys)."""
    removed = [
        k for k in list(variables.keys())
        if k != META_KEY and is_expired(variables, k)
    ]
    updated = dict(variables)
    for k in removed:
        updated.pop(k, None)
        updated = remove_ttl(updated, k)
    return updated, removed
