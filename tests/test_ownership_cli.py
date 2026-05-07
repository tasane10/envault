"""Tests for envault.ownership_cli."""

from __future__ import annotations

from unittest.mock import patch

import pytest
from click.testing import CliRunner

from envault.ownership_cli import ownership_cmd


@pytest.fixture()
def runner():
    return CliRunner()


def _invoke(runner, args, password="pass"):
    with patch("envault.ownership_cli.prompt_password", return_value=password):
        return runner.invoke(ownership_cmd, args, catch_exceptions=False)


_BASE = {"API_KEY": "secret", "DB_PASS": "hunter2"}


def test_set_owner_success(runner, tmp_path):
    with (
        patch("envault.ownership_cli.get_vault_path", return_value=tmp_path / "v.json"),
        patch("envault.ownership_cli.load_vault", return_value=dict(_BASE)),
        patch("envault.ownership_cli.save_vault") as mock_save,
    ):
        result = _invoke(runner, ["set", "API_KEY", "alice"])
    assert result.exit_code == 0
    assert "alice" in result.output
    mock_save.assert_called_once()


def test_set_owner_missing_key_fails(runner, tmp_path):
    with (
        patch("envault.ownership_cli.get_vault_path", return_value=tmp_path / "v.json"),
        patch("envault.ownership_cli.load_vault", return_value=dict(_BASE)),
        patch("envault.ownership_cli.save_vault"),
    ):
        result = _invoke(runner, ["set", "MISSING", "alice"])
    assert result.exit_code != 0
    assert "MISSING" in result.output


def test_remove_owner_success(runner, tmp_path):
    from envault.ownership import set_owner
    vars_with_owner = set_owner(_BASE, "API_KEY", "alice")
    with (
        patch("envault.ownership_cli.get_vault_path", return_value=tmp_path / "v.json"),
        patch("envault.ownership_cli.load_vault", return_value=vars_with_owner),
        patch("envault.ownership_cli.save_vault") as mock_save,
    ):
        result = _invoke(runner, ["remove", "API_KEY"])
    assert result.exit_code == 0
    assert "removed" in result.output
    mock_save.assert_called_once()


def test_show_owner_with_owner(runner, tmp_path):
    from envault.ownership import set_owner
    vars_with_owner = set_owner(_BASE, "API_KEY", "bob")
    with (
        patch("envault.ownership_cli.get_vault_path", return_value=tmp_path / "v.json"),
        patch("envault.ownership_cli.load_vault", return_value=vars_with_owner),
    ):
        result = _invoke(runner, ["show", "API_KEY"])
    assert result.exit_code == 0
    assert "bob" in result.output


def test_show_owner_no_owner(runner, tmp_path):
    with (
        patch("envault.ownership_cli.get_vault_path", return_value=tmp_path / "v.json"),
        patch("envault.ownership_cli.load_vault", return_value=dict(_BASE)),
    ):
        result = _invoke(runner, ["show", "API_KEY"])
    assert result.exit_code == 0
    assert "no owner" in result.output


def test_list_owners_all(runner, tmp_path):
    from envault.ownership import set_owner
    v = set_owner(_BASE, "API_KEY", "carol")
    with (
        patch("envault.ownership_cli.get_vault_path", return_value=tmp_path / "v.json"),
        patch("envault.ownership_cli.load_vault", return_value=v),
    ):
        result = _invoke(runner, ["list"])
    assert result.exit_code == 0
    assert "carol" in result.output


def test_list_owners_filter_by_owner(runner, tmp_path):
    from envault.ownership import set_owner
    v = set_owner(_BASE, "API_KEY", "alice")
    v = set_owner(v, "DB_PASS", "bob")
    with (
        patch("envault.ownership_cli.get_vault_path", return_value=tmp_path / "v.json"),
        patch("envault.ownership_cli.load_vault", return_value=v),
    ):
        result = _invoke(runner, ["list", "--owner", "alice"])
    assert result.exit_code == 0
    assert "API_KEY" in result.output
    assert "DB_PASS" not in result.output
