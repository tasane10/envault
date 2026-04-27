"""Vault locking: prevent concurrent access using a lock file."""

import os
import time
from pathlib import Path
from typing import Optional

DEFAULT_LOCK_TIMEOUT = 10  # seconds
DEFAULT_LOCK_STALE = 60    # seconds before a lock is considered stale


def get_lock_path(vault_path: Path) -> Path:
    """Return the lock file path for a given vault file."""
    return vault_path.with_suffix(".lock")


def acquire_lock(vault_path: Path, timeout: int = DEFAULT_LOCK_TIMEOUT) -> bool:
    """Attempt to acquire a lock for the vault.

    Returns True if lock was acquired, False if timed out.
    """
    lock_path = get_lock_path(vault_path)
    deadline = time.monotonic() + timeout

    while time.monotonic() < deadline:
        _clear_stale_lock(lock_path)
        try:
            fd = os.open(str(lock_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            with os.fdopen(fd, "w") as f:
                f.write(str(os.getpid()))
            return True
        except FileExistsError:
            time.sleep(0.05)

    return False


def release_lock(vault_path: Path) -> None:
    """Release the lock for the vault, if held by this process."""
    lock_path = get_lock_path(vault_path)
    pid = _read_lock_pid(lock_path)
    if pid == os.getpid():
        try:
            lock_path.unlink()
        except FileNotFoundError:
            pass


def is_locked(vault_path: Path) -> bool:
    """Return True if the vault currently has a non-stale lock."""
    lock_path = get_lock_path(vault_path)
    _clear_stale_lock(lock_path)
    return lock_path.exists()


def _read_lock_pid(lock_path: Path) -> Optional[int]:
    """Read the PID stored in the lock file."""
    try:
        return int(lock_path.read_text().strip())
    except (FileNotFoundError, ValueError):
        return None


def _clear_stale_lock(lock_path: Path, stale_after: int = DEFAULT_LOCK_STALE) -> None:
    """Remove the lock file if it is older than stale_after seconds."""
    try:
        age = time.time() - lock_path.stat().st_mtime
        if age > stale_after:
            lock_path.unlink(missing_ok=True)
    except FileNotFoundError:
        pass
