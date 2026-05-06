"""Tests for envault.compress_cli."""

import json
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest
from click.testing import CliRunner

from envault.compress_cli import compress_cmd
from envault.compress import compress_variables


@pytest.fixture()
def runner():
    return CliRunner()


def _invoke(runner, *args, **kwargs):
    return runner.invoke(compress_cmd, args, catch_exceptions=False, **kwargs)


_SAMPLE_VARS = {"API_KEY": "abc123", "PORT": "8080"}
_PASSWORD = "hunter2"


def test_pack_cmd_outputs_blob(runner, tmp_path):
    with patch("envault.compress_cli.prompt_password", return_value=_PASSWORD), \
         patch("envault.compress_cli.load_profile", return_value=_SAMPLE_VARS):
        result = _invoke(runner, "pack", "--profile", "default")
    assert result.exit_code == 0
    blob = result.output.strip()
    from envault.compress import decompress_variables
    recovered = decompress_variables(blob)
    assert recovered == _SAMPLE_VARS


def test_pack_cmd_writes_output_file(runner, tmp_path):
    out_file = tmp_path / "vault.blob"
    with patch("envault.compress_cli.prompt_password", return_value=_PASSWORD), \
         patch("envault.compress_cli.load_profile", return_value=_SAMPLE_VARS):
        result = _invoke(runner, "pack", "--profile", "default", "--output", str(out_file))
    assert result.exit_code == 0
    assert out_file.exists()
    assert "Packed" in result.output


def test_unpack_cmd_imports_variables(runner, tmp_path):
    blob_file = tmp_path / "vault.blob"
    blob_file.write_text(compress_variables(_SAMPLE_VARS))

    existing = {"OLD_KEY": "oldval"}
    saved = {}

    def fake_save(path, password, variables):
        saved.update(variables)

    with patch("envault.compress_cli.prompt_password", return_value=_PASSWORD), \
         patch("envault.compress_cli.load_profile", return_value=existing), \
         patch("envault.compress_cli.get_profile_vault_path", return_value=tmp_path / "v.enc"), \
         patch("envault.compress_cli.save_vault", side_effect=fake_save):
        result = _invoke(runner, "unpack", str(blob_file), "--profile", "default")

    assert result.exit_code == 0
    assert "Imported" in result.output
    assert saved["API_KEY"] == "abc123"


def test_unpack_cmd_skips_existing_without_overwrite(runner, tmp_path):
    blob_file = tmp_path / "vault.blob"
    blob_file.write_text(compress_variables(_SAMPLE_VARS))

    existing = {"API_KEY": "original"}
    saved = {}

    def fake_save(path, password, variables):
        saved.update(variables)

    with patch("envault.compress_cli.prompt_password", return_value=_PASSWORD), \
         patch("envault.compress_cli.load_profile", return_value=existing), \
         patch("envault.compress_cli.get_profile_vault_path", return_value=tmp_path / "v.enc"), \
         patch("envault.compress_cli.save_vault", side_effect=fake_save):
        result = _invoke(runner, "unpack", str(blob_file), "--profile", "default")

    assert result.exit_code == 0
    assert "skipped 1" in result.output
    assert saved["API_KEY"] == "original"


def test_unpack_cmd_bad_blob_exits(runner, tmp_path):
    bad_file = tmp_path / "bad.blob"
    bad_file.write_text("THIS IS NOT A VALID BLOB")

    with patch("envault.compress_cli.prompt_password", return_value=_PASSWORD):
        result = runner.invoke(compress_cmd, ["unpack", str(bad_file)], catch_exceptions=False)

    assert result.exit_code != 0
