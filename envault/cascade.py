"""Cascade variable resolution across multiple profiles in priority order."""

from typing import Dict, List, Optional, Tuple

META_PREFIX = "__"


def _is_meta(key: str) -> bool:
    return key.startswith(META_PREFIX)


def resolve_cascade(
    profiles: List[str],
    loaded: Dict[str, Dict[str, str]],
) -> Dict[str, str]:
    """Merge variables from multiple profiles in priority order.

    The first profile in the list has the highest priority.
    Meta keys are excluded from the result.

    Args:
        profiles: Ordered list of profile names (highest priority first).
        loaded: Mapping of profile name -> variable dict.

    Returns:
        Merged dict of variables.
    """
    merged: Dict[str, str] = {}
    for profile in reversed(profiles):
        variables = loaded.get(profile, {})
        for key, value in variables.items():
            if not _is_meta(key):
                merged[key] = value
    return merged


def explain_cascade(
    profiles: List[str],
    loaded: Dict[str, Dict[str, str]],
) -> Dict[str, Tuple[str, str]]:
    """Return the origin profile for each resolved key.

    Args:
        profiles: Ordered list of profile names (highest priority first).
        loaded: Mapping of profile name -> variable dict.

    Returns:
        Dict mapping key -> (value, source_profile).
    """
    result: Dict[str, Tuple[str, str]] = {}
    # Walk highest-priority first so later iterations override
    for profile in profiles:
        variables = loaded.get(profile, {})
        for key, value in variables.items():
            if not _is_meta(key):
                result[key] = (value, profile)
    return result


def list_overrides(
    profiles: List[str],
    loaded: Dict[str, Dict[str, str]],
) -> List[Dict[str, str]]:
    """List keys that are overridden by a higher-priority profile.

    Returns:
        List of dicts with keys: key, overriding_profile, overridden_profile, value.
    """
    overrides = []
    seen: Dict[str, str] = {}  # key -> first (highest priority) profile that defines it

    for profile in profiles:
        variables = loaded.get(profile, {})
        for key in variables:
            if _is_meta(key):
                continue
            if key in seen:
                overrides.append({
                    "key": key,
                    "overriding_profile": seen[key],
                    "overridden_profile": profile,
                    "value": loaded[seen[key]][key],
                })
            else:
                seen[key] = profile

    return overrides
