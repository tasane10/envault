"""Pin management: lock specific variables to prevent accidental overwrite."""

from typing import Dict, Any

META_KEY = "__pin__"


def get_pinned(variables: Dict[str, Any]) -> list:
    """Return the list of pinned variable names."""
    meta = variables.get(META_KEY, {})
    return list(meta.get("keys", []))


def pin_variable(variables: Dict[str, Any], key: str) -> Dict[str, Any]:
    """Return a new variables dict with *key* added to the pinned set."""
    if key not in variables:
        raise KeyError(f"Variable '{key}' does not exist in the vault.")
    meta = dict(variables.get(META_KEY, {}))
    pinned = set(meta.get("keys", []))
    pinned.add(key)
    meta["keys"] = sorted(pinned)
    return {**variables, META_KEY: meta}


def unpin_variable(variables: Dict[str, Any], key: str) -> Dict[str, Any]:
    """Return a new variables dict with *key* removed from the pinned set."""
    meta = dict(variables.get(META_KEY, {}))
    pinned = set(meta.get("keys", []))
    pinned.discard(key)
    meta["keys"] = sorted(pinned)
    result = {**variables, META_KEY: meta}
    if not meta["keys"]:
        result.pop(META_KEY, None)
    return result


def is_pinned(variables: Dict[str, Any], key: str) -> bool:
    """Return True if *key* is pinned."""
    return key in get_pinned(variables)


def guard_pinned(variables: Dict[str, Any], key: str) -> None:
    """Raise ValueError if *key* is pinned (used before overwrite/delete)."""
    if is_pinned(variables, key):
        raise ValueError(
            f"Variable '{key}' is pinned and cannot be modified. "
            "Unpin it first with: envault pin unpin {key}"
        )
