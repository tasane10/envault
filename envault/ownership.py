"""Ownership tracking for vault variables."""

from __future__ import annotations

from typing import Dict, List, Optional

_META_PREFIX = "__"


def _is_meta(key: str) -> bool:
    return key.startswith(_META_PREFIX)


def get_owner(variables: Dict, key: str) -> Optional[str]:
    """Return the owner of *key*, or None if unset."""
    meta = variables.get("__meta", {})
    return meta.get("ownership", {}).get(key)


def set_owner(variables: Dict, key: str, owner: str) -> Dict:
    """Return a new variables dict with *owner* assigned to *key*."""
    if key not in variables or _is_meta(key):
        raise KeyError(f"Variable '{key}' does not exist.")
    if not owner or not owner.strip():
        raise ValueError("Owner must be a non-empty string.")
    updated = {**variables}
    meta = dict(updated.get("__meta", {}))
    ownership = dict(meta.get("ownership", {}))
    ownership[key] = owner.strip()
    meta["ownership"] = ownership
    updated["__meta"] = meta
    return updated


def remove_owner(variables: Dict, key: str) -> Dict:
    """Return a new variables dict with ownership removed from *key*."""
    updated = {**variables}
    meta = dict(updated.get("__meta", {}))
    ownership = dict(meta.get("ownership", {}))
    ownership.pop(key, None)
    meta["ownership"] = ownership
    updated["__meta"] = meta
    return updated


def list_owners(variables: Dict) -> Dict[str, str]:
    """Return a mapping of key -> owner for all owned variables."""
    meta = variables.get("__meta", {})
    ownership = meta.get("ownership", {})
    return {k: v for k, v in sorted(ownership.items()) if k in variables}


def filter_by_owner(variables: Dict, owner: str) -> List[str]:
    """Return sorted list of keys owned by *owner*."""
    meta = variables.get("__meta", {})
    ownership = meta.get("ownership", {})
    return sorted(
        k for k, v in ownership.items()
        if v == owner and k in variables and not _is_meta(k)
    )
