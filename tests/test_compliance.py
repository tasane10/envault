"""Tests for envault.compliance module."""

import pytest
from envault.compliance import (
    check_naming,
    check_value,
    run_compliance,
    format_compliance_results,
    ComplianceIssue,
)


def test_check_naming_valid_upper_snake_case():
    issues = check_naming("DATABASE_URL")
    assert issues == []


def test_check_naming_valid_underscore_start():
    issues = check_naming("_PRIVATE_KEY")
    assert issues == []


def test_check_naming_warns_lowercase():
    issues = check_naming("database_url")
    assert len(issues) == 1
    assert issues[0].severity == "warning"
    assert "UPPER_SNAKE_CASE" in issues[0].message


def test_check_naming_error_mixed_case():
    issues = check_naming("Database-URL")
    assert len(issues) == 1
    assert issues[0].severity == "error"


def test_check_naming_error_starts_with_digit():
    issues = check_naming("1BAD_KEY")
    assert len(issues) == 1
    assert issues[0].severity == "error"


def test_check_value_empty_value_warns():
    issues = check_value("MY_VAR", "")
    assert any(i.severity == "warning" and "empty" in i.message for i in issues)


def test_check_value_clean_value_no_issues():
    issues = check_value("MY_VAR", "hello_world")
    assert issues == []


def test_check_value_password_key_warns():
    issues = check_value("DB_PASSWORD", "s3cr3t")
    assert any("sensitive" in i.message for i in issues)


def test_check_value_token_key_warns():
    issues = check_value("API_TOKEN", "abc123")
    assert any("sensitive" in i.message for i in issues)


def test_check_value_secret_key_warns():
    issues = check_value("APP_SECRET", "xyz")
    assert any("sensitive" in i.message for i in issues)


def test_run_compliance_skips_meta_keys():
    variables = {"__meta": "internal", "GOOD_KEY": "value"}
    issues = run_compliance(variables)
    assert all(i.key != "__meta" for i in issues)


def test_run_compliance_returns_all_issues():
    variables = {"bad_key": "", "GOOD_KEY": "fine"}
    issues = run_compliance(variables)
    keys_with_issues = {i.key for i in issues}
    assert "bad_key" in keys_with_issues


def test_run_compliance_clean_variables():
    variables = {"APP_NAME": "myapp", "PORT": "8080"}
    issues = run_compliance(variables)
    assert issues == []


def test_format_compliance_results_no_issues():
    result = format_compliance_results([])
    assert "No compliance issues" in result


def test_format_compliance_results_shows_errors():
    issues = [ComplianceIssue("BAD", "error", "Something wrong")]
    result = format_compliance_results(issues)
    assert "[ERROR]" in result
    assert "BAD" in result


def test_format_compliance_results_shows_warnings():
    issues = [ComplianceIssue("WARN_KEY", "warning", "Might be sensitive")]
    result = format_compliance_results(issues)
    assert "[WARN]" in result
    assert "WARN_KEY" in result
