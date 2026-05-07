"""Tests for envault.annotation."""

from __future__ import annotations

import pytest

from envault.annotation import (
    filter_annotated,
    get_annotation,
    get_annotations,
    remove_annotation,
    set_annotation,
)

BASE_VARS = {"DB_URL": "postgres://localhost", "SECRET": "s3cr3t"}


def test_get_annotations_empty_when_no_meta():
    assert get_annotations(BASE_VARS) == {}


def test_set_annotation_stores_description():
    result = set_annotation(BASE_VARS, "DB_URL", "Primary database connection string")
    assert get_annotation(result, "DB_URL") == "Primary database connection string"


def test_set_annotation_does_not_mutate_original():
    original = dict(BASE_VARS)
    set_annotation(original, "SECRET", "App secret key")
    assert "__annotations__" not in original


def test_set_annotation_raises_for_missing_key():
    with pytest.raises(KeyError, match="MISSING"):
        set_annotation(BASE_VARS, "MISSING", "some description")


def test_set_annotation_raises_for_meta_key():
    variables = {**BASE_VARS, "__tags__": {"DB_URL": ["prod"]}}
    with pytest.raises(KeyError):
        set_annotation(variables, "__tags__", "should fail")


def test_set_annotation_multiple_keys():
    v1 = set_annotation(BASE_VARS, "DB_URL", "The DB")
    v2 = set_annotation(v1, "SECRET", "The secret")
    assert get_annotation(v2, "DB_URL") == "The DB"
    assert get_annotation(v2, "SECRET") == "The secret"


def test_remove_annotation_removes_entry():
    annotated = set_annotation(BASE_VARS, "DB_URL", "desc")
    cleaned = remove_annotation(annotated, "DB_URL")
    assert get_annotation(cleaned, "DB_URL") is None


def test_remove_annotation_noop_when_not_set():
    result = remove_annotation(BASE_VARS, "DB_URL")
    assert get_annotation(result, "DB_URL") is None


def test_remove_annotation_does_not_mutate_original():
    annotated = set_annotation(BASE_VARS, "DB_URL", "desc")
    original_copy = dict(annotated)
    remove_annotation(annotated, "DB_URL")
    assert annotated == original_copy


def test_get_annotation_returns_none_when_absent():
    assert get_annotation(BASE_VARS, "DB_URL") is None


def test_filter_annotated_returns_only_existing_keys():
    v = set_annotation(BASE_VARS, "DB_URL", "desc")
    result = filter_annotated(v)
    assert set(result.keys()) == {"DB_URL"}


def test_filter_annotated_excludes_deleted_variables():
    v = set_annotation(BASE_VARS, "DB_URL", "desc")
    # Remove the actual variable but keep annotation block
    v.pop("DB_URL")
    result = filter_annotated(v)
    assert "DB_URL" not in result


def test_filter_annotated_empty_when_none_annotated():
    assert filter_annotated(BASE_VARS) == {}
