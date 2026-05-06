"""Tests for envault.quota_cli."""

from __future__ import annotations

from unittest.mock import patch, MagicMock

import pytest
from click.testing import CliRunner

from envault.quota_cli import quota_cmd


@pytest.fixture()
def runner():
    return CliRunner()


def _invoke(runner, *args, password="secret"):
    with patch("envault.quota_cli.prompt_password", return_value=password), \
         patch("envault.quota_cli.load_profile") as mock_load, \
         patch("envault.quota_cli.save_profile") as mock_save:
        result = runner.invoke(quota_cmd, list(args))
        return result, mock_load, mock_save


def test_set_quota_success(runner):
    with patch("envault.quota_cli.prompt_password", return_value="pw"), \
         patch("envault.quota_cli.load_profile", return_value={"A": "1"}) as ml, \
         patch("envault.quota_cli.save_profile") as ms:
        result = runner.invoke(quota_cmd, ["set", "50", "--profile", "default"])
    assert result.exit_code == 0
    assert "Quota set to 50" in result.output


def test_set_quota_invalid_limit(runner):
    with patch("envault.quota_cli.prompt_password", return_value="pw"), \
         patch("envault.quota_cli.load_profile", return_value={}):
        result = runner.invoke(quota_cmd, ["set", "0", "--profile", "default"])
    assert result.exit_code != 0
    assert "positive" in result.output.lower() or "Error" in result.output


def test_remove_quota_success(runner):
    with patch("envault.quota_cli.prompt_password", return_value="pw"), \
         patch("envault.quota_cli.load_profile", return_value={"__quota__": {"limit": 10}, "X": "1"}) as ml, \
         patch("envault.quota_cli.save_profile") as ms:
        result = runner.invoke(quota_cmd, ["remove", "--profile", "default"])
    assert result.exit_code == 0
    assert "removed" in result.output
    saved_vars = ms.call_args[0][1]
    assert "__quota__" not in saved_vars


def test_show_quota_no_limit(runner):
    with patch("envault.quota_cli.prompt_password", return_value="pw"), \
         patch("envault.quota_cli.load_profile", return_value={"A": "1", "B": "2"}):
        result = runner.invoke(quota_cmd, ["show", "--profile", "default"])
    assert result.exit_code == 0
    assert "unlimited" in result.output
    assert "Current" in result.output


def test_show_quota_with_limit(runner):
    from envault.quota import set_quota
    vars_with_quota = set_quota({"A": "1", "B": "2"}, 10)
    with patch("envault.quota_cli.prompt_password", return_value="pw"), \
         patch("envault.quota_cli.load_profile", return_value=vars_with_quota):
        result = runner.invoke(quota_cmd, ["show", "--profile", "default"])
    assert result.exit_code == 0
    assert "10" in result.output
    assert "8" in result.output  # remaining
