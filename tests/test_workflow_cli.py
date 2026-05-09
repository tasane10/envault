"""Tests for envault/workflow_cli.py."""
from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from envault.workflow_cli import workflow_cmd


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def wf_base(tmp_path):
    return tmp_path / "workflows"


def _invoke(runner, args, wf_base):
    with patch("envault.workflow_cli.save_workflow") as mock_save, \
         patch("envault.workflow_cli.load_workflow") as mock_load, \
         patch("envault.workflow_cli.list_workflows") as mock_list, \
         patch("envault.workflow_cli.delete_workflow") as mock_del, \
         patch("envault.workflow_cli.run_workflow") as mock_run:
        yield runner.invoke(workflow_cmd, args), mock_save, mock_load, mock_list, mock_del, mock_run


def test_create_cmd_success(runner, wf_base):
    steps = json.dumps([{"action": "set", "key": "K", "value": "v"}])
    with patch("envault.workflow_cli.save_workflow", return_value=Path("/tmp/deploy.json")) as m:
        result = runner.invoke(workflow_cmd, ["create", "deploy", steps])
    assert result.exit_code == 0
    assert "saved" in result.output
    m.assert_called_once()


def test_create_cmd_bad_json(runner):
    result = runner.invoke(workflow_cmd, ["create", "wf", "not-json"])
    assert result.exit_code != 0
    assert "Invalid JSON" in result.output


def test_create_cmd_invalid_action(runner):
    steps = json.dumps([{"action": "explode", "key": "K"}])
    with patch("envault.workflow_cli.save_workflow", side_effect=ValueError("Unknown action")):
        result = runner.invoke(workflow_cmd, ["create", "wf", steps])
    assert result.exit_code != 0
    assert "Unknown action" in result.output


def test_list_cmd_no_workflows(runner):
    with patch("envault.workflow_cli.list_workflows", return_value=[]):
        result = runner.invoke(workflow_cmd, ["list"])
    assert result.exit_code == 0
    assert "No workflows" in result.output


def test_list_cmd_shows_names(runner):
    with patch("envault.workflow_cli.list_workflows", return_value=["alpha", "beta"]):
        result = runner.invoke(workflow_cmd, ["list"])
    assert "alpha" in result.output
    assert "beta" in result.output


def test_show_cmd_not_found(runner):
    with patch("envault.workflow_cli.load_workflow", side_effect=FileNotFoundError("not found")):
        result = runner.invoke(workflow_cmd, ["show", "ghost"])
    assert result.exit_code != 0


def test_delete_cmd_success(runner):
    with patch("envault.workflow_cli.delete_workflow", return_value=True):
        result = runner.invoke(workflow_cmd, ["delete", "deploy"])
    assert result.exit_code == 0
    assert "deleted" in result.output


def test_delete_cmd_not_found(runner):
    with patch("envault.workflow_cli.delete_workflow", return_value=False):
        result = runner.invoke(workflow_cmd, ["delete", "ghost"])
    assert result.exit_code != 0


def test_run_cmd_success(runner):
    log = [{"action": "set", "key": "X", "status": "ok"}]
    with patch("envault.workflow_cli.run_workflow", return_value=log):
        result = runner.invoke(workflow_cmd, ["run", "deploy", "--vars", '{"X":"old"}'])
    assert result.exit_code == 0
    assert "OK" in result.output
