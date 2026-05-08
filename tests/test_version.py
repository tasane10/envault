"""Tests for envault.version."""
import time

import pytest

from envault.version import (
    clear_versions,
    get_versions,
    record_version,
    rollback,
)


@pytest.fixture()
def base_vars():
    return {"API_KEY": "secret", "DB_URL": "postgres://localhost/dev"}


# ---------------------------------------------------------------------------
# get_versions
# ---------------------------------------------------------------------------

def test_get_versions_empty_when_no_meta(base_vars):
    assert get_versions(base_vars, "API_KEY") == []


def test_get_versions_returns_copy(base_vars):
    updated = record_version(base_vars, "API_KEY", "secret")
    history = get_versions(updated, "API_KEY")
    history.clear()
    assert len(get_versions(updated, "API_KEY")) == 1


# ---------------------------------------------------------------------------
# record_version
# ---------------------------------------------------------------------------

def test_record_version_stores_value(base_vars):
    updated = record_version(base_vars, "API_KEY", "secret")
    history = get_versions(updated, "API_KEY")
    assert len(history) == 1
    assert history[0]["value"] == "secret"


def test_record_version_stores_timestamp(base_vars):
    before = time.time()
    updated = record_version(base_vars, "API_KEY", "secret")
    after = time.time()
    ts = get_versions(updated, "API_KEY")[0]["timestamp"]
    assert before <= ts <= after


def test_record_version_does_not_mutate_original(base_vars):
    original = dict(base_vars)
    record_version(base_vars, "API_KEY", "secret")
    assert base_vars == original


def test_record_version_accumulates_entries(base_vars):
    v = record_version(base_vars, "API_KEY", "v1")
    v = record_version(v, "API_KEY", "v2")
    assert len(get_versions(v, "API_KEY")) == 2


def test_record_version_caps_at_max_versions(base_vars):
    v = base_vars
    for i in range(25):
        v = record_version(v, "API_KEY", f"val-{i}", max_versions=10)
    assert len(get_versions(v, "API_KEY")) == 10


def test_record_version_raises_for_missing_key(base_vars):
    with pytest.raises(KeyError, match="MISSING"):
        record_version(base_vars, "MISSING", "x")


def test_record_version_raises_for_meta_key(base_vars):
    with pytest.raises(KeyError, match="meta"):
        record_version(base_vars, "__versions__", "x")


# ---------------------------------------------------------------------------
# rollback
# ---------------------------------------------------------------------------

def test_rollback_restores_previous_value(base_vars):
    v = record_version(base_vars, "API_KEY", "old-secret")
    v["API_KEY"] = "new-secret"
    restored = rollback(v, "API_KEY", steps=1)
    assert restored["API_KEY"] == "old-secret"


def test_rollback_does_not_mutate_original(base_vars):
    v = record_version(base_vars, "API_KEY", "old")
    original_value = v["API_KEY"]
    rollback(v, "API_KEY", steps=1)
    assert v["API_KEY"] == original_value


def test_rollback_raises_when_not_enough_history(base_vars):
    v = record_version(base_vars, "API_KEY", "only-one")
    with pytest.raises(IndexError):
        rollback(v, "API_KEY", steps=5)


# ---------------------------------------------------------------------------
# clear_versions
# ---------------------------------------------------------------------------

def test_clear_versions_removes_history(base_vars):
    v = record_version(base_vars, "API_KEY", "secret")
    v = clear_versions(v, "API_KEY")
    assert get_versions(v, "API_KEY") == []


def test_clear_versions_removes_meta_key_when_empty(base_vars):
    v = record_version(base_vars, "API_KEY", "secret")
    v = clear_versions(v, "API_KEY")
    assert "__versions__" not in v


def test_clear_versions_does_not_mutate_original(base_vars):
    v = record_version(base_vars, "API_KEY", "secret")
    original = dict(v)
    clear_versions(v, "API_KEY")
    assert v == original
