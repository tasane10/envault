"""Watch a vault profile for changes and trigger shell reload hooks."""

import hashlib
import json
import time
from pathlib import Path
from typing import Callable, Optional

from envault.profiles import get_profile_vault_path, load_profile


def _vault_checksum(profile: str, password: str) -> Optional[str]:
    """Return an MD5 hex digest of the sorted vault contents, or None on error."""
    try:
        variables = load_profile(profile, password)
        serialised = json.dumps(variables, sort_keys=True).encode()
        return hashlib.md5(serialised).hexdigest()
    except Exception:
        return None


def watch_profile(
    profile: str,
    password: str,
    interval: float = 2.0,
    on_change: Optional[Callable[[str, dict], None]] = None,
    max_iterations: Optional[int] = None,
) -> None:
    """Poll the vault for *profile* every *interval* seconds.

    When a change is detected *on_change(profile, new_variables)* is called.
    Pass *max_iterations* to limit the loop (useful for testing).
    """
    last_checksum = _vault_checksum(profile, password)
    iterations = 0

    while True:
        if max_iterations is not None and iterations >= max_iterations:
            break
        time.sleep(interval)
        current_checksum = _vault_checksum(profile, password)
        if current_checksum is not None and current_checksum != last_checksum:
            last_checksum = current_checksum
            if on_change is not None:
                try:
                    variables = load_profile(profile, password)
                    on_change(profile, variables)
                except Exception:
                    pass
        iterations += 1


def get_changed_keys(old: dict, new: dict) -> dict:
    """Return a summary of keys that were added, removed, or changed."""
    old_vars = {k: v for k, v in old.items() if not k.startswith("__")}
    new_vars = {k: v for k, v in new.items() if not k.startswith("__")}
    added = sorted(set(new_vars) - set(old_vars))
    removed = sorted(set(old_vars) - set(new_vars))
    changed = sorted(
        k for k in set(old_vars) & set(new_vars) if old_vars[k] != new_vars[k]
    )
    return {"added": added, "removed": removed, "changed": changed}
