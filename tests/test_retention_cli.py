"""Tests for envault.retention_cli."""

from __future__ import annotations

import time
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from envault.cli_main import main
from envault.retention import set_retention

META_KEY = "__meta__"


@pytest.fixture()
def runner():
    return CliRunner()


def _invoke(runner, args, input_text="password\n"):
    return runner.invoke(main, args, input=input_text, catch_exceptions=False)


@pytest.fixture(autouse=True)
def _patch_vault(tmp_path):
    vault_file = tmp_path / "default.vault"
    _store = {"vars": {"API_KEY": "abc", "DB_PASS": "secret"}}

    def fake_get_path(profile="default"):
        return vault_file

    def fake_load(path, password):
        return dict(_store["vars"])

    def fake_save(path, variables, password):
        _store["vars"] = dict(variables)

    with patch("envault.retention_cli.get_profile_vault_path", side_effect=fake_get_path), \
         patch("envault.retention_cli.load_profile", side_effect=fake_load), \
         patch("envault.retention_cli.save_profile", side_effect=fake_save):
        yield _store


def test_set_retention_cmd_success(runner, _patch_vault):
    result = _invoke(runner, ["retention", "set", "API_KEY", "30"])
    assert result.exit_code == 0
    assert "30 day" in result.output


def test_set_retention_cmd_missing_key(runner, _patch_vault):
    result = runner.invoke(
        main, ["retention", "set", "MISSING", "7"], input="password\n", catch_exceptions=False
    )
    assert result.exit_code != 0
    assert "MISSING" in result.output


def test_set_retention_cmd_zero_days(runner, _patch_vault):
    result = runner.invoke(
        main, ["retention", "set", "API_KEY", "0"], input="password\n", catch_exceptions=False
    )
    assert result.exit_code != 0


def test_show_retention_cmd_no_policy(runner, _patch_vault):
    result = _invoke(runner, ["retention", "show", "API_KEY"])
    assert result.exit_code == 0
    assert "No retention policy" in result.output


def test_show_retention_cmd_with_policy(runner, _patch_vault):
    _invoke(runner, ["retention", "set", "API_KEY", "14"])
    result = _invoke(runner, ["retention", "show", "API_KEY"])
    assert result.exit_code == 0
    assert "14" in result.output


def test_purge_cmd_no_expired(runner, _patch_vault):
    result = _invoke(runner, ["retention", "purge"])
    assert result.exit_code == 0
    assert "No expired" in result.output


def test_purge_cmd_dry_run_does_not_delete(runner, _patch_vault):
    _invoke(runner, ["retention", "set", "API_KEY", "1"])
    # Backdate the creation timestamp directly in the store
    _patch_vault["vars"][META_KEY]["API_KEY"]["_created_at"] = time.time() - 2 * 86400
    result = _invoke(runner, ["retention", "purge", "--dry-run"])
    assert result.exit_code == 0
    assert "dry-run" in result.output
    assert "API_KEY" in _patch_vault["vars"]
