"""Unit tests for envault.pin."""

import pytest
from envault.pin import (
    get_pinned,
    pin_variable,
    unpin_variable,
    is_pinned,
    guard_pinned,
    META_KEY,
)


BASE_VARS = {"DB_HOST": "localhost", "DB_PORT": "5432"}


def test_get_pinned_empty_when_no_meta():
    assert get_pinned(BASE_VARS) == []


def test_pin_variable_adds_key():
    result = pin_variable(BASE_VARS, "DB_HOST")
    assert "DB_HOST" in get_pinned(result)


def test_pin_variable_does_not_mutate_original():
    original = dict(BASE_VARS)
    pin_variable(original, "DB_HOST")
    assert META_KEY not in original


def test_pin_variable_raises_for_missing_key():
    with pytest.raises(KeyError, match="MISSING"):
        pin_variable(BASE_VARS, "MISSING")


def test_pin_variable_multiple_keys_sorted():
    v = pin_variable(BASE_VARS, "DB_PORT")
    v = pin_variable(v, "DB_HOST")
    assert get_pinned(v) == ["DB_HOST", "DB_PORT"]


def test_pin_variable_idempotent():
    v1 = pin_variable(BASE_VARS, "DB_HOST")
    v2 = pin_variable(v1, "DB_HOST")
    assert get_pinned(v2) == ["DB_HOST"]


def test_unpin_variable_removes_key():
    v = pin_variable(BASE_VARS, "DB_HOST")
    v = unpin_variable(v, "DB_HOST")
    assert get_pinned(v) == []


def test_unpin_variable_cleans_up_meta_when_empty():
    v = pin_variable(BASE_VARS, "DB_HOST")
    v = unpin_variable(v, "DB_HOST")
    assert META_KEY not in v


def test_unpin_variable_noop_when_not_pinned():
    result = unpin_variable(BASE_VARS, "DB_HOST")
    assert get_pinned(result) == []


def test_is_pinned_true_after_pin():
    v = pin_variable(BASE_VARS, "DB_HOST")
    assert is_pinned(v, "DB_HOST") is True


def test_is_pinned_false_before_pin():
    assert is_pinned(BASE_VARS, "DB_HOST") is False


def test_guard_pinned_raises_for_pinned_key():
    v = pin_variable(BASE_VARS, "DB_HOST")
    with pytest.raises(ValueError, match="pinned"):
        guard_pinned(v, "DB_HOST")


def test_guard_pinned_passes_for_unpinned_key():
    guard_pinned(BASE_VARS, "DB_HOST")  # should not raise
