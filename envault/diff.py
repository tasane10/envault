"""Diff utilities for comparing vault profiles or env files."""

from typing import Dict, Tuple


def diff_variables(
    base: Dict[str, str],
    target: Dict[str, str],
) -> Dict[str, Tuple[str, str]]:
    """Compare two variable dicts.

    Returns a dict keyed by variable name with tuples of
    (base_value, target_value). A value of None means the key
    is absent in that side.
    """
    all_keys = set(base) | set(target)
    result: Dict[str, Tuple[str, str]] = {}
    for key in sorted(all_keys):
        base_val = base.get(key)
        target_val = target.get(key)
        if base_val != target_val:
            result[key] = (base_val, target_val)
    return result


def format_diff(diff: Dict[str, Tuple[str, str]], show_values: bool = False) -> str:
    """Format a diff dict into a human-readable string.

    Args:
        diff: Output of diff_variables.
        show_values: If True, show actual values; otherwise mask them.
    """
    if not diff:
        return "No differences found."

    lines = []
    for key, (base_val, target_val) in diff.items():
        if base_val is None:
            indicator = "+"
            value_display = target_val if show_values else "***"
            lines.append(f"  {indicator} {key}={value_display}  (added)")
        elif target_val is None:
            indicator = "-"
            value_display = base_val if show_values else "***"
            lines.append(f"  {indicator} {key}={value_display}  (removed)")
        else:
            if show_values:
                lines.append(f"  ~ {key}: {base_val!r} -> {target_val!r}  (changed)")
            else:
                lines.append(f"  ~ {key}  (changed)")
    return "\n".join(lines)
