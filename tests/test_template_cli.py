"""Tests for envault.template_cli."""
from __future__ import annotations

from unittest.mock import patch

import pytest
from click.testing import CliRunner

from envault.template_cli import template_cmd

PROFILE_VARS = {"HOST": "db.local", "PORT": "3306"}


@pytest.fixture()
def runner():
    return CliRunner()


def _invoke(runner: CliRunner, args, **kwargs):
    return runner.invoke(template_cmd, args, catch_exceptions=False, **kwargs)


@patch("envault.template_cli.load_profile", return_value=PROFILE_VARS)
@patch("envault.template_cli.get_profile_vault_path", return_value="/fake/vault")
def test_render_cmd_outputs_to_stdout(mock_path, mock_load, runner, tmp_path):
    tmpl = tmp_path / "tmpl.txt"
    tmpl.write_text("{{HOST}}:{{PORT}}")
    result = _invoke(runner, ["render", str(tmpl), "--password", "secret"])
    assert result.exit_code == 0
    assert "db.local:3306" in result.output


@patch("envault.template_cli.load_profile", return_value=PROFILE_VARS)
@patch("envault.template_cli.get_profile_vault_path", return_value="/fake/vault")
def test_render_cmd_writes_output_file(mock_path, mock_load, runner, tmp_path):
    tmpl = tmp_path / "tmpl.txt"
    out = tmp_path / "out.txt"
    tmpl.write_text("{{HOST}}")
    result = _invoke(runner, ["render", str(tmpl), "-o", str(out), "--password", "secret"])
    assert result.exit_code == 0
    assert out.read_text() == "db.local"
    assert "written to" in result.output


@patch("envault.template_cli.load_profile", return_value=PROFILE_VARS)
@patch("envault.template_cli.get_profile_vault_path", return_value="/fake/vault")
def test_render_cmd_strict_fails_on_unknown(mock_path, mock_load, runner, tmp_path):
    tmpl = tmp_path / "tmpl.txt"
    tmpl.write_text("{{MISSING}}")
    result = runner.invoke(template_cmd, ["render", str(tmpl), "--password", "secret", "--strict"])
    assert result.exit_code != 0
    assert "MISSING" in result.output


def test_placeholders_cmd_lists_keys(runner, tmp_path):
    tmpl = tmp_path / "tmpl.txt"
    tmpl.write_text("{{Z_VAR}} and {{A_VAR}} and {{Z_VAR}}")
    result = _invoke(runner, ["placeholders", str(tmpl)])
    assert result.exit_code == 0
    lines = result.output.strip().splitlines()
    assert lines == ["A_VAR", "Z_VAR"]


def test_placeholders_cmd_no_placeholders(runner, tmp_path):
    tmpl = tmp_path / "tmpl.txt"
    tmpl.write_text("nothing here")
    result = _invoke(runner, ["placeholders", str(tmpl)])
    assert result.exit_code == 0
    assert "No placeholders" in result.output
