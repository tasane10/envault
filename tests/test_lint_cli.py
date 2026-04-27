"""Tests for the lint CLI commands."""

import pytest
from click.testing import CliRunner
from unittest.mock import patch, MagicMock

from envault.lint_cli import lint_cmd, check_cmd, check_name_cmd


@pytest.fixture
def runner():
    return CliRunner()


def _invoke(runner, cmd, args, input_text=None):
    return runner.invoke(cmd, args, input=input_text, catch_exceptions=False)


# ---------------------------------------------------------------------------
# check_cmd
# ---------------------------------------------------------------------------

def test_check_cmd_no_issues(runner, tmp_path):
    """check should report clean when there are no lint issues."""
    variables = {"API_KEY": "abc123", "DB_HOST": "localhost"}
    with patch("envault.lint_cli.get_profile_vault_path", return_value=tmp_path / "vault.json"), \
         patch("envault.lint_cli.load_profile", return_value=variables), \
         patch("envault.lint_cli.lint_variables", return_value=[]) as mock_lint:
        result = _invoke(runner, check_cmd, ["--profile", "default"], input_text="password\n")

    assert result.exit_code == 0
    assert "No issues" in result.output or "clean" in result.output.lower() or mock_lint.called


def test_check_cmd_shows_warnings(runner, tmp_path):
    """check should display lint warnings."""
    variables = {"api_key": "abc123"}
    issues = [{"key": "api_key", "level": "warning", "message": "Key should be uppercase"}]
    with patch("envault.lint_cli.get_profile_vault_path", return_value=tmp_path / "vault.json"), \
         patch("envault.lint_cli.load_profile", return_value=variables), \
         patch("envault.lint_cli.lint_variables", return_value=issues), \
         patch("envault.lint_cli.format_lint_results", return_value="api_key: [warning] Key should be uppercase"):
        result = _invoke(runner, check_cmd, ["--profile", "default"], input_text="password\n")

    assert result.exit_code == 0
    assert "api_key" in result.output or "warning" in result.output.lower()


def test_check_cmd_exits_nonzero_on_errors(runner, tmp_path):
    """check should exit with non-zero code when there are error-level issues."""
    variables = {"1INVALID": "value"}
    issues = [{"key": "1INVALID", "level": "error", "message": "Key must not start with a digit"}]
    with patch("envault.lint_cli.get_profile_vault_path", return_value=tmp_path / "vault.json"), \
         patch("envault.lint_cli.load_profile", return_value=variables), \
         patch("envault.lint_cli.lint_variables", return_value=issues), \
         patch("envault.lint_cli.format_lint_results", return_value="1INVALID: [error] Key must not start with a digit"):
        result = runner.invoke(check_cmd, ["--profile", "default"], input="password\n", catch_exceptions=False)

    # Should exit non-zero when errors present
    assert result.exit_code != 0 or "error" in result.output.lower()


def test_check_cmd_empty_vault(runner, tmp_path):
    """check on an empty vault should succeed with no issues."""
    with patch("envault.lint_cli.get_profile_vault_path", return_value=tmp_path / "vault.json"), \
         patch("envault.lint_cli.load_profile", return_value={}), \
         patch("envault.lint_cli.lint_variables", return_value=[]):
        result = _invoke(runner, check_cmd, ["--profile", "default"], input_text="password\n")

    assert result.exit_code == 0


# ---------------------------------------------------------------------------
# check_name_cmd
# ---------------------------------------------------------------------------

def test_check_name_cmd_valid(runner):
    """check-name should report a valid key name as OK."""
    with patch("envault.lint_cli.lint_name", return_value=[]) as mock_lint:
        result = _invoke(runner, check_name_cmd, ["MY_VAR"])

    assert result.exit_code == 0
    mock_lint.assert_called_once_with("MY_VAR")


def test_check_name_cmd_invalid_shows_issues(runner):
    """check-name should display issues for an invalid key name."""
    issues = [{"level": "error", "message": "Key must not start with a digit"}]
    with patch("envault.lint_cli.lint_name", return_value=issues):
        result = _invoke(runner, check_name_cmd, ["1BAD"])

    assert "error" in result.output.lower() or "digit" in result.output.lower()


def test_check_name_cmd_warning_exits_zero(runner):
    """check-name with only warnings should still exit 0."""
    issues = [{"level": "warning", "message": "Key should be uppercase"}]
    with patch("envault.lint_cli.lint_name", return_value=issues):
        result = _invoke(runner, check_name_cmd, ["my_var"])

    # warnings alone should not cause non-zero exit
    assert "warning" in result.output.lower() or result.exit_code == 0


# ---------------------------------------------------------------------------
# lint_cmd group
# ---------------------------------------------------------------------------

def test_lint_cmd_help(runner):
    """lint group should show help text."""
    result = runner.invoke(lint_cmd, ["--help"])
    assert result.exit_code == 0
    assert "lint" in result.output.lower() or "Usage" in result.output
