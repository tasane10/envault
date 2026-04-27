"""Audit log for tracking vault operations."""

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


DEFAULT_AUDIT_DIR = Path.home() / ".envault" / "audit"


def get_audit_log_path(profile: str = "default", audit_dir: Optional[Path] = None) -> Path:
    """Return the path to the audit log file for a given profile."""
    base = audit_dir if audit_dir is not None else DEFAULT_AUDIT_DIR
    return base / f"{profile}.jsonl"


def record_event(
    action: str,
    key: str,
    profile: str = "default",
    audit_dir: Optional[Path] = None,
    actor: Optional[str] = None,
) -> dict:
    """Append an audit event to the log and return the event dict."""
    event = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "action": action,
        "key": key,
        "profile": profile,
        "actor": actor or os.environ.get("USER", "unknown"),
    }
    log_path = get_audit_log_path(profile, audit_dir)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(event) + "\n")
    return event


def read_events(profile: str = "default", audit_dir: Optional[Path] = None) -> list:
    """Read all audit events for a given profile."""
    log_path = get_audit_log_path(profile, audit_dir)
    if not log_path.exists():
        return []
    events = []
    with log_path.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                events.append(json.loads(line))
    return events


def clear_events(profile: str = "default", audit_dir: Optional[Path] = None) -> int:
    """Delete the audit log for a profile. Returns number of events cleared."""
    log_path = get_audit_log_path(profile, audit_dir)
    if not log_path.exists():
        return 0
    events = read_events(profile, audit_dir)
    log_path.unlink()
    return len(events)
