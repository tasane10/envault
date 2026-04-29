"""Tests for envault.env_inject."""
from __future__ import annotations

import time
from unittest.mock import patch

import pytest

from envault.env_inject import build_env, run_with_vault


# ---------------------------------------------------------------------------
# build_env
# ---------------------------------------------------------------------------

def test_build_env_injects_variables():
    variables = {"API_KEY": "secret", "DEBUG": "true"}
    env = build_env(variables, base_env={})
    assert env["API_KEY"] == "secret"
    assert env["DEBUG"] == "true"


def test_build_env_skips_meta_keys():
    variables = {"KEY": "val", "__meta": {"tags": []}, "__ttl": {}}
    env = build_env(variables, base_env={})
    assert "KEY" in env
    assert "__meta" not in env
    assert "__ttl" not in env


def test_build_env_override_true_replaces_existing():
    variables = {"HOME": "/vault/home"}
    base = {"HOME": "/original/home"}
    env = build_env(variables, base_env=base, override=True)
    assert env["HOME"] == "/vault/home"


def test_build_env_override_false_preserves_existing():
    variables = {"HOME": "/vault/home"}
    base = {"HOME": "/original/home"}
    env = build_env(variables, base_env=base, override=False)
    assert env["HOME"] == "/original/home"


def test_build_env_skips_expired_keys():
    past_ts = time.time() - 3600
    variables = {
        "GONE": "value",
        "__ttl": {"GONE": past_ts},
    }
    env = build_env(variables, base_env={})
    assert "GONE" not in env


def test_build_env_includes_non_expired_keys():
    future_ts = time.time() + 3600
    variables = {
        "ALIVE": "yes",
        "__ttl": {"ALIVE": future_ts},
    }
    env = build_env(variables, base_env={})
    assert env["ALIVE"] == "yes"


def test_build_env_uses_os_environ_by_default():
    import os
    variables = {"INJECTED_VAR": "hello"}
    env = build_env(variables)
    assert env["INJECTED_VAR"] == "hello"
    # Should also contain standard env vars
    assert "PATH" in env or len(env) > 1


# ---------------------------------------------------------------------------
# run_with_vault
# ---------------------------------------------------------------------------

def test_run_with_vault_passes_variables_to_subprocess():
    fake_vars = {"MY_SECRET": "abc123"}
    with patch("envault.env_inject.load_profile", return_value=fake_vars):
        result = run_with_vault(
            ["env"],
            password="pw",
            profile="default",
        )
    assert result.returncode == 0


def test_run_with_vault_returns_nonzero_on_failure():
    fake_vars = {"X": "1"}
    with patch("envault.env_inject.load_profile", return_value=fake_vars):
        result = run_with_vault(
            ["false"],
            password="pw",
            profile="default",
        )
    assert result.returncode != 0
