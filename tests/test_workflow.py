"""Tests for envault/workflow.py."""
from __future__ import annotations

import json

import pytest

from envault.workflow import (
    delete_workflow,
    get_workflow_path,
    list_workflows,
    load_workflow,
    run_workflow,
    save_workflow,
)


@pytest.fixture()
def wf_base(tmp_path):
    return tmp_path / "workflows"


def _steps():
    return [{"action": "set", "key": "FOO", "value": "bar"}]


def test_save_workflow_creates_file(wf_base):
    path = save_workflow("deploy", _steps(), base=wf_base)
    assert path.exists()


def test_save_workflow_roundtrip(wf_base):
    save_workflow("deploy", _steps(), base=wf_base)
    wf = load_workflow("deploy", base=wf_base)
    assert wf["name"] == "deploy"
    assert wf["steps"] == _steps()


def test_save_workflow_invalid_name_raises(wf_base):
    with pytest.raises(ValueError, match="Invalid workflow name"):
        save_workflow("bad-name!", _steps(), base=wf_base)


def test_save_workflow_invalid_action_raises(wf_base):
    with pytest.raises(ValueError, match="Unknown action"):
        save_workflow("wf", [{"action": "explode", "key": "X"}], base=wf_base)


def test_load_workflow_missing_raises(wf_base):
    with pytest.raises(FileNotFoundError):
        load_workflow("ghost", base=wf_base)


def test_list_workflows_empty(wf_base):
    assert list_workflows(base=wf_base) == []


def test_list_workflows_returns_names(wf_base):
    save_workflow("alpha", _steps(), base=wf_base)
    save_workflow("beta", _steps(), base=wf_base)
    assert list_workflows(base=wf_base) == ["alpha", "beta"]


def test_delete_workflow_returns_true(wf_base):
    save_workflow("tmp", _steps(), base=wf_base)
    assert delete_workflow("tmp", base=wf_base) is True
    assert not get_workflow_path("tmp", base=wf_base).exists()


def test_delete_workflow_missing_returns_false(wf_base):
    assert delete_workflow("nope", base=wf_base) is False


def test_run_workflow_set_action(wf_base):
    save_workflow("setwf", [{"action": "set", "key": "X", "value": "42"}], base=wf_base)
    variables: dict = {}
    log = run_workflow("setwf", variables, base=wf_base)
    assert variables["X"] == "42"
    assert log[0]["status"] == "ok"


def test_run_workflow_delete_action(wf_base):
    save_workflow("delwf", [{"action": "delete", "key": "X"}], base=wf_base)
    variables = {"X": "old"}
    log = run_workflow("delwf", variables, base=wf_base)
    assert "X" not in variables
    assert log[0]["status"] == "ok"


def test_run_workflow_delete_missing_key_status(wf_base):
    save_workflow("delwf2", [{"action": "delete", "key": "MISSING"}], base=wf_base)
    variables: dict = {}
    log = run_workflow("delwf2", variables, base=wf_base)
    assert log[0]["status"] == "not_found"
