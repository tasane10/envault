"""Audit-aware wrappers for storage operations."""

from pathlib import Path
from typing import Optional

from envault.storage import load_vault, save_vault
from envault.audit import record_event, DEFAULT_AUDIT_DIR


def set_variable_audited(
    vault_path: Path,
    password: str,
    key: str,
    value: str,
    profile: str = "default",
    audit_dir: Optional[Path] = None,
    actor: Optional[str] = None,
) -> None:
    """Set a variable in the vault and record a SET audit event."""
    data = load_vault(vault_path, password)
    data[key] = value
    save_vault(vault_path, password, data)
    record_event("set", key, profile=profile, audit_dir=audit_dir or DEFAULT_AUDIT_DIR, actor=actor)


def get_variable_audited(
    vault_path: Path,
    password: str,
    key: str,
    profile: str = "default",
    audit_dir: Optional[Path] = None,
    actor: Optional[str] = None,
) -> Optional[str]:
    """Get a variable from the vault and record a GET audit event."""
    data = load_vault(vault_path, password)
    value = data.get(key)
    record_event("get", key, profile=profile, audit_dir=audit_dir or DEFAULT_AUDIT_DIR, actor=actor)
    return value


def delete_variable_audited(
    vault_path: Path,
    password: str,
    key: str,
    profile: str = "default",
    audit_dir: Optional[Path] = None,
    actor: Optional[str] = None,
) -> bool:
    """Delete a variable from the vault and record a DELETE audit event."""
    data = load_vault(vault_path, password)
    existed = key in data
    if existed:
        del data[key]
        save_vault(vault_path, password, data)
    record_event(
        "delete", key, profile=profile, audit_dir=audit_dir or DEFAULT_AUDIT_DIR, actor=actor
    )
    return existed
