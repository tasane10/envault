"""Tests for envault.hook and envault.hook_cli."""

from __future__ import annotations

import os
import stat
from pathlib import Path
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from envault.hook import (
    HOOK_EVENTS,
    get_hook_path,
    get_hooks_dir,
    install_hook,
    list_hooks,
    remove_hook,
    run_hook,
)
from envault.hook_cli import hook_cmd


@pytest.fixture()
def hooks_base(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVAULT_HOME", str(tmp_path))
    return tmp_path


# --- unit tests for hook.py ---

def test_get_hooks_dir_uses_envault_home(hooks_base):
    d = get_hooks_dir("default")
    assert str(hooks_base) in str(d)
    assert "hooks" in str(d)


def test_install_hook_creates_executable(hooks_base):
    path = install_hook("post-set", "#!/bin/sh\necho hello\n")
    assert path.exists()
    assert path.stat().st_mode & stat.S_IEXEC


def test_install_hook_unknown_event_raises(hooks_base):
    with pytest.raises(ValueError, match="Unknown hook event"):
        install_hook("on-moon-landing", "#!/bin/sh\n")


def test_remove_hook_returns_true_when_removed(hooks_base):
    install_hook("pre-set", "#!/bin/sh\n")
    assert remove_hook("pre-set") is True


def test_remove_hook_returns_false_when_missing(hooks_base):
    assert remove_hook("post-rotate") is False


def test_list_hooks_empty_when_none_installed(hooks_base):
    assert list_hooks() == []


def test_list_hooks_returns_installed(hooks_base):
    install_hook("post-set", "#!/bin/sh\n")
    install_hook("pre-delete", "#!/bin/sh\n")
    result = list_hooks()
    assert "post-set" in result
    assert "pre-delete" in result


def test_run_hook_returns_none_when_no_hook(hooks_base):
    assert run_hook("post-import") is None


def test_run_hook_returns_exit_code(hooks_base):
    install_hook("post-set", "#!/bin/sh\nexit 0\n")
    code = run_hook("post-set")
    assert code == 0


# --- CLI tests ---

@pytest.fixture()
def runner():
    return CliRunner()


def _invoke(runner, hooks_base, *args):
    env = {"ENVAULT_HOME": str(hooks_base)}
    return runner.invoke(hook_cmd, list(args), env=env, catch_exceptions=False)


def test_list_cmd_no_hooks(runner, hooks_base):
    result = _invoke(runner, hooks_base, "list")
    assert result.exit_code == 0
    assert "No hooks installed" in result.output


def test_show_events_cmd(runner, hooks_base):
    result = _invoke(runner, hooks_base, "show-events")
    assert result.exit_code == 0
    for event in HOOK_EVENTS:
        assert event in result.output


def test_install_and_list_cmd(runner, hooks_base, tmp_path):
    script = tmp_path / "myhook.sh"
    script.write_text("#!/bin/sh\necho hi\n")
    result = _invoke(runner, hooks_base, "install", "post-set", str(script))
    assert result.exit_code == 0
    assert "installed" in result.output
    result2 = _invoke(runner, hooks_base, "list")
    assert "post-set" in result2.output


def test_remove_cmd_success(runner, hooks_base):
    install_hook("post-delete", "#!/bin/sh\n", profile="default")
    result = _invoke(runner, hooks_base, "remove", "post-delete")
    assert result.exit_code == 0
    assert "removed" in result.output


def test_remove_cmd_missing_exits_nonzero(runner, hooks_base):
    result = runner.invoke(hook_cmd, ["remove", "post-rotate"],
                           env={"ENVAULT_HOME": str(hooks_base)}, catch_exceptions=False)
    assert result.exit_code != 0
