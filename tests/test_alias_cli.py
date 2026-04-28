"""Integration tests for alias CLI commands."""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from envault.alias_cli import alias_cmd
from envault.profiles import get_profile_vault_path, save_profile

PASSWORD = "test-pass"


@pytest.fixture()
def runner():
    return CliRunner()


def _invoke(runner, tmp_path, args, password=PASSWORD):
    """Run alias_cmd with a temp vault base directory."""
    import envault.profiles as prof_mod

    monkeypatch_base = tmp_path / "vaults"
    monkeypatch_base.mkdir()

    original_get = prof_mod.get_profile_vault_path

    def _patched_path(profile="default"):
        return monkeypatch_base / f"{profile}.vault"

    prof_mod.get_profile_vault_path = _patched_path

    # Pre-seed vault with some variables
    vault_path = _patched_path("default")
    save_profile(vault_path, {"DB_URL": "postgres://localhost", "API_KEY": "s"}, PASSWORD)

    result = runner.invoke(alias_cmd, args, input=f"{password}\n")
    prof_mod.get_profile_vault_path = original_get
    return result


def test_set_alias_success(runner, tmp_path):
    result = _invoke(runner, tmp_path, ["set", "db", "DB_URL"])
    assert result.exit_code == 0
    assert "db" in result.output
    assert "DB_URL" in result.output


def test_set_alias_missing_key_fails(runner, tmp_path):
    result = _invoke(runner, tmp_path, ["set", "x", "MISSING_VAR"])
    assert result.exit_code != 0
    assert "MISSING_VAR" in result.output


def test_remove_alias_success(runner, tmp_path):
    import envault.profiles as prof_mod

    monkeypatch_base = tmp_path / "vaults2"
    monkeypatch_base.mkdir()
    original_get = prof_mod.get_profile_vault_path

    def _patched_path(profile="default"):
        return monkeypatch_base / f"{profile}.vault"

    prof_mod.get_profile_vault_path = _patched_path

    from envault.alias import set_alias

    v = set_alias({"DB_URL": "x"}, "db", "DB_URL")
    save_profile(_patched_path("default"), v, PASSWORD)

    result = runner.invoke(alias_cmd, ["remove", "db"], input=f"{PASSWORD}\n")
    prof_mod.get_profile_vault_path = original_get
    assert result.exit_code == 0
    assert "removed" in result.output


def test_list_aliases_empty(runner, tmp_path):
    result = _invoke(runner, tmp_path, ["list"])
    assert result.exit_code == 0
    assert "No aliases" in result.output


def test_list_aliases_shows_entries(runner, tmp_path):
    import envault.profiles as prof_mod
    from envault.alias import set_alias

    monkeypatch_base = tmp_path / "vaults3"
    monkeypatch_base.mkdir()
    original_get = prof_mod.get_profile_vault_path

    def _patched_path(profile="default"):
        return monkeypatch_base / f"{profile}.vault"

    prof_mod.get_profile_vault_path = _patched_path

    v = {"DB_URL": "postgres://localhost"}
    v = set_alias(v, "db", "DB_URL")
    save_profile(_patched_path("default"), v, PASSWORD)

    result = runner.invoke(alias_cmd, ["list"], input=f"{PASSWORD}\n")
    prof_mod.get_profile_vault_path = original_get
    assert result.exit_code == 0
    assert "db" in result.output
    assert "DB_URL" in result.output
