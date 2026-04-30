import pytest
from unittest.mock import patch, MagicMock
from click.testing import CliRunner
from envault.remote_cli import remote_cmd
from envault.remote import RemoteError


@pytest.fixture
def runner():
    return CliRunner()


def _invoke(runner, args, input_text="password\n"):
    return runner.invoke(remote_cmd, args, input=input_text, catch_exceptions=False)


BASE_ARGS = ["--url", "http://localhost:8000", "--token", "tok123"]


@patch("envault.remote_cli.save_profile")
@patch("envault.remote_cli.pull_variables")
@patch("envault.remote_cli.load_profile")
def test_pull_cmd_adds_new_keys(mock_load, mock_pull, mock_save, runner):
    mock_load.return_value = {"EXISTING": "val"}
    mock_pull.return_value = {"NEW_KEY": "new_val", "EXISTING": "remote_val"}

    result = _invoke(runner, ["pull"] + BASE_ARGS)

    assert result.exit_code == 0
    assert "Pulled 1 variable(s)" in result.output
    assert "Skipped 1 existing" in result.output
    saved = mock_save.call_args[0][1]
    assert saved["NEW_KEY"] == "new_val"
    assert saved["EXISTING"] == "val"  # not overwritten


@patch("envault.remote_cli.save_profile")
@patch("envault.remote_cli.pull_variables")
@patch("envault.remote_cli.load_profile")
def test_pull_cmd_overwrite_flag(mock_load, mock_pull, mock_save, runner):
    mock_load.return_value = {"EXISTING": "old"}
    mock_pull.return_value = {"EXISTING": "new"}

    result = _invoke(runner, ["pull", "--overwrite"] + BASE_ARGS)

    assert result.exit_code == 0
    assert "Pulled 1 variable(s)" in result.output
    saved = mock_save.call_args[0][1]
    assert saved["EXISTING"] == "new"


@patch("envault.remote_cli.pull_variables")
@patch("envault.remote_cli.load_profile")
def test_pull_cmd_remote_error(mock_load, mock_pull, runner):
    mock_load.return_value = {}
    mock_pull.side_effect = RemoteError("connection refused")

    result = runner.invoke(remote_cmd, ["pull"] + BASE_ARGS, input="password\n")

    assert result.exit_code != 0
    assert "connection refused" in result.output


@patch("envault.remote_cli.push_variables")
@patch("envault.remote_cli.load_profile")
def test_push_cmd_success(mock_load, mock_push, runner):
    mock_load.return_value = {"KEY1": "val1", "KEY2": "val2"}
    mock_push.return_value = {"pushed": 2, "skipped": 0}

    result = _invoke(runner, ["push"] + BASE_ARGS)

    assert result.exit_code == 0
    assert "Pushed 2 variable(s)" in result.output


@patch("envault.remote_cli.push_variables")
@patch("envault.remote_cli.load_profile")
def test_push_cmd_with_key_filter(mock_load, mock_push, runner):
    mock_load.return_value = {"A": "1", "B": "2"}
    mock_push.return_value = {"pushed": 1, "skipped": 0}

    result = _invoke(runner, ["push", "--keys", "A"] + BASE_ARGS)

    assert result.exit_code == 0
    call_kwargs = mock_push.call_args[1]
    assert call_kwargs["keys"] == ["A"]


@patch("envault.remote_cli.load_profile")
def test_push_cmd_bad_password(mock_load, runner):
    mock_load.side_effect = ValueError("wrong password")

    result = runner.invoke(remote_cmd, ["push"] + BASE_ARGS, input="badpass\n")

    assert result.exit_code != 0
    assert "Failed to load profile" in result.output
