"""Quota management: enforce limits on number of variables per profile."""

from __future__ import annotations

from typing import Dict, Any, Optional

META_KEY = "__quota__"
DEFAULT_LIMIT = 100


def get_quota(variables: Dict[str, Any]) -> Optional[int]:
    """Return the quota limit stored in variables metadata, or None if unset."""
    meta = variables.get(META_KEY)
    if isinstance(meta, dict):
        return meta.get("limit")
    return None


def set_quota(variables: Dict[str, Any], limit: int) -> Dict[str, Any]:
    """Return a new variables dict with the quota limit set."""
    if limit < 1:
        raise ValueError("Quota limit must be a positive integer.")
    updated = dict(variables)
    updated[META_KEY] = {"limit": limit}
    return updated


def remove_quota(variables: Dict[str, Any]) -> Dict[str, Any]:
    """Return a new variables dict with the quota metadata removed."""
    return {k: v for k, v in variables.items() if k != META_KEY}


def count_variables(variables: Dict[str, Any]) -> int:
    """Count non-metadata variables."""
    return sum(1 for k in variables if not k.startswith("__"))


def check_quota(variables: Dict[str, Any], new_keys: int = 1) -> Dict[str, Any]:
    """Check whether adding *new_keys* variables would exceed the quota.

    Returns a dict with keys: ``allowed`` (bool), ``current`` (int),
    ``limit`` (int | None), ``remaining`` (int | None).
    """
    current = count_variables(variables)
    limit = get_quota(variables)
    if limit is None:
        return {"allowed": True, "current": current, "limit": None, "remaining": None}
    remaining = limit - current
    allowed = (current + new_keys) <= limit
    return {"allowed": allowed, "current": current, "limit": limit, "remaining": remaining}
