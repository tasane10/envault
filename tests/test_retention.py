"""Tests for envault.retention."""

from __future__ import annotations

import time

import pytest

from envault.retention import (
    find_expired,
    get_retention,
    purge_expired,
    remove_retention,
    set_retention,
)

META_KEY = "__meta__"


@pytest.fixture()
def base_vars() -> dict:
    return {"API_KEY": "abc123", "DB_PASS": "secret"}


def test_get_retention_returns_none_when_not_set(base_vars):
    assert get_retention(base_vars, "API_KEY") is None


def test_set_retention_stores_days(base_vars):
    result = set_retention(base_vars, "API_KEY", 30)
    assert get_retention(result, "API_KEY") == 30


def test_set_retention_does_not_mutate_original(base_vars):
    original = dict(base_vars)
    set_retention(base_vars, "API_KEY", 10)
    assert base_vars == original


def test_set_retention_raises_for_missing_key(base_vars):
    with pytest.raises(KeyError, match="MISSING"):
        set_retention(base_vars, "MISSING", 5)


def test_set_retention_raises_for_zero_days(base_vars):
    with pytest.raises(ValueError, match="positive"):
        set_retention(base_vars, "API_KEY", 0)


def test_set_retention_raises_for_negative_days(base_vars):
    with pytest.raises(ValueError):
        set_retention(base_vars, "API_KEY", -1)


def test_remove_retention_clears_policy(base_vars):
    variables = set_retention(base_vars, "API_KEY", 7)
    variables = remove_retention(variables, "API_KEY")
    assert get_retention(variables, "API_KEY") is None


def test_remove_retention_does_not_mutate_original(base_vars):
    variables = set_retention(base_vars, "API_KEY", 7)
    original_meta = dict(variables.get(META_KEY, {}))
    remove_retention(variables, "API_KEY")
    assert variables.get(META_KEY, {}) == original_meta


def test_find_expired_returns_empty_when_no_retention(base_vars):
    assert find_expired(base_vars) == []


def test_find_expired_returns_empty_for_future_expiry(base_vars):
    variables = set_retention(base_vars, "API_KEY", 30)
    assert find_expired(variables) == []


def test_find_expired_detects_past_expiry(base_vars):
    variables = set_retention(base_vars, "API_KEY", 1)
    # Backdate creation timestamp
    variables[META_KEY]["API_KEY"]["_created_at"] = time.time() - 2 * 86400
    expired = find_expired(variables)
    assert "API_KEY" in expired


def test_purge_expired_removes_keys(base_vars):
    variables = set_retention(base_vars, "API_KEY", 1)
    variables[META_KEY]["API_KEY"]["_created_at"] = time.time() - 2 * 86400
    new_vars, purged = purge_expired(variables)
    assert "API_KEY" not in new_vars
    assert "API_KEY" in purged


def test_purge_expired_preserves_non_expired(base_vars):
    variables = set_retention(base_vars, "API_KEY", 1)
    variables[META_KEY]["API_KEY"]["_created_at"] = time.time() - 2 * 86400
    new_vars, _ = purge_expired(variables)
    assert "DB_PASS" in new_vars


def test_purge_expired_does_not_mutate_original(base_vars):
    variables = set_retention(base_vars, "API_KEY", 1)
    variables[META_KEY]["API_KEY"]["_created_at"] = time.time() - 2 * 86400
    original_keys = set(variables.keys())
    purge_expired(variables)
    assert set(variables.keys()) == original_keys
