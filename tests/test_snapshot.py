"""Tests for envault.snapshot and snapshot_cli."""

import json
import pytest
from click.testing import CliRunner
from unittest.mock import patch
from pathlib import Path

from envault.snapshot import (
    create_snapshot,
    list_snapshots,
    restore_snapshot,
    delete_snapshot,
    get_snapshot_dir,
)
from envault.snapshot_cli import snapshot_cmd

PASSWORD = "test-secret"
PROFILE = "snap_test"


@pytest.fixture()
def mock_vault(tmp_path, monkeypatch):
    """Patch profile functions to use a temp directory."""
    vault_file = tmp_path / "profiles" / PROFILE / "vault.enc"

    def _get_path(profile=PROFILE):
        return tmp_path / "profiles" / profile / "vault.enc"

    def _load(password, profile=PROFILE):
        from envault.storage import load_vault
        return load_vault(_get_path(profile), password)

    def _save(variables, password, profile=PROFILE):
        from envault.storage import save_vault
        path = _get_path(profile)
        path.parent.mkdir(parents=True, exist_ok=True)
        save_vault(path, variables, password)

    monkeypatch.setattr("envault.snapshot.get_profile_vault_path", _get_path)
    monkeypatch.setattr("envault.snapshot.load_profile", _load)
    monkeypatch.setattr("envault.snapshot.save_profile", _save)
    return tmp_path


def _seed_vault(mock_vault, variables):
    from envault.storage import save_vault
    path = mock_vault / "profiles" / PROFILE / "vault.enc"
    path.parent.mkdir(parents=True, exist_ok=True)
    save_vault(path, variables, PASSWORD)


def test_create_snapshot_saves_file(mock_vault):
    _seed_vault(mock_vault, {"KEY": "value"})
    meta = create_snapshot(PASSWORD, profile=PROFILE, label="v1")
    assert meta["id"] == "v1"
    assert meta["key_count"] == 1
    snap_file = get_snapshot_dir(PROFILE) / "v1.json"
    assert snap_file.exists()


def test_create_snapshot_uses_timestamp_when_no_label(mock_vault):
    _seed_vault(mock_vault, {"A": "1", "B": "2"})
    meta = create_snapshot(PASSWORD, profile=PROFILE)
    assert meta["key_count"] == 2
    assert meta["id"].isdigit()


def test_list_snapshots_returns_newest_first(mock_vault):
    _seed_vault(mock_vault, {"X": "y"})
    create_snapshot(PASSWORD, profile=PROFILE, label="snap_a")
    create_snapshot(PASSWORD, profile=PROFILE, label="snap_b")
    snaps = list_snapshots(profile=PROFILE)
    assert len(snaps) == 2
    ids = [s["id"] for s in snaps]
    assert "snap_a" in ids and "snap_b" in ids


def test_list_snapshots_empty_when_none(mock_vault):
    assert list_snapshots(profile=PROFILE) == []


def test_restore_snapshot_overwrites_vault(mock_vault):
    _seed_vault(mock_vault, {"ORIGINAL": "yes"})
    create_snapshot(PASSWORD, profile=PROFILE, label="before")
    _seed_vault(mock_vault, {"MODIFIED": "no"})
    restored = restore_snapshot("before", PASSWORD, profile=PROFILE)
    assert restored == {"ORIGINAL": "yes"}


def test_restore_snapshot_missing_raises(mock_vault):
    with pytest.raises(FileNotFoundError):
        restore_snapshot("ghost", PASSWORD, profile=PROFILE)


def test_delete_snapshot_removes_file(mock_vault):
    _seed_vault(mock_vault, {"K": "v"})
    create_snapshot(PASSWORD, profile=PROFILE, label="to_delete")
    assert delete_snapshot("to_delete", profile=PROFILE) is True
    assert not (get_snapshot_dir(PROFILE) / "to_delete.json").exists()


def test_delete_snapshot_returns_false_when_missing(mock_vault):
    assert delete_snapshot("nonexistent", profile=PROFILE) is False
