"""Tests for envault.expiry module."""

from __future__ import annotations

import time

import pytest

from envault.expiry import (
    get_expiry,
    set_expiry,
    remove_expiry,
    is_expired,
    list_expiring,
    purge_expired,
)

_FUTURE = time.time() + 3600
_PAST = time.time() - 3600


@pytest.fixture
def base_vars() -> dict:
    return {"API_KEY": "secret", "DB_URL": "postgres://localhost/db"}


def test_get_expiry_returns_none_when_not_set(base_vars):
    assert get_expiry(base_vars, "API_KEY") is None


def test_get_expiry_returns_timestamp_when_set(base_vars):
    updated = set_expiry(base_vars, "API_KEY", _FUTURE)
    assert get_expiry(updated, "API_KEY") == pytest.approx(_FUTURE)


def test_set_expiry_does_not_mutate_original(base_vars):
    original = dict(base_vars)
    set_expiry(base_vars, "API_KEY", _FUTURE)
    assert base_vars == original


def test_set_expiry_raises_for_missing_key(base_vars):
    with pytest.raises(ValueError, match="does not exist"):
        set_expiry(base_vars, "MISSING_KEY", _FUTURE)


def test_set_expiry_raises_for_meta_key(base_vars):
    base_vars["__meta__"] = {}
    with pytest.raises(ValueError, match="meta key"):
        set_expiry(base_vars, "__meta__", _FUTURE)


def test_set_expiry_raises_for_past_timestamp(base_vars):
    with pytest.raises(ValueError, match="future timestamp"):
        set_expiry(base_vars, "API_KEY", _PAST)


def test_remove_expiry_clears_key(base_vars):
    updated = set_expiry(base_vars, "API_KEY", _FUTURE)
    cleared = remove_expiry(updated, "API_KEY")
    assert get_expiry(cleared, "API_KEY") is None


def test_remove_expiry_removes_meta_key_when_empty(base_vars):
    updated = set_expiry(base_vars, "API_KEY", _FUTURE)
    cleared = remove_expiry(updated, "API_KEY")
    assert "__expiry__" not in cleared


def test_remove_expiry_keeps_other_entries(base_vars):
    updated = set_expiry(base_vars, "API_KEY", _FUTURE)
    updated = set_expiry(updated, "DB_URL", _FUTURE)
    cleared = remove_expiry(updated, "API_KEY")
    assert get_expiry(cleared, "DB_URL") is not None


def test_is_expired_false_for_future(base_vars):
    updated = set_expiry(base_vars, "API_KEY", _FUTURE)
    assert is_expired(updated, "API_KEY") is False


def test_is_expired_true_for_past(base_vars):
    base_vars["__expiry__"] = {"API_KEY": _PAST}
    assert is_expired(base_vars, "API_KEY") is True


def test_is_expired_false_when_no_expiry(base_vars):
    assert is_expired(base_vars, "API_KEY") is False


def test_list_expiring_sorted_soonest_first(base_vars):
    updated = set_expiry(base_vars, "DB_URL", _FUTURE + 100)
    updated = set_expiry(updated, "API_KEY", _FUTURE + 10)
    entries = list_expiring(updated)
    assert entries[0]["key"] == "API_KEY"
    assert entries[1]["key"] == "DB_URL"


def test_list_expiring_marks_expired(base_vars):
    base_vars["__expiry__"] = {"API_KEY": _PAST}
    entries = list_expiring(base_vars)
    assert entries[0]["expired"] is True


def test_purge_expired_removes_past_keys(base_vars):
    base_vars["__expiry__"] = {"API_KEY": _PAST}
    updated, removed = purge_expired(base_vars)
    assert "API_KEY" not in updated
    assert "API_KEY" in removed


def test_purge_expired_keeps_future_keys(base_vars):
    updated_vars = set_expiry(base_vars, "API_KEY", _FUTURE)
    result, removed = purge_expired(updated_vars)
    assert "API_KEY" in result
    assert removed == []


def test_purge_expired_returns_removed_list(base_vars):
    base_vars["__expiry__"] = {"API_KEY": _PAST, "DB_URL": _PAST}
    _, removed = purge_expired(base_vars)
    assert sorted(removed) == ["API_KEY", "DB_URL"]
