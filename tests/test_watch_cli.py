"""Tests for envault.watch_cli."""

import pytest
from click.testing import CliRunner

from envault.watch_cli import watch_cmd


@pytest.fixture()
def runner():
    return CliRunner()


def _invoke(runner, *args, password="secret", **kwargs):
    return runner.invoke(watch_cmd, list(args), input=f"{password}\n", catch_exceptions=False, **kwargs)


def test_start_cmd_exits_on_bad_password(runner, monkeypatch):
    monkeypatch.setattr(
        "envault.watch_cli.load_profile",
        lambda profile, password: (_ for _ in ()).throw(ValueError("bad password")),
    )
    result = runner.invoke(watch_cmd, ["start", "--profile", "default"], input="wrong\n")
    assert result.exit_code != 0 or "Error" in result.output


def test_start_cmd_stops_on_keyboard_interrupt(runner, monkeypatch):
    monkeypatch.setattr("envault.watch_cli.load_profile", lambda p, pw: {"A": "1"})
    monkeypatch.setattr(
        "envault.watch_cli.watch_profile",
        lambda *a, **kw: (_ for _ in ()).throw(KeyboardInterrupt()),
    )
    result = runner.invoke(watch_cmd, ["start", "--profile", "default"], input="secret\n")
    assert "Stopped watching" in result.output


def test_diff_cmd_no_snapshots(runner, monkeypatch):
    monkeypatch.setattr("envault.watch_cli.load_profile", lambda p, pw: {"A": "1"})
    monkeypatch.setattr("envault.watch_cli.list_snapshots", lambda p: [])
    result = runner.invoke(
        watch_cmd, ["diff", "--profile", "default", "--snapshot", "snap1"], input="secret\n"
    )
    assert result.exit_code != 0
    assert "not found" in result.output


def test_diff_cmd_no_differences(runner, monkeypatch):
    vars_ = {"A": "1"}
    monkeypatch.setattr("envault.watch_cli.load_profile", lambda p, pw: vars_)
    monkeypatch.setattr("envault.watch_cli.list_snapshots", lambda p: ["snap1"])
    monkeypatch.setattr(
        "envault.watch_cli.restore_snapshot",
        lambda p, s, pw, dry_run=False: vars_.copy(),
    )
    monkeypatch.setattr("envault.watch_cli.diff_variables", lambda a, b: [])
    monkeypatch.setattr("envault.watch_cli.format_diff", lambda r: "")
    result = runner.invoke(
        watch_cmd, ["diff", "--profile", "default", "--snapshot", "snap1"], input="secret\n"
    )
    assert result.exit_code == 0
    assert "No differences" in result.output
