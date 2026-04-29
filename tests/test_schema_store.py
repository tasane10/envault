import json
import pytest
from pathlib import Path
from unittest.mock import patch
from envault.schema_store import (
    get_schema_path, load_schema, save_schema, delete_schema, list_schemas
)


@pytest.fixture
def mock_vault_base(tmp_path):
    def _get_profile_vault_path(profile="default"):
        return tmp_path / "profiles" / profile / "vault.enc"
    with patch("envault.schema_store.get_profile_vault_path", side_effect=_get_profile_vault_path):
        yield tmp_path


def test_get_schema_path_default(mock_vault_base, tmp_path):
    path = get_schema_path("default")
    assert path.name == "default.schema.json"
    assert "schemas" in str(path)


def test_get_schema_path_named(mock_vault_base, tmp_path):
    path = get_schema_path("production")
    assert "production.schema.json" in str(path)


def test_load_schema_returns_empty_when_missing(mock_vault_base):
    result = load_schema("default")
    assert result == {}


def test_save_and_load_roundtrip(mock_vault_base):
    schema = {"API_KEY": {"required": True, "min_length": 8}}
    save_schema(schema, "default")
    loaded = load_schema("default")
    assert loaded == schema


def test_save_creates_parent_directories(mock_vault_base, tmp_path):
    schema = {"X": {"required": False}}
    save_schema(schema, "staging")
    path = get_schema_path("staging")
    assert path.exists()


def test_delete_schema_returns_true_when_exists(mock_vault_base):
    save_schema({"K": {"required": True}}, "default")
    result = delete_schema("default")
    assert result is True
    assert load_schema("default") == {}


def test_delete_schema_returns_false_when_missing(mock_vault_base):
    result = delete_schema("nonexistent")
    assert result is False


def test_list_schemas_empty(mock_vault_base):
    result = list_schemas()
    assert result == []


def test_list_schemas_returns_profile_names(mock_vault_base):
    save_schema({"A": {}}, "alpha")
    save_schema({"B": {}}, "beta")
    result = list_schemas()
    assert set(result) == {"alpha", "beta"}
