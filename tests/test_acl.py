"""Tests for envault.acl — access control list logic."""

from __future__ import annotations

import pytest

from envault.acl import (
    check_access,
    get_acl,
    list_acl,
    remove_acl,
    set_acl,
)


@pytest.fixture()
def base_vars():
    return {"API_KEY": "secret", "DEBUG": "true"}


def test_get_acl_empty_when_no_meta(base_vars):
    assert get_acl(base_vars) == {}


def test_set_acl_stores_roles(base_vars):
    updated = set_acl(base_vars, "API_KEY", ["reader"])
    assert get_acl(updated) == {"API_KEY": ["reader"]}


def test_set_acl_sorts_and_deduplicates_roles(base_vars):
    updated = set_acl(base_vars, "API_KEY", ["writer", "reader", "reader"])
    assert get_acl(updated)["API_KEY"] == ["reader", "writer"]


def test_set_acl_does_not_mutate_original(base_vars):
    original = dict(base_vars)
    set_acl(base_vars, "API_KEY", ["reader"])
    assert base_vars == original


def test_set_acl_raises_for_missing_key(base_vars):
    with pytest.raises(KeyError, match="MISSING"):
        set_acl(base_vars, "MISSING", ["reader"])


def test_set_acl_raises_for_invalid_role(base_vars):
    with pytest.raises(ValueError, match="Invalid roles"):
        set_acl(base_vars, "API_KEY", ["superuser"])


def test_set_acl_empty_roles_removes_entry(base_vars):
    updated = set_acl(base_vars, "API_KEY", ["reader"])
    updated = set_acl(updated, "API_KEY", [])
    assert "API_KEY" not in get_acl(updated)


def test_remove_acl_clears_entry(base_vars):
    updated = set_acl(base_vars, "API_KEY", ["writer"])
    updated = remove_acl(updated, "API_KEY")
    assert get_acl(updated) == {}


def test_remove_acl_noop_when_not_set(base_vars):
    updated = remove_acl(base_vars, "API_KEY")
    assert get_acl(updated) == {}


def test_check_access_no_acl_grants_all(base_vars):
    assert check_access(base_vars, "API_KEY", "reader") is True
    assert check_access(base_vars, "API_KEY", "writer") is True


def test_check_access_admin_always_allowed(base_vars):
    updated = set_acl(base_vars, "API_KEY", ["reader"])
    assert check_access(updated, "API_KEY", "admin") is True


def test_check_access_denied_when_role_not_in_acl(base_vars):
    updated = set_acl(base_vars, "API_KEY", ["reader"])
    assert check_access(updated, "API_KEY", "writer") is False


def test_check_access_granted_when_role_in_acl(base_vars):
    updated = set_acl(base_vars, "API_KEY", ["reader", "writer"])
    assert check_access(updated, "API_KEY", "writer") is True


def test_list_acl_returns_sorted(base_vars):
    updated = set_acl(base_vars, "DEBUG", ["admin"])
    updated = set_acl(updated, "API_KEY", ["reader"])
    entries = list_acl(updated)
    assert [e["key"] for e in entries] == ["API_KEY", "DEBUG"]


def test_list_acl_empty_when_no_entries(base_vars):
    assert list_acl(base_vars) == []
