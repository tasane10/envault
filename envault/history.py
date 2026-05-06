"""Variable history tracking — records value changes over time per key."""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any

ENVAULT_HOME = Path.home() / ".envault"
MAX_HISTORY_ENTRIES = 50


def get_history_path(profile: str = "default") -> Path:
    """Return the path to the history JSON file for a profile."""
    return ENVAULT_HOME / "profiles" / profile / "history.json"


def _load_raw(profile: str = "default") -> dict[str, list[dict[str, Any]]]:
    import json

    path = get_history_path(profile)
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text())
    except Exception:
        return {}


def _save_raw(data: dict[str, list[dict[str, Any]]], profile: str = "default") -> None:
    import json

    path = get_history_path(profile)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2))


def record_change(
    key: str,
    new_value: str,
    old_value: str | None = None,
    profile: str = "default",
    actor: str = "cli",
) -> dict[str, Any]:
    """Append a change entry for *key* and return the entry."""
    data = _load_raw(profile)
    entries: list[dict[str, Any]] = data.get(key, [])

    entry: dict[str, Any] = {
        "timestamp": time.time(),
        "new_value": new_value,
        "actor": actor,
    }
    if old_value is not None:
        entry["old_value"] = old_value

    entries.append(entry)
    # Keep only the most recent MAX_HISTORY_ENTRIES entries
    data[key] = entries[-MAX_HISTORY_ENTRIES:]
    _save_raw(data, profile)
    return entry


def get_history(
    key: str, profile: str = "default", limit: int = 10
) -> list[dict[str, Any]]:
    """Return the most recent *limit* history entries for *key*."""
    data = _load_raw(profile)
    entries = data.get(key, [])
    return entries[-limit:]


def clear_history(key: str | None = None, profile: str = "default") -> int:
    """Clear history for *key* (or all keys if None). Returns number of entries removed."""
    data = _load_raw(profile)
    if key is not None:
        removed = len(data.pop(key, []))
    else:
        removed = sum(len(v) for v in data.values())
        data = {}
    _save_raw(data, profile)
    return removed


def list_tracked_keys(profile: str = "default") -> list[str]:
    """Return sorted list of keys that have history entries."""
    return sorted(_load_raw(profile).keys())
