"""Tests for envault.visibility module."""

import pytest
from envault.visibility import (
    get_visibility,
    set_visibility,
    remove_visibility,
    get_level,
    filter_by_visibility,
    list_visibility,
    VALID_LEVELS,
)

base_vars = {
    "API_KEY": "abc123",
    "DB_HOST": "localhost",
    "PORT": "5432",
}


def test_get_visibility_empty_when_no_meta():
    result = get_visibility(base_vars)
    assert result == {}


def test_set_visibility_stores_level():
    updated = set_visibility(base_vars, "API_KEY", "secret")
    assert updated["__meta_visibility__"]["API_KEY"] == "secret"


def test_set_visibility_does_not_mutate_original():
    original = dict(base_vars)
    set_visibility(original, "PORT", "public")
    assert "__meta_visibility__" not in original


def test_set_visibility_raises_for_missing_key():
    with pytest.raises(KeyError, match="MISSING"):
        set_visibility(base_vars, "MISSING", "public")


def test_set_visibility_raises_for_invalid_level():
    with pytest.raises(ValueError, match="invalid"):
        set_visibility(base_vars, "API_KEY", "invalid")


def test_set_visibility_raises_for_meta_key():
    vars_with_meta = {**base_vars, "__meta_visibility__": {}}
    with pytest.raises(ValueError, match="metadata"):
        set_visibility(vars_with_meta, "__meta_visibility__", "public")


def test_set_visibility_all_valid_levels():
    for level in VALID_LEVELS:
        updated = set_visibility(base_vars, "PORT", level)
        assert updated["__meta_visibility__"]["PORT"] == level


def test_remove_visibility_clears_entry():
    updated = set_visibility(base_vars, "API_KEY", "secret")
    removed = remove_visibility(updated, "API_KEY")
    assert "API_KEY" not in removed.get("__meta_visibility__", {})


def test_remove_visibility_noop_when_not_set():
    result = remove_visibility(base_vars, "API_KEY")
    assert result.get("__meta_visibility__", {}) == {}


def test_get_level_defaults_to_private():
    assert get_level(base_vars, "API_KEY") == "private"


def test_get_level_returns_set_level():
    updated = set_visibility(base_vars, "DB_HOST", "public")
    assert get_level(updated, "DB_HOST") == "public"


def test_filter_by_visibility_returns_matching():
    v = set_visibility(base_vars, "API_KEY", "secret")
    v = set_visibility(v, "PORT", "public")
    result = filter_by_visibility(v, "secret")
    assert result == {"API_KEY": "abc123"}


def test_filter_by_visibility_excludes_meta_keys():
    v = set_visibility(base_vars, "API_KEY", "public")
    result = filter_by_visibility(v, "public")
    assert all(not k.startswith("__") for k in result)


def test_filter_by_visibility_invalid_level_raises():
    with pytest.raises(ValueError):
        filter_by_visibility(base_vars, "classified")


def test_list_visibility_returns_all_keys():
    v = set_visibility(base_vars, "API_KEY", "secret")
    result = list_visibility(v)
    assert set(result.keys()) == {"API_KEY", "DB_HOST", "PORT"}
    assert result["API_KEY"] == "secret"
    assert result["DB_HOST"] == "private"
