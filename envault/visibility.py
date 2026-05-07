"""Variable visibility control: mark variables as public, private, or secret."""

from typing import Dict, Any

VALID_LEVELS = ("public", "private", "secret")
_META_KEY = "__meta_visibility__"


def _is_meta(key: str) -> bool:
    return key.startswith("__") and key.endswith("__")


def get_visibility(variables: Dict[str, Any]) -> Dict[str, str]:
    """Return a copy of the visibility mapping from metadata."""
    meta = variables.get(_META_KEY, {})
    return dict(meta)


def set_visibility(variables: Dict[str, Any], key: str, level: str) -> Dict[str, Any]:
    """Return a new variables dict with visibility level set for key."""
    if _is_meta(key):
        raise ValueError(f"Cannot set visibility on metadata key: {key!r}")
    if key not in variables:
        raise KeyError(f"Variable {key!r} does not exist")
    if level not in VALID_LEVELS:
        raise ValueError(f"Invalid visibility level {level!r}. Must be one of {VALID_LEVELS}")
    updated = dict(variables)
    meta = dict(updated.get(_META_KEY, {}))
    meta[key] = level
    updated[_META_KEY] = meta
    return updated


def remove_visibility(variables: Dict[str, Any], key: str) -> Dict[str, Any]:
    """Return a new variables dict with visibility entry removed for key."""
    updated = dict(variables)
    meta = dict(updated.get(_META_KEY, {}))
    meta.pop(key, None)
    updated[_META_KEY] = meta
    return updated


def get_level(variables: Dict[str, Any], key: str) -> str:
    """Return the visibility level for a key, defaulting to 'private'."""
    return variables.get(_META_KEY, {}).get(key, "private")


def filter_by_visibility(variables: Dict[str, Any], level: str) -> Dict[str, str]:
    """Return only variable key/value pairs that match the given visibility level."""
    if level not in VALID_LEVELS:
        raise ValueError(f"Invalid visibility level {level!r}")
    vis = get_visibility(variables)
    result = {}
    for k, v in variables.items():
        if _is_meta(k):
            continue
        effective = vis.get(k, "private")
        if effective == level:
            result[k] = v
    return result


def list_visibility(variables: Dict[str, Any]) -> Dict[str, str]:
    """Return visibility level for every non-meta variable."""
    vis = get_visibility(variables)
    return {
        k: vis.get(k, "private")
        for k in sorted(variables)
        if not _is_meta(k)
    }
