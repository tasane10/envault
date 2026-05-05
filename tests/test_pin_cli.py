"""Integration tests for the pin CLI commands."""

import pytest
from click.testing import CliRunner
from unittest.mock import patch
from envault.pin_cli import pin_cmd
from envault.pin import pin_variable, META_KEY


@pytest.fixture
def runner():
    return CliRunner()


def _invoke(runner, args, password="secret"):
    return runner.invoke(pin_cmd, args, input=password + "\n", catch_exceptions=False)


@pytest.fixture
def _patched(tmp_path):
    """Patch profile helpers to use tmp_path."""
    vault_file = tmp_path / "default.json.enc"
    base_vars = {"API_KEY": "abc123", "DB_URL": "postgres://localhost"}

    with (
        patch("envault.pin_cli.get_profile_vault_path", return_value=vault_file),
        patch("envault.pin_cli.load_profile", return_value=dict(base_vars)) as mock_load,
        patch("envault.pin_cli.save_profile") as mock_save,
    ):
        yield mock_load, mock_save, base_vars


def test_set_pin_success(runner, _patched):
    mock_load, mock_save, _ = _patched
    result = _invoke(runner, ["set", "API_KEY"])
    assert result.exit_code == 0
    assert "Pinned 'API_KEY'" in result.output
    saved_vars = mock_save.call_args[0][1]
    assert "API_KEY" in saved_vars.get(META_KEY, {}).get("keys", [])


def test_set_pin_missing_key_fails(runner, _patched):
    result = runner.invoke(pin_cmd, ["set", "MISSING"], input="secret\n", catch_exceptions=False)
    assert result.exit_code != 0
    assert "does not exist" in result.output


def test_unpin_success(runner, tmp_path):
    pinned_vars = pin_variable({"API_KEY": "abc"}, "API_KEY")
    vault_file = tmp_path / "default.json.enc"
    with (
        patch("envault.pin_cli.get_profile_vault_path", return_value=vault_file),
        patch("envault.pin_cli.load_profile", return_value=dict(pinned_vars)),
        patch("envault.pin_cli.save_profile") as mock_save,
    ):
        result = _invoke(runner, ["unpin", "API_KEY"])
    assert result.exit_code == 0
    assert "Unpinned 'API_KEY'" in result.output
    saved_vars = mock_save.call_args[0][1]
    assert META_KEY not in saved_vars


def test_list_pins_no_pins(runner, _patched):
    result = _invoke(runner, ["list"])
    assert result.exit_code == 0
    assert "No pinned variables" in result.output


def test_list_pins_shows_pinned(runner, tmp_path):
    pinned_vars = pin_variable({"API_KEY": "abc"}, "API_KEY")
    vault_file = tmp_path / "default.json.enc"
    with (
        patch("envault.pin_cli.get_profile_vault_path", return_value=vault_file),
        patch("envault.pin_cli.load_profile", return_value=dict(pinned_vars)),
    ):
        result = _invoke(runner, ["list"])
    assert result.exit_code == 0
    assert "API_KEY" in result.output


def test_check_pin_is_pinned(runner, tmp_path):
    pinned_vars = pin_variable({"API_KEY": "abc"}, "API_KEY")
    vault_file = tmp_path / "default.json.enc"
    with (
        patch("envault.pin_cli.get_profile_vault_path", return_value=vault_file),
        patch("envault.pin_cli.load_profile", return_value=dict(pinned_vars)),
    ):
        result = _invoke(runner, ["check", "API_KEY"])
    assert "is pinned" in result.output


def test_check_pin_not_pinned(runner, _patched):
    result = _invoke(runner, ["check", "API_KEY"])
    assert "NOT pinned" in result.output
