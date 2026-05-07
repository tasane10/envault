"""Tests for envault.priority."""

from __future__ import annotations

import pytest

from envault.priority import (
    get_priority,
    list_priorities,
    remove_priority,
    set_priority,
    sort_by_priority,
)


@pytest.fixture()
def base_vars() -> dict:
    return {"DB_HOST": "localhost", "DB_PORT": "5432", "API_KEY": "secret"}


def test_get_priority_returns_none_when_not_set(base_vars):
    assert get_priority(base_vars, "DB_HOST") is None


def test_set_priority_stores_level(base_vars):
    updated = set_priority(base_vars, "DB_HOST", 10)
    assert get_priority(updated, "DB_HOST") == 10


def test_set_priority_does_not_mutate_original(base_vars):
    original_copy = dict(base_vars)
    set_priority(base_vars, "DB_HOST", 5)
    assert base_vars == original_copy


def test_set_priority_raises_for_missing_key(base_vars):
    with pytest.raises(KeyError, match="MISSING"):
        set_priority(base_vars, "MISSING", 1)


def test_set_priority_raises_for_meta_key(base_vars):
    vars_with_meta = {**base_vars, "__tags__": {}}
    with pytest.raises(ValueError, match="metadata"):
        set_priority(vars_with_meta, "__tags__", 1)


def test_set_priority_raises_for_negative_level(base_vars):
    with pytest.raises(ValueError, match="non-negative"):
        set_priority(base_vars, "DB_HOST", -1)


def test_set_priority_allows_zero(base_vars):
    updated = set_priority(base_vars, "DB_HOST", 0)
    assert get_priority(updated, "DB_HOST") == 0


def test_remove_priority_clears_entry(base_vars):
    updated = set_priority(base_vars, "DB_HOST", 7)
    updated = remove_priority(updated, "DB_HOST")
    assert get_priority(updated, "DB_HOST") is None


def test_remove_priority_removes_meta_key_when_empty(base_vars):
    updated = set_priority(base_vars, "DB_HOST", 3)
    updated = remove_priority(updated, "DB_HOST")
    assert "__priority__" not in updated


def test_remove_priority_noop_when_not_set(base_vars):
    updated = remove_priority(base_vars, "DB_HOST")
    assert updated == base_vars


def test_list_priorities_returns_all_entries(base_vars):
    updated = set_priority(base_vars, "DB_HOST", 10)
    updated = set_priority(updated, "API_KEY", 5)
    result = list_priorities(updated)
    assert result == {"DB_HOST": 10, "API_KEY": 5}


def test_list_priorities_empty_when_none_set(base_vars):
    assert list_priorities(base_vars) == {}


def test_sort_by_priority_orders_highest_first(base_vars):
    updated = set_priority(base_vars, "DB_PORT", 1)
    updated = set_priority(updated, "DB_HOST", 10)
    updated = set_priority(updated, "API_KEY", 5)
    ordered = sort_by_priority(updated)
    prioritised = [k for k in ordered if k in {"DB_HOST", "DB_PORT", "API_KEY"}]
    assert prioritised.index("DB_HOST") < prioritised.index("API_KEY")
    assert prioritised.index("API_KEY") < prioritised.index("DB_PORT")


def test_sort_by_priority_excludes_meta_keys():
    variables = {"A": "1", "__priority__": {"A": 5}, "__tags__": {}}
    ordered = sort_by_priority(variables)
    assert "__priority__" not in ordered
    assert "__tags__" not in ordered
