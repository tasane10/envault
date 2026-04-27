"""Tests for envault/lock.py — file-based vault locking."""

import os
import time
import pytest
from pathlib import Path
from unittest.mock import patch

from envault.lock import (
    get_lock_path,
    acquire_lock,
    release_lock,
    is_locked,
    _read_lock_pid,
)


@pytest.fixture
def vault_file(tmp_path):
    """Return a temporary vault file path."""
    return tmp_path / "test.vault"


def test_get_lock_path_has_lock_suffix(vault_file):
    lock_path = get_lock_path(vault_file)
    assert str(lock_path).endswith(".lock")


def test_get_lock_path_is_sibling_of_vault(vault_file):
    lock_path = get_lock_path(vault_file)
    assert lock_path.parent == vault_file.parent


def test_acquire_lock_creates_lock_file(vault_file):
    lock_path = get_lock_path(vault_file)
    assert not lock_path.exists()
    acquire_lock(vault_file)
    assert lock_path.exists()
    release_lock(vault_file)


def test_acquire_lock_writes_pid(vault_file):
    acquire_lock(vault_file)
    pid = _read_lock_pid(vault_file)
    assert pid == os.getpid()
    release_lock(vault_file)


def test_release_lock_removes_file(vault_file):
    acquire_lock(vault_file)
    assert get_lock_path(vault_file).exists()
    release_lock(vault_file)
    assert not get_lock_path(vault_file).exists()


def test_release_lock_no_op_when_not_locked(vault_file):
    """release_lock should not raise if no lock file exists."""
    release_lock(vault_file)  # should not raise


def test_is_locked_false_when_no_lock_file(vault_file):
    assert not is_locked(vault_file)


def test_is_locked_true_after_acquire(vault_file):
    acquire_lock(vault_file)
    assert is_locked(vault_file)
    release_lock(vault_file)


def test_is_locked_false_after_release(vault_file):
    acquire_lock(vault_file)
    release_lock(vault_file)
    assert not is_locked(vault_file)


def test_acquire_lock_raises_if_already_locked_by_other_pid(vault_file):
    """If the lock file contains a different (fake) PID, acquire should raise."""
    lock_path = get_lock_path(vault_file)
    # Write a fake PID that is not our own
    fake_pid = os.getpid() + 9999
    lock_path.write_text(str(fake_pid))
    with pytest.raises(RuntimeError, match="locked"):
        acquire_lock(vault_file)
    lock_path.unlink()  # cleanup


def test_acquire_lock_reclaims_stale_lock(vault_file):
    """If the PID in the lock file no longer exists, acquire should succeed."""
    lock_path = get_lock_path(vault_file)
    # Use PID 0 — never a real running user process
    lock_path.write_text("99999999")
    # Patch os.kill to simulate that the process does not exist
    with patch("envault.lock.os.kill", side_effect=ProcessLookupError):
        acquire_lock(vault_file)  # should not raise
    assert _read_lock_pid(vault_file) == os.getpid()
    release_lock(vault_file)
