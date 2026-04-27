"""Snapshot management: save and restore vault state at a point in time."""

import json
import time
from pathlib import Path
from typing import Optional

from envault.profiles import get_profile_vault_path, load_profile, save_profile


def get_snapshot_dir(profile: str = "default") -> Path:
    """Return the directory where snapshots for a profile are stored."""
    vault_path = get_profile_vault_path(profile)
    return vault_path.parent / "snapshots"


def create_snapshot(
    password: str,
    profile: str = "default",
    label: Optional[str] = None,
) -> dict:
    """Save the current vault state as a named snapshot.

    Returns metadata dict for the created snapshot.
    """
    variables = load_profile(password, profile)
    timestamp = int(time.time())
    snapshot_id = label if label else str(timestamp)

    snapshot_dir = get_snapshot_dir(profile)
    snapshot_dir.mkdir(parents=True, exist_ok=True)

    snapshot_file = snapshot_dir / f"{snapshot_id}.json"
    meta = {
        "id": snapshot_id,
        "profile": profile,
        "timestamp": timestamp,
        "key_count": len(variables),
    }
    payload = {"meta": meta, "variables": variables}
    snapshot_file.write_text(json.dumps(payload, indent=2))
    return meta


def list_snapshots(profile: str = "default") -> list[dict]:
    """Return metadata for all snapshots of a profile, newest first."""
    snapshot_dir = get_snapshot_dir(profile)
    if not snapshot_dir.exists():
        return []
    metas = []
    for f in sorted(snapshot_dir.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True):
        try:
            payload = json.loads(f.read_text())
            metas.append(payload["meta"])
        except (json.JSONDecodeError, KeyError):
            continue
    return metas


def restore_snapshot(
    snapshot_id: str,
    password: str,
    profile: str = "default",
) -> dict:
    """Restore vault from a snapshot. Returns the restored variables dict."""
    snapshot_dir = get_snapshot_dir(profile)
    snapshot_file = snapshot_dir / f"{snapshot_id}.json"
    if not snapshot_file.exists():
        raise FileNotFoundError(f"Snapshot '{snapshot_id}' not found for profile '{profile}'.")
    payload = json.loads(snapshot_file.read_text())
    variables = payload["variables"]
    save_profile(variables, password, profile)
    return variables


def delete_snapshot(snapshot_id: str, profile: str = "default") -> bool:
    """Delete a snapshot by id. Returns True if deleted, False if not found."""
    snapshot_file = get_snapshot_dir(profile) / f"{snapshot_id}.json"
    if not snapshot_file.exists():
        return False
    snapshot_file.unlink()
    return True
