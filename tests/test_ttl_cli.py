"""Tests for envault.ttl_cli module."""

import pytest
from click.testing import CliRunner
from unittest.mock import patch, MagicMock
from pathlib import Path

from envault.ttl_cli import ttl_cmd
from envault.ttl import set_ttl

PASSWORD = "testpass"


@pytest.fixture
def runner():
    return CliRunner()


def _invoke(runner, args, password=PASSWORD):
    return runner.invoke(ttl_cmd, args, input=password + "\n", catch_exceptions=False)


@patch("envault.ttl_cli.save_profile")
@patch("envault.ttl_cli.load_profile", return_value={"API_KEY": "secret"})
@patch("envault.ttl_cli.get_profile_vault_path", return_value=Path("/fake/vault"))
def test_set_ttl_cmd_success(mock_path, mock_load, mock_save, runner):
    result = _invoke(runner, ["set", "API_KEY", "3600"])
    assert result.exit_code == 0
    assert "expires at" in result.output
    mock_save.assert_called_once()


@patch("envault.ttl_cli.load_profile", return_value={"API_KEY": "secret"})
@patch("envault.ttl_cli.get_profile_vault_path", return_value=Path("/fake/vault"))
def test_set_ttl_cmd_missing_key(mock_path, mock_load, runner):
    result = runner.invoke(ttl_cmd, ["set", "MISSING", "60"], input=PASSWORD + "\n")
    assert result.exit_code != 0
    assert "not found" in result.output


@patch("envault.ttl_cli.load_profile")
@patch("envault.ttl_cli.get_profile_vault_path", return_value=Path("/fake/vault"))
def test_show_ttl_cmd_no_ttl(mock_path, mock_load, runner):
    mock_load.return_value = {"API_KEY": "secret"}
    result = _invoke(runner, ["show", "API_KEY"])
    assert result.exit_code == 0
    assert "No TTL" in result.output


@patch("envault.ttl_cli.load_profile")
@patch("envault.ttl_cli.get_profile_vault_path", return_value=Path("/fake/vault"))
def test_show_ttl_cmd_with_ttl(mock_path, mock_load, runner):
    vars_with_ttl = set_ttl({"API_KEY": "secret"}, "API_KEY", 3600)
    mock_load.return_value = vars_with_ttl
    result = _invoke(runner, ["show", "API_KEY"])
    assert result.exit_code == 0
    assert "expires at" in result.output
    assert "remaining" in result.output


@patch("envault.ttl_cli.save_profile")
@patch("envault.ttl_cli.load_profile")
@patch("envault.ttl_cli.get_profile_vault_path", return_value=Path("/fake/vault"))
def test_remove_ttl_cmd(mock_path, mock_load, mock_save, runner):
    vars_with_ttl = set_ttl({"API_KEY": "secret"}, "API_KEY", 3600)
    mock_load.return_value = vars_with_ttl
    result = _invoke(runner, ["remove", "API_KEY"])
    assert result.exit_code == 0
    assert "removed" in result.output
    mock_save.assert_called_once()


@patch("envault.ttl_cli.save_profile")
@patch("envault.ttl_cli.load_profile")
@patch("envault.ttl_cli.get_profile_vault_path", return_value=Path("/fake/vault"))
def test_purge_cmd_removes_expired(mock_path, mock_load, mock_save, runner):
    expired_vars = set_ttl({"OLD_KEY": "val", "LIVE_KEY": "ok"}, "OLD_KEY", -1)
    mock_load.return_value = expired_vars
    result = _invoke(runner, ["purge"])
    assert result.exit_code == 0
    assert "OLD_KEY" in result.output
    assert "Purged 1" in result.output
    mock_save.assert_called_once()


@patch("envault.ttl_cli.load_profile", return_value={"LIVE": "yes"})
@patch("envault.ttl_cli.get_profile_vault_path", return_value=Path("/fake/vault"))
def test_purge_cmd_no_expired(mock_path, mock_load, runner):
    result = _invoke(runner, ["purge"])
    assert result.exit_code == 0
    assert "No expired" in result.output
