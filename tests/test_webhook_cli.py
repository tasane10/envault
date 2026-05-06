"""Tests for envault.webhook_cli."""
from __future__ import annotations

from unittest.mock import patch, MagicMock

import pytest
from click.testing import CliRunner

from envault.webhook_cli import webhook_cmd

BASE_VARS: dict = {"FOO": "bar"}
PASSWORD = "secret"


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


def _invoke(runner: CliRunner, args: list, input_text: str = ""):
    return runner.invoke(webhook_cmd, args, input=input_text, catch_exceptions=False)


def _patch(variables=None):
    if variables is None:
        variables = dict(BASE_VARS)
    load = patch("envault.webhook_cli.load_vault", return_value=variables)
    save = patch("envault.webhook_cli.save_vault")
    return load, save


def test_add_cmd_success(runner):
    load, save = _patch()
    with load, save as mock_save:
        result = _invoke(runner, ["add", "set", "https://hook.example.com", "--password", PASSWORD])
    assert result.exit_code == 0
    assert "Webhook added" in result.output
    assert mock_save.called


def test_add_cmd_invalid_event_fails(runner):
    result = runner.invoke(webhook_cmd, ["add", "invalid_event", "https://x.com", "--password", PASSWORD])
    assert result.exit_code != 0


def test_remove_cmd_success(runner):
    url = "https://hook.example.com"
    from envault.webhook import set_webhook
    variables = set_webhook(dict(BASE_VARS), "set", url)
    load, save = _patch(variables)
    with load, save:
        result = _invoke(runner, ["remove", "set", url, "--password", PASSWORD])
    assert result.exit_code == 0
    assert "Webhook removed" in result.output


def test_list_cmd_no_webhooks(runner):
    load, save = _patch()
    with load, save:
        result = _invoke(runner, ["list", "--password", PASSWORD])
    assert result.exit_code == 0
    assert "No webhooks" in result.output


def test_list_cmd_shows_entries(runner):
    from envault.webhook import set_webhook
    variables = set_webhook(dict(BASE_VARS), "rotate", "https://notify.example.com")
    load, save = _patch(variables)
    with load, save:
        result = _invoke(runner, ["list", "--password", PASSWORD])
    assert "rotate" in result.output
    assert "https://notify.example.com" in result.output


def test_fire_cmd_no_webhooks_message(runner):
    load, save = _patch()
    with load, save:
        result = _invoke(runner, ["fire", "import", "--password", PASSWORD])
    assert result.exit_code == 0
    assert "No webhooks" in result.output


def test_fire_cmd_reports_results(runner):
    from envault.webhook import set_webhook
    variables = set_webhook(dict(BASE_VARS), "import", "https://hook.example.com")
    load, save = _patch(variables)
    with load, save:
        with patch("envault.webhook.fire_webhook", return_value=True):
            result = _invoke(runner, ["fire", "import", "--password", PASSWORD])
    assert result.exit_code == 0
    assert "https://hook.example.com" in result.output
