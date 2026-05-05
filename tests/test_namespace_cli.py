"""Tests for envault.namespace_cli."""

from unittest.mock import patch

import pytest
from click.testing import CliRunner

from envault.namespace_cli import namespace_cmd


@pytest.fixture()
def runner():
    return CliRunner()


def _invoke(runner, args, password="secret", variables=None):
    if variables is None:
        variables = {}
    with patch("envault.namespace_cli.prompt_password", return_value=password), \
         patch("envault.namespace_cli.load_profile", return_value=variables), \
         patch("envault.namespace_cli.save_profile") as mock_save:
        result = runner.invoke(namespace_cmd, args, catch_exceptions=False)
        return result, mock_save


SAMPLE = {
    "APP_HOST": "localhost",
    "APP_PORT": "8080",
    "DB_URL": "postgres://localhost/db",
}


def test_list_cmd_shows_namespaces(runner):
    result, _ = _invoke(runner, ["list"], variables=SAMPLE)
    assert result.exit_code == 0
    assert "APP" in result.output
    assert "DB" in result.output


def test_list_cmd_no_namespaces_message(runner):
    result, _ = _invoke(runner, ["list"], variables={"STANDALONE": "yes"})
    assert result.exit_code == 0
    assert "No namespaces found" in result.output


def test_filter_cmd_shows_matching_keys(runner):
    result, _ = _invoke(runner, ["filter", "APP"], variables=SAMPLE)
    assert result.exit_code == 0
    assert "APP_HOST=localhost" in result.output
    assert "APP_PORT=8080" in result.output
    assert "DB_URL" not in result.output


def test_filter_cmd_strip_flag_removes_prefix(runner):
    result, _ = _invoke(runner, ["filter", "APP", "--strip"], variables=SAMPLE)
    assert result.exit_code == 0
    assert "HOST=localhost" in result.output
    assert "APP_HOST" not in result.output


def test_filter_cmd_no_match_message(runner):
    result, _ = _invoke(runner, ["filter", "MISSING"], variables=SAMPLE)
    assert result.exit_code == 0
    assert "No variables found" in result.output


def test_move_cmd_renames_and_saves(runner):
    result, mock_save = _invoke(runner, ["move", "APP", "SVC"], variables=SAMPLE)
    assert result.exit_code == 0
    assert "Moved 2" in result.output
    mock_save.assert_called_once()
    saved_vars = mock_save.call_args[0][1]
    assert "SVC_HOST" in saved_vars
    assert "APP_HOST" not in saved_vars


def test_move_cmd_no_match_message(runner):
    result, mock_save = _invoke(runner, ["move", "GHOST", "NEW"], variables=SAMPLE)
    assert result.exit_code == 0
    assert "No variables found" in result.output
    mock_save.assert_not_called()
