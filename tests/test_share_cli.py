"""Integration tests for envault.share_cli."""

from __future__ import annotations

import json
import os
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from envault.share_cli import share_cmd

VAULT_PASSWORD = "vaultpass"
SHARE_PASSWORD = "sharepass"

SAMPLE_VARS = {"API_KEY": "abc123", "DEBUG": "true"}


@pytest.fixture()
def runner():
    return CliRunner()


def _invoke(runner, *args, **kwargs):
    return runner.invoke(share_cmd, *args, catch_exceptions=False, **kwargs)


# ---------------------------------------------------------------------------
# create
# ---------------------------------------------------------------------------

def test_create_cmd_writes_bundle_file(runner, tmp_path):
    out = str(tmp_path / "bundle.json")
    with patch("envault.share_cli.load_profile", return_value=SAMPLE_VARS):
        result = _invoke(
            runner,
            ["create", "--output", out,
             "--password", VAULT_PASSWORD,
             "--share-password", SHARE_PASSWORD],
        )
    assert result.exit_code == 0, result.output
    assert os.path.exists(out)
    with open(out) as fh:
        data = json.load(fh)
    assert "token" in data
    assert "payload" in data


def test_create_cmd_bad_vault_password_exits(runner, tmp_path):
    out = str(tmp_path / "bundle.json")
    with patch("envault.share_cli.load_profile", side_effect=ValueError("bad pw")):
        result = runner.invoke(
            share_cmd,
            ["create", "--output", out,
             "--password", "wrong",
             "--share-password", SHARE_PASSWORD],
        )
    assert result.exit_code != 0


# ---------------------------------------------------------------------------
# import
# ---------------------------------------------------------------------------

def test_import_cmd_adds_variables(runner, tmp_path):
    from envault.share import bundle_to_file, create_share_bundle

    bundle_path = str(tmp_path / "bundle.json")
    bundle = create_share_bundle(SAMPLE_VARS, SHARE_PASSWORD)
    bundle_to_file(bundle, bundle_path)

    with patch("envault.share_cli.load_profile", return_value={}), \
         patch("envault.share_cli.save_profile") as mock_save:
        result = _invoke(
            runner,
            ["import", bundle_path,
             "--password", VAULT_PASSWORD,
             "--share-password", SHARE_PASSWORD],
        )
    assert result.exit_code == 0, result.output
    assert "Imported 2" in result.output
    mock_save.assert_called_once()


def test_import_cmd_skips_existing_without_overwrite(runner, tmp_path):
    from envault.share import bundle_to_file, create_share_bundle

    bundle_path = str(tmp_path / "bundle.json")
    bundle = create_share_bundle(SAMPLE_VARS, SHARE_PASSWORD)
    bundle_to_file(bundle, bundle_path)

    existing = {"API_KEY": "old_value"}
    with patch("envault.share_cli.load_profile", return_value=existing), \
         patch("envault.share_cli.save_profile"):
        result = _invoke(
            runner,
            ["import", bundle_path,
             "--password", VAULT_PASSWORD,
             "--share-password", SHARE_PASSWORD],
        )
    assert "skipped 1" in result.output


# ---------------------------------------------------------------------------
# inspect
# ---------------------------------------------------------------------------

def test_inspect_cmd_shows_token(runner, tmp_path):
    from envault.share import bundle_to_file, create_share_bundle

    bundle_path = str(tmp_path / "bundle.json")
    bundle = create_share_bundle(SAMPLE_VARS, SHARE_PASSWORD)
    bundle_to_file(bundle, bundle_path)

    result = _invoke(runner, ["inspect", bundle_path])
    assert result.exit_code == 0
    assert bundle["token"] in result.output
    assert "never" in result.output


def test_inspect_cmd_missing_file_exits(runner, tmp_path):
    result = runner.invoke(share_cmd, ["inspect", str(tmp_path / "nope.json")])
    assert result.exit_code != 0
