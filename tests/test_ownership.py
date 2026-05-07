"""Tests for envault.ownership."""

from __future__ import annotations

import pytest

from envault.ownership import (
    filter_by_owner,
    get_owner,
    list_owners,
    remove_owner,
    set_owner,
)


@pytest.fixture()
def base_vars():
    return {"API_KEY": "secret", "DB_PASS": "hunter2", "PORT": "8080"}


def test_get_owner_returns_none_when_no_meta(base_vars):
    assert get_owner(base_vars, "API_KEY") is None


def test_get_owner_returns_owner_when_set(base_vars):
    updated = set_owner(base_vars, "API_KEY", "alice")
    assert get_owner(updated, "API_KEY") == "alice"


def test_set_owner_does_not_mutate_original(base_vars):
    original_meta = base_vars.get("__meta")
    set_owner(base_vars, "API_KEY", "bob")
    assert base_vars.get("__meta") == original_meta


def test_set_owner_raises_for_missing_key(base_vars):
    with pytest.raises(KeyError, match="MISSING"):
        set_owner(base_vars, "MISSING", "alice")


def test_set_owner_raises_for_meta_key(base_vars):
    base_vars["__meta"] = {}
    with pytest.raises(KeyError):
        set_owner(base_vars, "__meta", "alice")


def test_set_owner_raises_for_empty_owner(base_vars):
    with pytest.raises(ValueError, match="non-empty"):
        set_owner(base_vars, "API_KEY", "   ")


def test_set_owner_strips_whitespace(base_vars):
    updated = set_owner(base_vars, "API_KEY", "  carol  ")
    assert get_owner(updated, "API_KEY") == "carol"


def test_set_owner_overwrites_previous(base_vars):
    v1 = set_owner(base_vars, "API_KEY", "alice")
    v2 = set_owner(v1, "API_KEY", "bob")
    assert get_owner(v2, "API_KEY") == "bob"


def test_remove_owner_clears_entry(base_vars):
    updated = set_owner(base_vars, "API_KEY", "alice")
    cleared = remove_owner(updated, "API_KEY")
    assert get_owner(cleared, "API_KEY") is None


def test_remove_owner_on_unowned_key_is_safe(base_vars):
    result = remove_owner(base_vars, "PORT")
    assert get_owner(result, "PORT") is None


def test_list_owners_returns_sorted_mapping(base_vars):
    v = set_owner(base_vars, "PORT", "dave")
    v = set_owner(v, "API_KEY", "alice")
    owners = list_owners(v)
    assert list(owners.keys()) == ["API_KEY", "PORT"]
    assert owners["API_KEY"] == "alice"
    assert owners["PORT"] == "dave"


def test_list_owners_excludes_deleted_keys(base_vars):
    v = set_owner(base_vars, "API_KEY", "alice")
    # Remove the variable itself but leave meta intact
    v.pop("API_KEY")
    owners = list_owners(v)
    assert "API_KEY" not in owners


def test_filter_by_owner_returns_matching_keys(base_vars):
    v = set_owner(base_vars, "API_KEY", "alice")
    v = set_owner(v, "PORT", "alice")
    v = set_owner(v, "DB_PASS", "bob")
    keys = filter_by_owner(v, "alice")
    assert keys == ["API_KEY", "PORT"]


def test_filter_by_owner_empty_when_no_match(base_vars):
    assert filter_by_owner(base_vars, "nobody") == []
