"""Search and filter environment variables across profiles."""

from typing import Optional
from envault.profiles import list_profiles, load_profile


def search_variables(
    pattern: str,
    password: str,
    profile: Optional[str] = None,
    keys_only: bool = False,
    values_only: bool = False,
) -> dict[str, dict[str, str]]:
    """Search for variables matching a pattern across one or all profiles.

    Returns a dict mapping profile_name -> {key: value} for matches.
    """
    import re

    try:
        regex = re.compile(pattern, re.IGNORECASE)
    except re.error as exc:
        raise ValueError(f"Invalid search pattern: {exc}") from exc

    profiles_to_search = [profile] if profile else list_profiles()
    results: dict[str, dict[str, str]] = {}

    for prof in profiles_to_search:
        try:
            variables = load_profile(prof, password)
        except Exception:
            continue

        matches: dict[str, str] = {}
        for key, value in variables.items():
            key_match = not values_only and regex.search(key)
            value_match = not keys_only and regex.search(value)
            if key_match or value_match:
                matches[key] = value

        if matches:
            results[prof] = matches

    return results


def format_search_results(
    results: dict[str, dict[str, str]], show_values: bool = True
) -> str:
    """Format search results for display."""
    if not results:
        return "No matches found."

    lines: list[str] = []
    for profile_name, variables in results.items():
        lines.append(f"[{profile_name}]")
        for key, value in sorted(variables.items()):
            if show_values:
                lines.append(f"  {key}={value}")
            else:
                lines.append(f"  {key}")
        lines.append("")

    return "\n".join(lines).rstrip()
