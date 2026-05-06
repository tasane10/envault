"""Group-related operations for envault variables."""
from __future__ import annotations

META_KEY = "__meta__"
GROUP_META_KEY = "groups"


def get_groups(variables: dict) -> dict[str, list[str]]:
    """Return a mapping of group_name -> [key, ...] from variables metadata."""
    meta = variables.get(META_KEY, {})
    return dict(meta.get(GROUP_META_KEY, {}))


def set_group(variables: dict, key: str, group: str) -> dict:
    """Assign *key* to *group*. Returns a new variables dict (no mutation)."""
    if key not in variables or key == META_KEY:
        raise KeyError(f"Variable '{key}' does not exist.")
    variables = dict(variables)
    meta = dict(variables.get(META_KEY, {}))
    groups: dict[str, list[str]] = dict(meta.get(GROUP_META_KEY, {}))
    # Remove key from any existing group first
    groups = {g: [k for k in keys if k != key] for g, keys in groups.items()}
    # Add to new group (sorted, unique)
    existing = groups.get(group, [])
    if key not in existing:
        existing = sorted(existing + [key])
    groups[group] = existing
    # Prune empty groups
    groups = {g: keys for g, keys in groups.items() if keys}
    meta[GROUP_META_KEY] = groups
    variables[META_KEY] = meta
    return variables


def remove_from_group(variables: dict, key: str, group: str) -> dict:
    """Remove *key* from *group*. Returns a new variables dict."""
    variables = dict(variables)
    meta = dict(variables.get(META_KEY, {}))
    groups: dict[str, list[str]] = dict(meta.get(GROUP_META_KEY, {}))
    keys = [k for k in groups.get(group, []) if k != key]
    if keys:
        groups[group] = keys
    else:
        groups.pop(group, None)
    meta[GROUP_META_KEY] = groups
    variables[META_KEY] = meta
    return variables


def filter_by_group(variables: dict, group: str) -> dict:
    """Return only the key/value pairs that belong to *group*."""
    groups = get_groups(variables)
    keys = set(groups.get(group, []))
    return {k: v for k, v in variables.items() if k in keys}


def list_groups(variables: dict) -> list[str]:
    """Return sorted list of group names present in *variables*."""
    return sorted(get_groups(variables).keys())
