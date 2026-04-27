import pytest
from click.testing import CliRunner
from unittest.mock import patch, MagicMock
from envault.copy_cli import copy_cmd


@pytest.fixture
def runner():
    return CliRunner()


def _invoke(runner, args, inputs=None):
    return runner.invoke(copy_cmd, args, input=inputs, catch_exceptions=False)


@patch("envault.copy_cli.save_profile")
@patch("envault.copy_cli.copy_profile", return_value=(3, 0))
@patch("envault.copy_cli.prompt_password", side_effect=["srcpass", "dstpass"])
def test_copy_profile_success(mock_pw, mock_copy, mock_save, runner):
    result = _invoke(runner, ["profile", "dev", "staging"])
    assert result.exit_code == 0
    assert "Copied 3 variable(s)" in result.output
    mock_copy.assert_called_once_with("dev", "srcpass", "staging", "dstpass", overwrite=False)


@patch("envault.copy_cli.save_profile")
@patch("envault.copy_cli.copy_profile", return_value=(2, 1))
@patch("envault.copy_cli.prompt_password", side_effect=["srcpass", "dstpass"])
def test_copy_profile_shows_skipped(mock_pw, mock_copy, mock_save, runner):
    result = _invoke(runner, ["profile", "dev", "staging"])
    assert result.exit_code == 0
    assert "Skipped 1 existing key(s)" in result.output


@patch("envault.copy_cli.copy_profile", side_effect=ValueError("Bad password"))
@patch("envault.copy_cli.prompt_password", side_effect=["wrong", "dstpass"])
def test_copy_profile_bad_password(mock_pw, mock_copy, runner):
    result = runner.invoke(copy_cmd, ["profile", "dev", "staging"], catch_exceptions=False)
    assert result.exit_code != 0
    assert "Bad password" in result.output


@patch("envault.copy_cli.save_profile")
@patch("envault.copy_cli.load_profile", side_effect=[{"KEY": "val"}, {}])
@patch("envault.copy_cli.prompt_password", side_effect=["srcpass", "dstpass"])
def test_copy_var_success(mock_pw, mock_load, mock_save, runner):
    result = _invoke(runner, ["var", "KEY", "dev", "staging"])
    assert result.exit_code == 0
    assert "Copied 'KEY'" in result.output
    mock_save.assert_called_once_with("staging", {"KEY": "val"}, "dstpass")


@patch("envault.copy_cli.load_profile", return_value={"OTHER": "val"})
@patch("envault.copy_cli.prompt_password", side_effect=["srcpass", "dstpass"])
def test_copy_var_key_not_found(mock_pw, mock_load, runner):
    result = runner.invoke(copy_cmd, ["var", "MISSING", "dev", "staging"], catch_exceptions=False)
    assert result.exit_code != 0
    assert "not found" in result.output


@patch("envault.copy_cli.save_profile")
@patch("envault.copy_cli.load_profile", side_effect=[{"KEY": "new"}, {"KEY": "old"}])
@patch("envault.copy_cli.prompt_password", side_effect=["srcpass", "dstpass"])
def test_copy_var_no_overwrite_raises(mock_pw, mock_load, mock_save, runner):
    result = runner.invoke(copy_cmd, ["var", "KEY", "dev", "staging"], catch_exceptions=False)
    assert result.exit_code != 0
    assert "already exists" in result.output
    mock_save.assert_not_called()


@patch("envault.copy_cli.save_profile")
@patch("envault.copy_cli.load_profile", side_effect=[{"KEY": "new"}, {"KEY": "old"}])
@patch("envault.copy_cli.prompt_password", side_effect=["srcpass", "dstpass"])
def test_copy_var_with_overwrite(mock_pw, mock_load, mock_save, runner):
    result = _invoke(runner, ["var", "KEY", "dev", "staging", "--overwrite"])
    assert result.exit_code == 0
    assert "Copied 'KEY'" in result.output
    mock_save.assert_called_once_with("staging", {"KEY": "new"}, "dstpass")
