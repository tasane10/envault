"""Local encrypted storage for envault vault files."""

import json
import os
from pathlib import Path
from typing import Dict, Optional

from envault.crypto import encrypt, decrypt

DEFAULT_VAULT_DIR = Path.home() / ".envault"
DEFAULT_VAULT_FILE = "vault.enc"


def get_vault_path(vault_dir: Optional[Path] = None) -> Path:
    """Return the path to the vault file."""
    base = vault_dir or DEFAULT_VAULT_DIR
    return base / DEFAULT_VAULT_FILE


def load_vault(password: str, vault_path: Optional[Path] = None) -> Dict[str, str]:
    """Load and decrypt the vault, returning a dict of env vars.

    Returns an empty dict if the vault file does not exist yet.
    """
    path = vault_path or get_vault_path()
    if not path.exists():
        return {}
    ciphertext = path.read_text(encoding="utf-8")
    plaintext = decrypt(ciphertext, password)
    return json.loads(plaintext)


def save_vault(
    data: Dict[str, str], password: str, vault_path: Optional[Path] = None
) -> None:
    """Encrypt and persist the vault dict to disk."""
    path = vault_path or get_vault_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    plaintext = json.dumps(data)
    ciphertext = encrypt(plaintext, password)
    path.write_text(ciphertext, encoding="utf-8")


def set_variable(
    key: str, value: str, password: str, vault_path: Optional[Path] = None
) -> None:
    """Set a single environment variable in the vault."""
    data = load_vault(password, vault_path)
    data[key] = value
    save_vault(data, password, vault_path)


def get_variable(
    key: str, password: str, vault_path: Optional[Path] = None
) -> Optional[str]:
    """Retrieve a single environment variable from the vault."""
    data = load_vault(password, vault_path)
    return data.get(key)


def delete_variable(
    key: str, password: str, vault_path: Optional[Path] = None
) -> bool:
    """Delete a variable from the vault. Returns True if it existed."""
    data = load_vault(password, vault_path)
    if key not in data:
        return False
    del data[key]
    save_vault(data, password, vault_path)
    return True
