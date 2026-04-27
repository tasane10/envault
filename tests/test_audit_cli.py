"""Tests for the audit CLI commands."""

import pytest
from click.testing import CliRunner
from pathlib import Path

from envault.audit import record_event
from envault.audit_cli import audit_cmd


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def audit_dir(tmp_path):
    return tmp_path / "audit"


def test_log_cmd_no_events(runner, audit_dir):
    result = runner.invoke(
        audit_cmd, ["log", "--profile", "default", "--audit-dir", str(audit_dir)]
    )
    assert result.exit_code == 0
    assert "No audit events" in result.output


def test_log_cmd_shows_events(runner, audit_dir):
    record_event("set", "API_KEY", profile="default", audit_dir=audit_dir, actor="bob")
    record_event("get", "DB_URL", profile="default", audit_dir=audit_dir, actor="bob")
    result = runner.invoke(
        audit_cmd, ["log", "--profile", "default", "--audit-dir", str(audit_dir)]
    )
    assert result.exit_code == 0
    assert "SET" in result.output
    assert "GET" in result.output
    assert "API_KEY" in result.output
    assert "DB_URL" in result.output
    assert "bob" in result.output


def test_log_cmd_respects_limit(runner, audit_dir):
    for i in range(10):
        record_event("set", f"KEY_{i}", profile="default", audit_dir=audit_dir)
    result = runner.invoke(
        audit_cmd,
        ["log", "--profile", "default", "--limit", "3", "--audit-dir", str(audit_dir)],
    )
    assert result.exit_code == 0
    assert "showing 3 of 10" in result.output


def test_clear_cmd_with_confirmation(runner, audit_dir):
    record_event("set", "TOKEN", profile="default", audit_dir=audit_dir)
    result = runner.invoke(
        audit_cmd,
        ["clear", "--profile", "default", "--audit-dir", str(audit_dir)],
        input="y\n",
    )
    assert result.exit_code == 0
    assert "Cleared 1" in result.output


def test_clear_cmd_aborted(runner, audit_dir):
    record_event("set", "TOKEN", profile="default", audit_dir=audit_dir)
    result = runner.invoke(
        audit_cmd,
        ["clear", "--profile", "default", "--audit-dir", str(audit_dir)],
        input="n\n",
    )
    assert result.exit_code != 0 or "Aborted" in result.output


def test_log_cmd_profile_isolation(runner, audit_dir):
    record_event("set", "PROD_KEY", profile="prod", audit_dir=audit_dir)
    result = runner.invoke(
        audit_cmd, ["log", "--profile", "dev", "--audit-dir", str(audit_dir)]
    )
    assert result.exit_code == 0
    assert "No audit events" in result.output
