"""Checksum utilities for detecting vault file tampering or drift."""

import hashlib
import json
from pathlib import Path
from typing import Optional


def _is_meta(key: str) -> bool:
    return key.startswith("__") and key.endswith("__")


def compute_variables_checksum(variables: dict) -> str:
    """Return a stable SHA-256 hex digest of the non-meta variable key/value pairs."""
    filtered = {
        k: v
        for k, v in variables.items()
        if not _is_meta(k) and isinstance(v, str)
    }
    canonical = json.dumps(filtered, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode()).hexdigest()


def get_checksum_path(vault_path: Path) -> Path:
    """Return the path to the checksum sidecar file for a given vault."""
    return vault_path.with_suffix(".checksum")


def save_checksum(vault_path: Path, checksum: str) -> None:
    """Persist a checksum string to the sidecar file."""
    path = get_checksum_path(vault_path)
    path.write_text(checksum, encoding="utf-8")


def load_checksum(vault_path: Path) -> Optional[str]:
    """Load the stored checksum from the sidecar file, or None if missing."""
    path = get_checksum_path(vault_path)
    if not path.exists():
        return None
    return path.read_text(encoding="utf-8").strip()


def verify_checksum(vault_path: Path, variables: dict) -> bool:
    """Return True if the stored checksum matches the current variables."""
    stored = load_checksum(vault_path)
    if stored is None:
        return False
    return stored == compute_variables_checksum(variables)


def update_checksum(vault_path: Path, variables: dict) -> str:
    """Recompute and persist the checksum for the given variables. Returns the digest."""
    digest = compute_variables_checksum(variables)
    save_checksum(vault_path, digest)
    return digest
