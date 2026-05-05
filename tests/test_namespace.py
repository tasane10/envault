"""Tests for envault.namespace."""

import pytest

from envault.namespace import (
    add_namespace,
    filter_by_namespace,
    get_namespace_prefix,
    list_namespaces,
    move_namespace,
    strip_namespace,
)


SAMPLE_VARS = {
    "APP_HOST": "localhost",
    "APP_PORT": "8080",
    "DB_HOST": "db.local",
    "DB_PORT": "5432",
    "STANDALONE": "yes",
    "__meta_tags": "{}",
}


def test_get_namespace_prefix_uppercase():
    assert get_namespace_prefix("app") == "APP_"


def test_get_namespace_prefix_strips_trailing_underscore():
    assert get_namespace_prefix("APP_") == "APP_"


def test_get_namespace_prefix_empty_raises():
    with pytest.raises(ValueError):
        get_namespace_prefix("")


def test_list_namespaces_returns_sorted_unique():
    result = list_namespaces(SAMPLE_VARS)
    assert result == ["APP", "DB"]


def test_list_namespaces_excludes_meta_keys():
    result = list_namespaces(SAMPLE_VARS)
    assert not any(ns.startswith("_") for ns in result)


def test_list_namespaces_empty_vars():
    assert list_namespaces({}) == []


def test_filter_by_namespace_returns_correct_keys():
    result = filter_by_namespace(SAMPLE_VARS, "APP")
    assert set(result.keys()) == {"APP_HOST", "APP_PORT"}


def test_filter_by_namespace_excludes_meta():
    vars_with_meta = {"APP_KEY": "val", "__meta": "data"}
    result = filter_by_namespace(vars_with_meta, "APP")
    assert "__meta" not in result


def test_filter_by_namespace_empty_when_no_match():
    result = filter_by_namespace(SAMPLE_VARS, "MISSING")
    assert result == {}


def test_strip_namespace_removes_prefix():
    filtered = filter_by_namespace(SAMPLE_VARS, "DB")
    result = strip_namespace(filtered, "DB")
    assert result == {"HOST": "db.local", "PORT": "5432"}


def test_add_namespace_prepends_prefix():
    result = add_namespace({"HOST": "localhost", "PORT": "80"}, "svc")
    assert result == {"SVC_HOST": "localhost", "SVC_PORT": "80"}


def test_add_namespace_does_not_mutate_original():
    original = {"KEY": "val"}
    add_namespace(original, "NS")
    assert "KEY" in original


def test_move_namespace_renames_keys():
    updated, count = move_namespace(SAMPLE_VARS, "APP", "SVC")
    assert count == 2
    assert "SVC_HOST" in updated
    assert "SVC_PORT" in updated
    assert "APP_HOST" not in updated


def test_move_namespace_returns_zero_when_no_match():
    updated, count = move_namespace(SAMPLE_VARS, "GHOST", "NEW")
    assert count == 0
    assert updated == SAMPLE_VARS


def test_move_namespace_preserves_unrelated_keys():
    updated, _ = move_namespace(SAMPLE_VARS, "APP", "SVC")
    assert "DB_HOST" in updated
    assert "STANDALONE" in updated
