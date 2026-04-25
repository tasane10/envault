"""Tests for envault.storage module."""

import pytest
from pathlib import Path

from envault.storage import (
    load_vault,
    save_vault,
    set_variable,
    get_variable,
    delete_variable,
    get_vault_path,
)

PASSWORD = "super-secret-password"


@pytest.fixture()
def vault_path(tmp_path: Path) -> Path:
    return tmp_path / "test_vault.enc"


def test_load_vault_returns_empty_dict_when_missing(vault_path):
    result = load_vault(PASSWORD, vault_path)
    assert result == {}


def test_save_and_load_roundtrip(vault_path):
    data = {"API_KEY": "abc123", "DEBUG": "true"}
    save_vault(data, PASSWORD, vault_path)
    loaded = load_vault(PASSWORD, vault_path)
    assert loaded == data


def test_save_creates_parent_directories(tmp_path):
    nested_path = tmp_path / "a" / "b" / "vault.enc"
    save_vault({"X": "1"}, PASSWORD, nested_path)
    assert nested_path.exists()


def test_load_vault_wrong_password_raises(vault_path):
    save_vault({"KEY": "value"}, PASSWORD, vault_path)
    with pytest.raises(Exception):
        load_vault("wrong-password", vault_path)


def test_set_variable_creates_entry(vault_path):
    set_variable("MY_VAR", "hello", PASSWORD, vault_path)
    assert get_variable("MY_VAR", PASSWORD, vault_path) == "hello"


def test_set_variable_overwrites_existing(vault_path):
    set_variable("MY_VAR", "first", PASSWORD, vault_path)
    set_variable("MY_VAR", "second", PASSWORD, vault_path)
    assert get_variable("MY_VAR", PASSWORD, vault_path) == "second"


def test_get_variable_missing_key_returns_none(vault_path):
    result = get_variable("NONEXISTENT", PASSWORD, vault_path)
    assert result is None


def test_delete_variable_removes_key(vault_path):
    set_variable("TO_DELETE", "bye", PASSWORD, vault_path)
    removed = delete_variable("TO_DELETE", PASSWORD, vault_path)
    assert removed is True
    assert get_variable("TO_DELETE", PASSWORD, vault_path) is None


def test_delete_variable_missing_key_returns_false(vault_path):
    result = delete_variable("GHOST", PASSWORD, vault_path)
    assert result is False


def test_get_vault_path_default():
    path = get_vault_path()
    assert path.name == "vault.enc"
    assert ".envault" in str(path)
