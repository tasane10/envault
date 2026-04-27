"""Tests for envault profile management."""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from envault.profiles import (
    get_profile_vault_path,
    list_profiles,
    load_profile,
    save_profile,
    copy_profile,
    delete_profile,
    DEFAULT_PROFILE,
)


@pytest.fixture
def mock_vault_base(tmp_path):
    vault_file = tmp_path / ".envault.json.enc"
    with patch("envault.profiles.get_vault_path", return_value=vault_file):
        yield tmp_path, vault_file


def test_get_profile_vault_path_default(mock_vault_base):
    tmp_path, vault_file = mock_vault_base
    result = get_profile_vault_path(DEFAULT_PROFILE)
    assert result == vault_file


def test_get_profile_vault_path_named(mock_vault_base):
    tmp_path, vault_file = mock_vault_base
    result = get_profile_vault_path("staging")
    assert result == tmp_path / ".envault_staging.json.enc"


def test_list_profiles_empty_dir(mock_vault_base):
    profiles = list_profiles()
    assert profiles == [DEFAULT_PROFILE]


def test_list_profiles_with_extra_profiles(mock_vault_base):
    tmp_path, _ = mock_vault_base
    (tmp_path / ".envault_dev.json.enc").touch()
    (tmp_path / ".envault_prod.json.enc").touch()
    profiles = list_profiles()
    assert "default" in profiles
    assert "dev" in profiles
    assert "prod" in profiles
    assert profiles == sorted(set(profiles))


def test_load_profile_delegates_to_load_vault(mock_vault_base):
    with patch("envault.profiles.load_vault", return_value={"KEY": "val"}) as mock_load:
        result = load_profile("default", "secret")
        assert result == {"KEY": "val"}
        mock_load.assert_called_once()


def test_save_profile_delegates_to_save_vault(mock_vault_base):
    with patch("envault.profiles.save_vault") as mock_save:
        save_profile("default", "secret", {"A": "1"})
        mock_save.assert_called_once()


def test_copy_profile(mock_vault_base):
    src_data = {"FOO": "bar", "BAZ": "qux"}
    dst_data = {"EXISTING": "val"}

    with patch("envault.profiles.load_profile", side_effect=[src_data, dst_data]) as mock_load, \
         patch("envault.profiles.save_profile") as mock_save:
        count = copy_profile("dev", "staging", "secret")
        assert count == 2
        saved_data = mock_save.call_args[0][2]
        assert saved_data["FOO"] == "bar"
        assert saved_data["EXISTING"] == "val"


def test_delete_profile_removes_file(mock_vault_base):
    tmp_path, _ = mock_vault_base
    profile_file = tmp_path / ".envault_test.json.enc"
    profile_file.touch()
    result = delete_profile("test")
    assert result is True
    assert not profile_file.exists()


def test_delete_profile_returns_false_if_missing(mock_vault_base):
    result = delete_profile("nonexistent")
    assert result is False


def test_delete_default_profile_raises(mock_vault_base):
    with pytest.raises(ValueError, match="Cannot delete the default profile"):
        delete_profile(DEFAULT_PROFILE)
