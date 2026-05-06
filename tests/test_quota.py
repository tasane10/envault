"""Tests for envault.quota."""

from __future__ import annotations

import pytest

from envault.quota import (
    get_quota,
    set_quota,
    remove_quota,
    count_variables,
    check_quota,
    META_KEY,
)


@pytest.fixture()
def base_vars():
    return {"DB_HOST": "localhost", "DB_PORT": "5432", "API_KEY": "secret"}


def test_get_quota_returns_none_when_not_set(base_vars):
    assert get_quota(base_vars) is None


def test_get_quota_returns_limit_when_set(base_vars):
    updated = set_quota(base_vars, 50)
    assert get_quota(updated) == 50


def test_set_quota_does_not_mutate_original(base_vars):
    original = dict(base_vars)
    set_quota(base_vars, 10)
    assert base_vars == original


def test_set_quota_raises_for_zero():
    with pytest.raises(ValueError, match="positive"):
        set_quota({}, 0)


def test_set_quota_raises_for_negative():
    with pytest.raises(ValueError):
        set_quota({}, -5)


def test_remove_quota_deletes_meta_key(base_vars):
    updated = set_quota(base_vars, 20)
    assert META_KEY in updated
    cleaned = remove_quota(updated)
    assert META_KEY not in cleaned


def test_remove_quota_preserves_other_keys(base_vars):
    updated = set_quota(base_vars, 20)
    cleaned = remove_quota(updated)
    assert cleaned["DB_HOST"] == "localhost"


def test_count_variables_excludes_meta_keys(base_vars):
    updated = set_quota(base_vars, 10)
    assert count_variables(updated) == 3


def test_check_quota_allowed_when_no_limit(base_vars):
    result = check_quota(base_vars)
    assert result["allowed"] is True
    assert result["limit"] is None
    assert result["remaining"] is None


def test_check_quota_allowed_within_limit(base_vars):
    updated = set_quota(base_vars, 5)
    result = check_quota(updated)
    assert result["allowed"] is True
    assert result["remaining"] == 2


def test_check_quota_denied_when_at_limit(base_vars):
    updated = set_quota(base_vars, 3)
    result = check_quota(updated, new_keys=1)
    assert result["allowed"] is False
    assert result["remaining"] == 0


def test_check_quota_multiple_new_keys(base_vars):
    updated = set_quota(base_vars, 4)
    result = check_quota(updated, new_keys=2)
    assert result["allowed"] is False
