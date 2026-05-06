"""Tests for envault.history — variable change history tracking."""

from __future__ import annotations

import time
from pathlib import Path
from unittest.mock import patch

import pytest

import envault.history as history_mod
from envault.history import (
    clear_history,
    get_history,
    get_history_path,
    list_tracked_keys,
    record_change,
)


@pytest.fixture(autouse=True)
def isolated_history(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """Redirect ENVAULT_HOME to a temp directory for every test."""
    monkeypatch.setattr(history_mod, "ENVAULT_HOME", tmp_path)


# ---------------------------------------------------------------------------
# get_history_path
# ---------------------------------------------------------------------------

def test_get_history_path_default_profile(tmp_path: Path):
    p = get_history_path()
    assert p == tmp_path / "profiles" / "default" / "history.json"


def test_get_history_path_named_profile(tmp_path: Path):
    p = get_history_path("staging")
    assert p == tmp_path / "profiles" / "staging" / "history.json"


# ---------------------------------------------------------------------------
# record_change
# ---------------------------------------------------------------------------

def test_record_change_creates_entry():
    entry = record_change("API_KEY", "abc123")
    assert entry["new_value"] == "abc123"
    assert "timestamp" in entry
    assert entry["actor"] == "cli"


def test_record_change_stores_old_value():
    entry = record_change("DB_URL", "new", old_value="old")
    assert entry["old_value"] == "old"


def test_record_change_no_old_value_omits_key():
    entry = record_change("SECRET", "x")
    assert "old_value" not in entry


def test_record_change_persists_across_calls():
    record_change("TOKEN", "v1")
    record_change("TOKEN", "v2", old_value="v1")
    entries = get_history("TOKEN", limit=10)
    assert len(entries) == 2
    assert entries[0]["new_value"] == "v1"
    assert entries[1]["new_value"] == "v2"


def test_record_change_respects_max_entries():
    original_max = history_mod.MAX_HISTORY_ENTRIES
    history_mod.MAX_HISTORY_ENTRIES = 3
    try:
        for i in range(5):
            record_change("KEY", str(i))
        entries = get_history("KEY", limit=10)
        assert len(entries) == 3
        assert entries[-1]["new_value"] == "4"
    finally:
        history_mod.MAX_HISTORY_ENTRIES = original_max


# ---------------------------------------------------------------------------
# get_history
# ---------------------------------------------------------------------------

def test_get_history_returns_empty_for_unknown_key():
    assert get_history("MISSING_KEY") == []


def test_get_history_limit_respected():
    for i in range(8):
        record_change("K", str(i))
    entries = get_history("K", limit=3)
    assert len(entries) == 3
    assert entries[-1]["new_value"] == "7"


# ---------------------------------------------------------------------------
# clear_history
# ---------------------------------------------------------------------------

def test_clear_history_specific_key():
    record_change("A", "1")
    record_change("B", "2")
    removed = clear_history("A")
    assert removed == 1
    assert get_history("A") == []
    assert len(get_history("B")) == 1


def test_clear_history_all_keys():
    record_change("X", "1")
    record_change("Y", "2")
    removed = clear_history()
    assert removed == 2
    assert list_tracked_keys() == []


def test_clear_history_missing_key_returns_zero():
    assert clear_history("NONEXISTENT") == 0


# ---------------------------------------------------------------------------
# list_tracked_keys
# ---------------------------------------------------------------------------

def test_list_tracked_keys_sorted():
    record_change("ZEBRA", "1")
    record_change("ALPHA", "2")
    record_change("MANGO", "3")
    assert list_tracked_keys() == ["ALPHA", "MANGO", "ZEBRA"]


def test_list_tracked_keys_empty_when_no_history():
    assert list_tracked_keys() == []
