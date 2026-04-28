"""Tests for envault.watch."""

import pytest

from envault.watch import get_changed_keys, watch_profile


# ---------------------------------------------------------------------------
# get_changed_keys
# ---------------------------------------------------------------------------

def test_get_changed_keys_detects_added():
    old = {"A": "1"}
    new = {"A": "1", "B": "2"}
    result = get_changed_keys(old, new)
    assert result["added"] == ["B"]
    assert result["removed"] == []
    assert result["changed"] == []


def test_get_changed_keys_detects_removed():
    old = {"A": "1", "B": "2"}
    new = {"A": "1"}
    result = get_changed_keys(old, new)
    assert result["removed"] == ["B"]
    assert result["added"] == []
    assert result["changed"] == []


def test_get_changed_keys_detects_changed():
    old = {"A": "1"}
    new = {"A": "99"}
    result = get_changed_keys(old, new)
    assert result["changed"] == ["A"]
    assert result["added"] == []
    assert result["removed"] == []


def test_get_changed_keys_ignores_meta_keys():
    old = {"__tags__": {"A": ["x"]}, "A": "1"}
    new = {"__tags__": {"A": ["y"]}, "A": "1"}
    result = get_changed_keys(old, new)
    assert result == {"added": [], "removed": [], "changed": []}


def test_get_changed_keys_identical_returns_empty():
    vars_ = {"A": "1", "B": "2"}
    result = get_changed_keys(vars_, vars_.copy())
    assert result == {"added": [], "removed": [], "changed": []}


# ---------------------------------------------------------------------------
# watch_profile
# ---------------------------------------------------------------------------

def test_watch_profile_calls_on_change_when_vault_changes(tmp_path, monkeypatch):
    """on_change should be called exactly once when the vault content changes."""
    call_log = []

    iteration = 0
    checksums = ["aaa", "bbb"]  # first poll sees a change

    def fake_checksum(profile, password):
        nonlocal iteration
        val = checksums[min(iteration, len(checksums) - 1)]
        iteration += 1
        return val

    def fake_load(profile, password):
        return {"NEW_KEY": "new_value"}

    monkeypatch.setattr("envault.watch._vault_checksum", fake_checksum)
    monkeypatch.setattr("envault.watch.load_profile", fake_load)
    monkeypatch.setattr("envault.watch.time.sleep", lambda _: None)

    def on_change(profile, new_vars):
        call_log.append((profile, new_vars))

    watch_profile("default", "pass", interval=0, on_change=on_change, max_iterations=1)

    assert len(call_log) == 1
    assert call_log[0][0] == "default"
    assert call_log[0][1] == {"NEW_KEY": "new_value"}


def test_watch_profile_no_callback_when_unchanged(monkeypatch):
    call_log = []
    monkeypatch.setattr("envault.watch._vault_checksum", lambda p, pw: "same")
    monkeypatch.setattr("envault.watch.time.sleep", lambda _: None)

    watch_profile("default", "pass", interval=0, on_change=lambda p, v: call_log.append(1), max_iterations=3)

    assert call_log == []
