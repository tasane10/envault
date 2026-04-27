"""Tests for envault.lock."""

import os
import time
from pathlib import Path

import pytest

from envault.lock import (
    acquire_lock,
    get_lock_path,
    is_locked,
    release_lock,
    _clear_stale_lock,
)


@pytest.fixture
def vault_file(tmp_path: Path) -> Path:
    v = tmp_path / "vault.enc"
    v.write_text("dummy")
    return v


def test_get_lock_path_has_lock_suffix(vault_file: Path) -> None:
    lock = get_lock_path(vault_file)
    assert lock.suffix == ".lock"
    assert lock.stem == vault_file.stem


def test_acquire_lock_creates_lock_file(vault_file: Path) -> None:
    acquired = acquire_lock(vault_file)
    assert acquired is True
    assert get_lock_path(vault_file).exists()
    release_lock(vault_file)


def test_acquire_lock_writes_pid(vault_file: Path) -> None:
    acquire_lock(vault_file)
    lock_path = get_lock_path(vault_file)
    pid = int(lock_path.read_text().strip())
    assert pid == os.getpid()
    release_lock(vault_file)


def test_release_lock_removes_file(vault_file: Path) -> None:
    acquire_lock(vault_file)
    release_lock(vault_file)
    assert not get_lock_path(vault_file).exists()


def test_release_lock_noop_when_not_held(vault_file: Path) -> None:
    # Should not raise even if no lock exists
    release_lock(vault_file)


def test_is_locked_true_after_acquire(vault_file: Path) -> None:
    acquire_lock(vault_file)
    assert is_locked(vault_file) is True
    release_lock(vault_file)


def test_is_locked_false_after_release(vault_file: Path) -> None:
    acquire_lock(vault_file)
    release_lock(vault_file)
    assert is_locked(vault_file) is False


def test_acquire_lock_times_out_when_already_locked(vault_file: Path) -> None:
    lock_path = get_lock_path(vault_file)
    # Manually create a lock file owned by a fake PID
    lock_path.write_text("99999999")
    result = acquire_lock(vault_file, timeout=0)
    assert result is False
    lock_path.unlink(missing_ok=True)


def test_clear_stale_lock_removes_old_file(vault_file: Path) -> None:
    lock_path = get_lock_path(vault_file)
    lock_path.write_text("12345")
    # Back-date the file modification time
    old_time = time.time() - 120
    os.utime(lock_path, (old_time, old_time))
    _clear_stale_lock(lock_path, stale_after=60)
    assert not lock_path.exists()


def test_clear_stale_lock_keeps_fresh_file(vault_file: Path) -> None:
    lock_path = get_lock_path(vault_file)
    lock_path.write_text("12345")
    _clear_stale_lock(lock_path, stale_after=60)
    assert lock_path.exists()
    lock_path.unlink()
