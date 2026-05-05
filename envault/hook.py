"""Git-style hooks for envault lifecycle events."""

from __future__ import annotations

import os
import stat
import subprocess
from pathlib import Path

HOOK_EVENTS = (
    "pre-set",
    "post-set",
    "pre-delete",
    "post-delete",
    "post-import",
    "post-rotate",
)


def get_hooks_dir(profile: str = "default") -> Path:
    """Return the hooks directory for a given profile."""
    base = Path(os.environ.get("ENVAULT_HOME", Path.home() / ".envault"))
    return base / "hooks" / profile


def get_hook_path(event: str, profile: str = "default") -> Path:
    """Return the path for a specific hook script."""
    return get_hooks_dir(profile) / event


def install_hook(event: str, script: str, profile: str = "default") -> Path:
    """Write a hook script and make it executable."""
    if event not in HOOK_EVENTS:
        raise ValueError(f"Unknown hook event '{event}'. Valid events: {HOOK_EVENTS}")
    hook_path = get_hook_path(event, profile)
    hook_path.parent.mkdir(parents=True, exist_ok=True)
    hook_path.write_text(script)
    hook_path.chmod(hook_path.stat().st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)
    return hook_path


def remove_hook(event: str, profile: str = "default") -> bool:
    """Remove a hook script. Returns True if removed, False if not found."""
    hook_path = get_hook_path(event, profile)
    if hook_path.exists():
        hook_path.unlink()
        return True
    return False


def list_hooks(profile: str = "default") -> list[str]:
    """Return the names of installed hooks for a profile."""
    hooks_dir = get_hooks_dir(profile)
    if not hooks_dir.exists():
        return []
    return sorted(
        p.name for p in hooks_dir.iterdir()
        if p.is_file() and p.name in HOOK_EVENTS
    )


def run_hook(event: str, env_vars: dict[str, str] | None = None, profile: str = "default") -> int | None:
    """Run a hook script if it exists. Returns exit code or None if no hook."""
    hook_path = get_hook_path(event, profile)
    if not hook_path.exists():
        return None
    env = {**os.environ, **(env_vars or {})}
    result = subprocess.run([str(hook_path)], env=env, check=False)
    return result.returncode
