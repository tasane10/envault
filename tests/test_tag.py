"""Tests for envault.tag module."""

import json
import pytest
from unittest.mock import patch, MagicMock
from envault.tag import (
    TAGS_META_KEY,
    get_tags,
    set_tags,
    remove_tags,
    filter_by_tag,
    tag_variable,
)


@pytest.fixture
def base_vars():
    return {"DB_URL": "postgres://localhost", "API_KEY": "secret"}


def test_get_tags_empty_when_no_meta(base_vars):
    assert get_tags(base_vars, "DB_URL") == []


def test_set_tags_stores_sorted_unique(base_vars):
    updated = set_tags(base_vars, "DB_URL", ["prod", "db", "prod"])
    assert get_tags(updated, "DB_URL") == ["db", "prod"]


def test_set_tags_does_not_mutate_original(base_vars):
    set_tags(base_vars, "DB_URL", ["prod"])
    assert TAGS_META_KEY not in base_vars


def test_set_tags_empty_list_removes_entry(base_vars):
    with_tags = set_tags(base_vars, "DB_URL", ["prod"])
    cleared = set_tags(with_tags, "DB_URL", [])
    assert get_tags(cleared, "DB_URL") == []


def test_get_tags_returns_correct_var(base_vars):
    updated = set_tags(base_vars, "DB_URL", ["db"])
    updated = set_tags(updated, "API_KEY", ["auth"])
    assert get_tags(updated, "DB_URL") == ["db"]
    assert get_tags(updated, "API_KEY") == ["auth"]


def test_remove_tags_specific(base_vars):
    updated = set_tags(base_vars, "DB_URL", ["prod", "db", "infra"])
    updated = remove_tags(updated, "DB_URL", ["db", "infra"])
    assert get_tags(updated, "DB_URL") == ["prod"]


def test_remove_tags_all(base_vars):
    updated = set_tags(base_vars, "DB_URL", ["prod", "db"])
    updated = remove_tags(updated, "DB_URL", None)
    assert get_tags(updated, "DB_URL") == []


def test_filter_by_tag_returns_matching_vars(base_vars):
    updated = set_tags(base_vars, "DB_URL", ["prod", "db"])
    updated = set_tags(updated, "API_KEY", ["prod", "auth"])
    result = filter_by_tag(updated, "prod")
    assert set(result.keys()) == {"DB_URL", "API_KEY"}


def test_filter_by_tag_excludes_meta_key(base_vars):
    updated = set_tags(base_vars, "DB_URL", ["prod"])
    result = filter_by_tag(updated, "prod")
    assert TAGS_META_KEY not in result


def test_filter_by_tag_no_matches(base_vars):
    updated = set_tags(base_vars, "DB_URL", ["dev"])
    result = filter_by_tag(updated, "prod")
    assert result == {}


def test_tag_variable_persists(base_vars):
    with patch("envault.tag.load_profile", return_value=dict(base_vars)) as mock_load, \
         patch("envault.tag.save_profile") as mock_save:
        result = tag_variable("pass", "DB_URL", ["prod", "db"], profile="default")
        mock_save.assert_called_once()
        assert "prod" in result and "db" in result


def test_tag_variable_raises_for_missing_var(base_vars):
    with patch("envault.tag.load_profile", return_value=dict(base_vars)):
        with pytest.raises(KeyError, match="MISSING"):
            tag_variable("pass", "MISSING", ["x"], profile="default")
