"""Tests for envault.acl_cli — CLI surface for ACL management."""

from __future__ import annotations

from unittest.mock import patch

import pytest
from click.testing import CliRunner

from envault.acl_cli import acl_cmd


@pytest.fixture()
def runner():
    return CliRunner()


def _invoke(runner, *args, password="test-pass", **kwargs):
    return runner.invoke(acl_cmd, args, input=f"{password}\n", catch_exceptions=False, **kwargs)


def _base_vars():
    return {"API_KEY": "secret", "DEBUG": "1"}


@patch("envault.acl_cli.save_vault")
@patch("envault.acl_cli.load_vault", return_value={"API_KEY": "secret", "DEBUG": "1"})
@patch("envault.acl_cli.get_vault_path", return_value="/tmp/vault.json")
def test_set_acl_success(mock_path, mock_load, mock_save, runner):
    result = _invoke(runner, "set", "API_KEY", "-r", "reader")
    assert result.exit_code == 0
    assert "ACL set for 'API_KEY'" in result.output
    mock_save.assert_called_once()


@patch("envault.acl_cli.load_vault", return_value={"API_KEY": "secret"})
@patch("envault.acl_cli.get_vault_path", return_value="/tmp/vault.json")
def test_set_acl_invalid_role_fails(mock_path, mock_load, runner):
    result = runner.invoke(acl_cmd, ["set", "API_KEY", "-r", "superuser"], input="pass\n")
    assert result.exit_code != 0
    assert "Invalid roles" in result.output


@patch("envault.acl_cli.load_vault", return_value={"API_KEY": "secret"})
@patch("envault.acl_cli.get_vault_path", return_value="/tmp/vault.json")
def test_set_acl_missing_key_fails(mock_path, mock_load, runner):
    result = runner.invoke(acl_cmd, ["set", "MISSING", "-r", "reader"], input="pass\n")
    assert result.exit_code != 0
    assert "MISSING" in result.output


@patch("envault.acl_cli.save_vault")
@patch("envault.acl_cli.load_vault", return_value={"API_KEY": "secret"})
@patch("envault.acl_cli.get_vault_path", return_value="/tmp/vault.json")
def test_remove_acl_success(mock_path, mock_load, mock_save, runner):
    result = _invoke(runner, "remove", "API_KEY")
    assert result.exit_code == 0
    assert "ACL removed for 'API_KEY'" in result.output


@patch("envault.acl_cli.load_vault")
@patch("envault.acl_cli.get_vault_path", return_value="/tmp/vault.json")
def test_list_acl_no_entries(mock_path, mock_load, runner):
    mock_load.return_value = {"KEY": "val"}
    result = _invoke(runner, "list")
    assert result.exit_code == 0
    assert "No ACL entries" in result.output


@patch("envault.acl_cli.load_vault")
@patch("envault.acl_cli.get_vault_path", return_value="/tmp/vault.json")
def test_check_acl_access_granted(mock_path, mock_load, runner):
    from envault.acl import set_acl
    vars_ = set_acl({"API_KEY": "s"}, "API_KEY", ["reader"])
    mock_load.return_value = vars_
    result = _invoke(runner, "check", "API_KEY", "reader")
    assert result.exit_code == 0
    assert "has access" in result.output


@patch("envault.acl_cli.load_vault")
@patch("envault.acl_cli.get_vault_path", return_value="/tmp/vault.json")
def test_check_acl_access_denied(mock_path, mock_load, runner):
    from envault.acl import set_acl
    vars_ = set_acl({"API_KEY": "s"}, "API_KEY", ["reader"])
    mock_load.return_value = vars_
    result = runner.invoke(acl_cmd, ["check", "API_KEY", "writer"], input="pass\n")
    assert result.exit_code == 1
    assert "does NOT have access" in result.output
