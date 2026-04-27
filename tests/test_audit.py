"""Tests for envault.audit module."""

import json
import pytest
from pathlib import Path

from envault.audit import (
    get_audit_log_path,
    record_event,
    read_events,
    clear_events,
)


@pytest.fixture
def audit_dir(tmp_path):
    return tmp_path / "audit"


def test_get_audit_log_path_default_profile(audit_dir):
    path = get_audit_log_path("default", audit_dir)
    assert path == audit_dir / "default.jsonl"


def test_get_audit_log_path_named_profile(audit_dir):
    path = get_audit_log_path("production", audit_dir)
    assert path == audit_dir / "production.jsonl"


def test_record_event_creates_file(audit_dir):
    record_event("set", "API_KEY", profile="default", audit_dir=audit_dir)
    log_path = get_audit_log_path("default", audit_dir)
    assert log_path.exists()


def test_record_event_returns_event_dict(audit_dir):
    event = record_event("set", "DB_URL", profile="default", audit_dir=audit_dir)
    assert event["action"] == "set"
    assert event["key"] == "DB_URL"
    assert event["profile"] == "default"
    assert "timestamp" in event
    assert "actor" in event


def test_record_event_appends_multiple(audit_dir):
    record_event("set", "KEY1", profile="default", audit_dir=audit_dir)
    record_event("get", "KEY1", profile="default", audit_dir=audit_dir)
    record_event("delete", "KEY1", profile="default", audit_dir=audit_dir)
    events = read_events("default", audit_dir)
    assert len(events) == 3
    assert events[0]["action"] == "set"
    assert events[1]["action"] == "get"
    assert events[2]["action"] == "delete"


def test_read_events_empty_when_no_log(audit_dir):
    events = read_events("nonexistent", audit_dir)
    assert events == []


def test_read_events_valid_json(audit_dir):
    record_event("set", "TOKEN", profile="staging", audit_dir=audit_dir, actor="alice")
    events = read_events("staging", audit_dir)
    assert len(events) == 1
    assert events[0]["actor"] == "alice"


def test_record_event_creates_parent_dirs(tmp_path):
    deep_dir = tmp_path / "a" / "b" / "c"
    record_event("set", "X", profile="default", audit_dir=deep_dir)
    assert (deep_dir / "default.jsonl").exists()


def test_clear_events_returns_count(audit_dir):
    record_event("set", "A", profile="default", audit_dir=audit_dir)
    record_event("set", "B", profile="default", audit_dir=audit_dir)
    count = clear_events("default", audit_dir)
    assert count == 2


def test_clear_events_removes_file(audit_dir):
    record_event("set", "A", profile="default", audit_dir=audit_dir)
    clear_events("default", audit_dir)
    assert not get_audit_log_path("default", audit_dir).exists()


def test_clear_events_nonexistent_returns_zero(audit_dir):
    count = clear_events("ghost", audit_dir)
    assert count == 0


def test_profiles_have_separate_logs(audit_dir):
    record_event("set", "KEY", profile="dev", audit_dir=audit_dir)
    record_event("set", "KEY", profile="prod", audit_dir=audit_dir)
    dev_events = read_events("dev", audit_dir)
    prod_events = read_events("prod", audit_dir)
    assert len(dev_events) == 1
    assert len(prod_events) == 1
