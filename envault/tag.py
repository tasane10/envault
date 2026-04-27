"""Tag management for environment variables — assign, query, and filter by tags."""

from typing import Dict, List, Optional
from envault.profiles import load_profile, save_profile

TAGS_META_KEY = "__tags__"


def get_tags(variables: Dict[str, str], var_name: str) -> List[str]:
    """Return the list of tags for a given variable name."""
    raw = variables.get(TAGS_META_KEY, "")
    if not raw:
        return []
    import json
    try:
        tag_map: Dict[str, List[str]] = json.loads(raw)
    except (ValueError, TypeError):
        return []
    return tag_map.get(var_name, [])


def set_tags(
    variables: Dict[str, str], var_name: str, tags: List[str]
) -> Dict[str, str]:
    """Set tags for a variable, returning the updated variables dict."""
    import json
    raw = variables.get(TAGS_META_KEY, "")
    try:
        tag_map: Dict[str, List[str]] = json.loads(raw) if raw else {}
    except (ValueError, TypeError):
        tag_map = {}
    if tags:
        tag_map[var_name] = sorted(set(tags))
    else:
        tag_map.pop(var_name, None)
    updated = dict(variables)
    updated[TAGS_META_KEY] = json.dumps(tag_map)
    return updated


def remove_tags(
    variables: Dict[str, str], var_name: str, tags: Optional[List[str]] = None
) -> Dict[str, str]:
    """Remove specific tags (or all tags) from a variable."""
    existing = get_tags(variables, var_name)
    if tags is None:
        remaining: List[str] = []
    else:
        remaining = [t for t in existing if t not in tags]
    return set_tags(variables, var_name, remaining)


def filter_by_tag(variables: Dict[str, str], tag: str) -> Dict[str, str]:
    """Return a dict of variable_name -> value for all vars that carry *tag*."""
    import json
    raw = variables.get(TAGS_META_KEY, "")
    try:
        tag_map: Dict[str, List[str]] = json.loads(raw) if raw else {}
    except (ValueError, TypeError):
        tag_map = {}
    return {
        k: v
        for k, v in variables.items()
        if k != TAGS_META_KEY and tag in tag_map.get(k, [])
    }


def tag_variable(
    password: str, var_name: str, tags: List[str], profile: str = "default"
) -> List[str]:
    """Persist new tags for *var_name* in *profile*; returns final tag list."""
    variables = load_profile(profile, password)
    if var_name not in variables and var_name != TAGS_META_KEY:
        raise KeyError(f"Variable '{var_name}' not found in profile '{profile}'.")
    updated = set_tags(variables, var_name, tags)
    save_profile(profile, updated, password)
    return get_tags(updated, var_name)
