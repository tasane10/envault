"""Tests for envault.label."""
from __future__ import annotations

import pytest

from envault.label import (
    filter_by_label,
    get_labels,
    list_labels,
    remove_labels,
    set_labels,
)

_META = "__labels__"

base_vars: dict = {"API_KEY": "secret", "DB_URL": "postgres://localhost/db"}


def test_get_labels_empty_when_no_meta():
    assert get_labels(base_vars) == {}


def test_get_labels_returns_existing_mapping():
    variables = {**base_vars, _META: {"API_KEY": ["production", "secret"]}}
    result = get_labels(variables)
    assert result == {"API_KEY": ["production", "secret"]}


def test_get_labels_returns_copy():
    variables = {**base_vars, _META: {"API_KEY": ["x"]}}
    result = get_labels(variables)
    result["API_KEY"].append("y")
    assert get_labels(variables) == {"API_KEY": ["x"]}


def test_set_labels_stores_sorted_unique():
    result = set_labels(base_vars, "API_KEY", ["secret", "production", "secret"])
    assert result[_META]["API_KEY"] == ["production", "secret"]


def test_set_labels_does_not_mutate_original():
    set_labels(base_vars, "API_KEY", ["x"])
    assert _META not in base_vars


def test_set_labels_raises_for_missing_key():
    with pytest.raises(KeyError, match="MISSING"):
        set_labels(base_vars, "MISSING", ["x"])


def test_set_labels_raises_for_meta_key():
    variables = {**base_vars, _META: {}}
    with pytest.raises(KeyError):
        set_labels(variables, _META, ["x"])


def test_set_labels_empty_list_removes_entry():
    variables = {**base_vars, _META: {"API_KEY": ["production"]}}
    result = set_labels(variables, "API_KEY", [])
    assert "API_KEY" not in result.get(_META, {})


def test_remove_labels_clears_entry():
    variables = {**base_vars, _META: {"API_KEY": ["secret"]}}
    result = remove_labels(variables, "API_KEY")
    assert "API_KEY" not in result.get(_META, {})


def test_filter_by_label_returns_matching_keys():
    variables = {
        **base_vars,
        _META: {
            "API_KEY": ["production", "secret"],
            "DB_URL": ["production"],
        },
    }
    result = filter_by_label(variables, "secret")
    assert result == {"API_KEY": "secret"}


def test_filter_by_label_excludes_meta_keys():
    variables = {**base_vars, _META: {"API_KEY": ["x"]}}
    result = filter_by_label(variables, "x")
    assert _META not in result


def test_filter_by_label_no_match_returns_empty():
    result = filter_by_label(base_vars, "nonexistent")
    assert result == {}


def test_list_labels_returns_sorted_unique():
    variables = {
        **base_vars,
        _META: {
            "API_KEY": ["secret", "production"],
            "DB_URL": ["production", "legacy"],
        },
    }
    assert list_labels(variables) == ["legacy", "production", "secret"]


def test_list_labels_empty_when_no_meta():
    assert list_labels(base_vars) == []
