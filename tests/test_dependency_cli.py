"""Tests for envault.dependency_cli."""

from __future__ import annotations

from unittest.mock import patch

import pytest
from click.testing import CliRunner

from envault.dependency_cli import dependency_cmd

_PROFILE = "default"
_PASSWORD = "secret"
_BASE_VARS = {"A": "1", "B": "2", "C": "3"}


@pytest.fixture()
def runner():
    return CliRunner()


def _invoke(runner: CliRunner, args, variables: dict | None = None):
    vars_store = dict(variables or _BASE_VARS)

    def _load(profile, password):
        return dict(vars_store)

    def _save(profile, data, password):
        vars_store.clear()
        vars_store.update(data)

    with patch("envault.dependency_cli.prompt_password", return_value=_PASSWORD), \
         patch("envault.dependency_cli.load_profile", side_effect=_load), \
         patch("envault.dependency_cli.save_profile", side_effect=_save):
        result = runner.invoke(dependency_cmd, args, catch_exceptions=False)
    return result, vars_store


def test_set_dep_success(runner):
    result, store = _invoke(runner, ["set", "C", "A", "B"])
    assert result.exit_code == 0
    assert "C -> A, B" in result.output
    deps = store.get("__meta__", {}).get("dependencies", {})
    assert deps.get("C") == ["A", "B"]


def test_set_dep_missing_key_fails(runner):
    result, _ = _invoke(runner, ["set", "Z", "A"])
    assert result.exit_code != 0
    assert "Z" in result.output


def test_remove_dep_success(runner):
    from envault.dependency import set_dependency
    pre = set_dependency(_BASE_VARS, "C", ["A"])
    result, store = _invoke(runner, ["remove", "C"], variables=pre)
    assert result.exit_code == 0
    assert "removed" in result.output.lower()
    deps = store.get("__meta__", {}).get("dependencies", {})
    assert "C" not in deps


def test_list_deps_no_deps(runner):
    result, _ = _invoke(runner, ["list"])
    assert result.exit_code == 0
    assert "No dependencies" in result.output


def test_list_deps_shows_entries(runner):
    from envault.dependency import set_dependency
    pre = set_dependency(_BASE_VARS, "B", ["A"])
    result, _ = _invoke(runner, ["list"], variables=pre)
    assert result.exit_code == 0
    assert "B -> A" in result.output


def test_order_cmd_respects_deps(runner):
    from envault.dependency import set_dependency
    pre = set_dependency(_BASE_VARS, "C", ["A"])
    result, _ = _invoke(runner, ["order"], variables=pre)
    assert result.exit_code == 0
    lines = [l.strip() for l in result.output.strip().splitlines() if l.strip()]
    keys = [l.split(".", 1)[1].strip() for l in lines]
    assert keys.index("A") < keys.index("C")
