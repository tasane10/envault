"""Shareable export: generate and consume one-time encrypted share bundles."""

from __future__ import annotations

import json
import os
import secrets
import time
from typing import Optional

from envault.crypto import encrypt, decrypt


def generate_share_token() -> str:
    """Return a cryptographically random 32-char hex token."""
    return secrets.token_hex(16)


def create_share_bundle(
    variables: dict[str, str],
    password: str,
    ttl_seconds: Optional[int] = None,
    keys: Optional[list[str]] = None,
) -> dict:
    """Encrypt a subset (or all) of *variables* into a portable share bundle.

    Args:
        variables: The full variable mapping (excluding metadata keys).
        password:  Encryption password for the bundle.
        ttl_seconds: Optional lifetime in seconds from now.
        keys: Whitelist of keys to include. None means include all.

    Returns:
        A dict with ``token``, ``payload``, and optional ``expires_at``.
    """
    subset = {
        k: v
        for k, v in variables.items()
        if not k.startswith("__") and (keys is None or k in keys)
    }
    plaintext = json.dumps(subset)
    payload = encrypt(plaintext, password)
    bundle: dict = {
        "token": generate_share_token(),
        "payload": payload,
        "created_at": int(time.time()),
    }
    if ttl_seconds is not None:
        bundle["expires_at"] = bundle["created_at"] + ttl_seconds
    return bundle


def open_share_bundle(bundle: dict, password: str) -> dict[str, str]:
    """Decrypt a share bundle and return the variable mapping.

    Raises:
        ValueError: If the bundle has expired or decryption fails.
    """
    expires_at = bundle.get("expires_at")
    if expires_at is not None and int(time.time()) > expires_at:
        raise ValueError("Share bundle has expired.")
    plaintext = decrypt(bundle["payload"], password)
    return json.loads(plaintext)


def bundle_to_file(bundle: dict, path: str) -> None:
    """Serialise *bundle* to a JSON file at *path*."""
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(bundle, fh, indent=2)


def bundle_from_file(path: str) -> dict:
    """Load a share bundle from a JSON file."""
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)
