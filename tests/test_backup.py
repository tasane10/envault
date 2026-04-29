"""Tests for envault.backup."""

from __future__ import annotations

import json
import tarfile
from pathlib import Path
from unittest.mock import patch

import pytest

from envault.backup import create_backup, restore_backup


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _fake_vault_path(base: Path, profile: str) -> Path:
    return base / f"{profile}.json"


def _seed_vault(base: Path, profile: str, data: dict) -> Path:
    p = _fake_vault_path(base, profile)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data))
    return p


# ---------------------------------------------------------------------------
# create_backup
# ---------------------------------------------------------------------------

def test_create_backup_produces_tar_gz(tmp_path):
    vault_base = tmp_path / "vaults"
    _seed_vault(vault_base, "default", {"KEY": "val"})

    out = tmp_path / "backup.tar.gz"
    with (
        patch("envault.backup.list_profiles", return_value=["default"]),
        patch("envault.backup.get_profile_vault_path", side_effect=lambda p: _fake_vault_path(vault_base, p)),
    ):
        result = create_backup(output_path=out, profiles=["default"])

    assert result == out
    assert tarfile.is_tarfile(out)


def test_create_backup_includes_manifest(tmp_path):
    vault_base = tmp_path / "vaults"
    _seed_vault(vault_base, "default", {})
    out = tmp_path / "backup.tar.gz"

    with (
        patch("envault.backup.list_profiles", return_value=["default"]),
        patch("envault.backup.get_profile_vault_path", side_effect=lambda p: _fake_vault_path(vault_base, p)),
    ):
        create_backup(output_path=out, profiles=["default"])

    with tarfile.open(out, "r:gz") as tar:
        names = tar.getnames()
    assert "envault_backup_manifest.json" in names


def test_create_backup_raises_for_unknown_profile(tmp_path):
    with patch("envault.backup.list_profiles", return_value=["default"]):
        with pytest.raises(ValueError, match="Unknown profiles"):
            create_backup(output_path=tmp_path / "x.tar.gz", profiles=["ghost"])


def test_create_backup_skips_missing_vault_files(tmp_path):
    vault_base = tmp_path / "vaults"
    # Do NOT create the vault file — it simply should not appear in the archive.
    out = tmp_path / "backup.tar.gz"

    with (
        patch("envault.backup.list_profiles", return_value=["empty"]),
        patch("envault.backup.get_profile_vault_path", side_effect=lambda p: _fake_vault_path(vault_base, p)),
    ):
        create_backup(output_path=out, profiles=["empty"])

    with tarfile.open(out, "r:gz") as tar:
        names = tar.getnames()
    assert "vaults/empty.json" not in names


# ---------------------------------------------------------------------------
# restore_backup
# ---------------------------------------------------------------------------

def _make_archive(tmp_path: Path, profiles: dict[str, dict]) -> Path:
    """Build a minimal backup archive from a mapping of profile→data."""
    vault_base = tmp_path / "src_vaults"
    for name, data in profiles.items():
        _seed_vault(vault_base, name, data)

    out = tmp_path / "backup.tar.gz"
    with (
        patch("envault.backup.list_profiles", return_value=list(profiles)),
        patch("envault.backup.get_profile_vault_path", side_effect=lambda p: _fake_vault_path(vault_base, p)),
    ):
        create_backup(output_path=out, profiles=list(profiles))
    return out


def test_restore_backup_restores_profiles(tmp_path):
    archive = _make_archive(tmp_path, {"default": {"A": "1"}, "prod": {"B": "2"}})
    dest = tmp_path / "restored"
    summary = restore_backup(archive, dest_dir=dest)
    assert set(summary["restored"]) == {"default", "prod"}
    assert summary["skipped"] == []
    assert (dest / "default.json").exists()


def test_restore_backup_skips_existing_without_overwrite(tmp_path):
    archive = _make_archive(tmp_path, {"default": {"A": "1"}})
    dest = tmp_path / "restored"
    dest.mkdir()
    (dest / "default.json").write_text("{}")
    summary = restore_backup(archive, dest_dir=dest, overwrite=False)
    assert "default" in summary["skipped"]
    assert summary["restored"] == []


def test_restore_backup_overwrites_when_flag_set(tmp_path):
    archive = _make_archive(tmp_path, {"default": {"A": "new"}})
    dest = tmp_path / "restored"
    dest.mkdir()
    (dest / "default.json").write_text(json.dumps({"A": "old"}))
    summary = restore_backup(archive, dest_dir=dest, overwrite=True)
    assert "default" in summary["restored"]
    data = json.loads((dest / "default.json").read_text())
    assert data["A"] == "new"


def test_restore_backup_raises_when_archive_missing(tmp_path):
    with pytest.raises(FileNotFoundError):
        restore_backup(tmp_path / "nonexistent.tar.gz", dest_dir=tmp_path)
