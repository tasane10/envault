"""Tests for envault.group module."""
import pytest
from envault.group import (
    get_groups,
    set_group,
    remove_from_group,
    filter_by_group,
    list_groups,
)

META = "__meta__"


@pytest.fixture
def base_vars():
    return {"DB_HOST": "localhost", "DB_PORT": "5432", "API_KEY": "secret"}


def test_get_groups_empty_when_no_meta(base_vars):
    assert get_groups(base_vars) == {}


def test_set_group_assigns_key(base_vars):
    result = set_group(base_vars, "DB_HOST", "database")
    groups = get_groups(result)
    assert "DB_HOST" in groups["database"]


def test_set_group_does_not_mutate_original(base_vars):
    original = dict(base_vars)
    set_group(base_vars, "DB_HOST", "database")
    assert base_vars == original


def test_set_group_raises_for_missing_key(base_vars):
    with pytest.raises(KeyError, match="MISSING"):
        set_group(base_vars, "MISSING", "somegroup")


def test_set_group_raises_for_meta_key():
    variables = {"__meta__": {}}
    with pytest.raises(KeyError):
        set_group(variables, "__meta__", "somegroup")


def test_set_group_moves_key_between_groups(base_vars):
    v = set_group(base_vars, "DB_HOST", "database")
    v = set_group(v, "DB_HOST", "network")
    groups = get_groups(v)
    assert "DB_HOST" not in groups.get("database", [])
    assert "DB_HOST" in groups["network"]


def test_set_group_multiple_keys_sorted(base_vars):
    v = set_group(base_vars, "DB_PORT", "database")
    v = set_group(v, "DB_HOST", "database")
    groups = get_groups(v)
    assert groups["database"] == sorted(groups["database"])


def test_remove_from_group_removes_key(base_vars):
    v = set_group(base_vars, "DB_HOST", "database")
    v = remove_from_group(v, "DB_HOST", "database")
    groups = get_groups(v)
    assert "database" not in groups


def test_remove_from_group_prunes_empty_group(base_vars):
    v = set_group(base_vars, "DB_HOST", "database")
    v = remove_from_group(v, "DB_HOST", "database")
    assert "database" not in get_groups(v)


def test_remove_from_group_raises_for_unknown_key(base_vars):
    """Removing a key not in the group should raise a KeyError."""
    v = set_group(base_vars, "DB_HOST", "database")
    with pytest.raises(KeyError):
        remove_from_group(v, "API_KEY", "database")


def test_remove_from_group_raises_for_unknown_group(base_vars):
    """Removing a key from a non-existent group should raise a KeyError."""
    with pytest.raises(KeyError):
        remove_from_group(base_vars, "DB_HOST", "nonexistent")


def test_filter_by_group_returns_subset(base_vars):
    v = set_group(base_vars, "DB_HOST", "database")
    v = set_group(v, "DB_PORT", "database")
    subset = filter_by_group(v, "database")
    assert set(subset.keys()) == {"DB_HOST", "DB_PORT"}


def test_filter_by_group_empty_for_unknown(base_vars):
    assert filter_by_group(base_vars, "nonexistent") == {}


def test_list_groups_sorted(base_vars):
    v = set_group(base_vars, "API_KEY", "security")
    v = set_group(v, "DB_HOST", "database")
    assert list_groups(v) == ["database", "security"]


def test_list_groups_empty_when_none(base_vars):
    assert list_groups(base_vars) == []
