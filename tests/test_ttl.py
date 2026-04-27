"""Tests for envault.ttl module."""

import time
import pytest
from datetime import datetime, timezone

from envault.ttl import (
    set_ttl,
    get_ttl,
    is_expired,
    remove_ttl,
    purge_expired,
    META_KEY,
)


BASE_VARS = {"FOO": "bar", "BAZ": "qux"}


def test_set_ttl_stores_expiry():
    before = datetime.now(timezone.utc).timestamp()
    updated = set_ttl(BASE_VARS, "FOO", 60)
    after = datetime.now(timezone.utc).timestamp()
    expiry = updated[META_KEY]["FOO"]["ttl"]
    assert before + 60 <= expiry <= after + 60


def test_set_ttl_does_not_mutate_original():
    original = dict(BASE_VARS)
    set_ttl(original, "FOO", 30)
    assert META_KEY not in original


def test_get_ttl_returns_none_when_not_set():
    assert get_ttl(BASE_VARS, "FOO") is None


def test_get_ttl_returns_timestamp_when_set():
    updated = set_ttl(BASE_VARS, "FOO", 100)
    ttl = get_ttl(updated, "FOO")
    assert isinstance(ttl, float)
    assert ttl > datetime.now(timezone.utc).timestamp()


def test_is_expired_false_for_future_ttl():
    updated = set_ttl(BASE_VARS, "FOO", 3600)
    assert not is_expired(updated, "FOO")


def test_is_expired_true_for_past_ttl():
    updated = set_ttl(BASE_VARS, "FOO", -1)
    assert is_expired(updated, "FOO")


def test_is_expired_false_when_no_ttl():
    assert not is_expired(BASE_VARS, "FOO")


def test_remove_ttl_clears_entry():
    updated = set_ttl(BASE_VARS, "FOO", 60)
    cleaned = remove_ttl(updated, "FOO")
    assert get_ttl(cleaned, "FOO") is None


def test_remove_ttl_removes_meta_when_empty():
    updated = set_ttl(BASE_VARS, "FOO", 60)
    cleaned = remove_ttl(updated, "FOO")
    assert META_KEY not in cleaned


def test_remove_ttl_keeps_other_entries():
    updated = set_ttl(BASE_VARS, "FOO", 60)
    updated = set_ttl(updated, "BAZ", 120)
    cleaned = remove_ttl(updated, "FOO")
    assert get_ttl(cleaned, "BAZ") is not None


def test_purge_expired_removes_stale_vars():
    updated = set_ttl(BASE_VARS, "FOO", -1)
    result, removed = purge_expired(updated)
    assert "FOO" not in result
    assert "FOO" in removed


def test_purge_expired_keeps_live_vars():
    updated = set_ttl(BASE_VARS, "FOO", 3600)
    result, removed = purge_expired(updated)
    assert "FOO" in result
    assert removed == []


def test_purge_expired_returns_empty_list_when_nothing_expired():
    _, removed = purge_expired(BASE_VARS)
    assert removed == []
