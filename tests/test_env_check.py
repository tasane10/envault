"""Tests for envault.env_check."""

from __future__ import annotations

import pytest

from envault.env_check import check_variables, format_check_results


VAULT = {"DB_HOST": "localhost", "DB_PORT": "5432", "SECRET": "abc123"}


def test_all_ok_when_env_matches():
    env = dict(VAULT)
    results = check_variables(VAULT, env)
    assert all(r["status"] == "ok" for r in results)
    assert len(results) == 3


def test_missing_when_key_absent_from_env():
    env = {"DB_HOST": "localhost", "DB_PORT": "5432"}  # SECRET missing
    results = check_variables(VAULT, env)
    statuses = {r["key"]: r["status"] for r in results}
    assert statuses["SECRET"] == "missing"
    assert statuses["DB_HOST"] == "ok"


def test_mismatch_when_value_differs():
    env = {**VAULT, "DB_HOST": "remotehost"}
    results = check_variables(VAULT, env)
    statuses = {r["key"]: r["status"] for r in results}
    assert statuses["DB_HOST"] == "mismatch"


def test_env_value_captured_in_result():
    env = {**VAULT, "DB_PORT": "9999"}
    results = check_variables(VAULT, env)
    port_result = next(r for r in results if r["key"] == "DB_PORT")
    assert port_result["env_value"] == "9999"
    assert port_result["vault_value"] == "5432"


def test_skips_metadata_keys():
    vault_with_meta = {**VAULT, "_tags": "{}", "_ttl": "123"}
    results = check_variables(vault_with_meta, dict(VAULT))
    keys = [r["key"] for r in results]
    assert "_tags" not in keys
    assert "_ttl" not in keys


def test_empty_vault_returns_empty_results():
    results = check_variables({}, {"SOME_VAR": "val"})
    assert results == []


def test_format_check_results_no_variables():
    output = format_check_results([])
    assert "No variables" in output


def test_format_check_results_shows_missing():
    results = check_variables({"FOO": "bar"}, {})
    output = format_check_results(results)
    assert "MISSING" in output
    assert "FOO" in output


def test_format_check_results_shows_mismatch():
    results = check_variables({"FOO": "bar"}, {"FOO": "baz"})
    output = format_check_results(results)
    assert "MISMATCH" in output
    assert "bar" in output
    assert "baz" in output


def test_format_check_results_summary_line():
    vault = {"A": "1", "B": "2", "C": "3"}
    env = {"A": "1", "B": "wrong"}  # C missing
    results = check_variables(vault, env)
    output = format_check_results(results)
    assert "1 ok" in output
    assert "1 missing" in output
    assert "1 mismatched" in output
