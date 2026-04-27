"""Tests for envault.rotate_cli."""

import pytest
from click.testing import CliRunner
from unittest.mock import patch

from envault.rotate_cli import rotate_cmd


@pytest.fixture()
def runner():
    return CliRunner()


def _invoke(runner, args, input_text):
    return runner.invoke(rotate_cmd, args, input=input_text, catch_exceptions=False)


def test_rotate_key_success(runner):
    summary = {"profile": "default", "rotated": 3}
    with patch("envault.rotate_cli.rotate_key", return_value=summary) as mock_rot:
        result = _invoke(runner, ["key", "--profile", "default"], "old\nnew\nnew\n")
    assert result.exit_code == 0
    assert "rotated" in result.output
    assert "default" in result.output
    mock_rot.assert_called_once()


def test_rotate_key_mismatched_confirmation(runner):
    result = _invoke(runner, ["key"], "old\nnew\ndifferent\n")
    assert result.exit_code == 1
    assert "do not match" in result.output


def test_rotate_key_same_password_rejected(runner):
    result = _invoke(runner, ["key"], "same\nsame\nsame\n")
    assert result.exit_code == 1
    assert "must differ" in result.output


def test_rotate_key_wrong_old_password(runner):
    with patch("envault.rotate_cli.rotate_key", side_effect=ValueError("bad password")):
        result = _invoke(runner, ["key"], "wrong\nnew\nnew\n")
    assert result.exit_code == 1
    assert "Error" in result.output


def test_rotate_key_all_profiles(runner):
    summaries = [
        {"profile": "default", "rotated": 1},
        {"profile": "prod", "rotated": 2},
    ]
    with patch("envault.rotate_cli.rotate_key_all_profiles", return_value=summaries):
        result = _invoke(runner, ["key", "--all-profiles"], "old\nnew\nnew\n")
    assert result.exit_code == 0
    assert "default" in result.output
    assert "prod" in result.output
