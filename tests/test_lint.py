"""Tests for envault.lint module."""

import pytest
from envault.lint import (
    lint_name,
    lint_value,
    lint_variables,
    format_lint_results,
    ERROR_INVALID_NAME,
    ERROR_EMPTY_NAME,
    WARN_LOWERCASE,
    WARN_EMPTY_VALUE,
    WARN_WHITESPACE_VALUE,
)


# --- lint_name ---

def test_lint_name_valid_uppercase():
    assert lint_name("MY_VAR") == []


def test_lint_name_valid_with_digits():
    assert lint_name("VAR_1") == []


def test_lint_name_valid_underscore_start():
    assert lint_name("_PRIVATE") == []


def test_lint_name_warns_lowercase():
    issues = lint_name("my_var")
    messages = [i["message"] for i in issues]
    assert WARN_LOWERCASE in messages
    assert all(i["level"] == "warning" for i in issues)


def test_lint_name_error_starts_with_digit():
    issues = lint_name("1BAD")
    messages = [i["message"] for i in issues]
    assert ERROR_INVALID_NAME in messages
    assert any(i["level"] == "error" for i in issues)


def test_lint_name_error_contains_dash():
    issues = lint_name("MY-VAR")
    messages = [i["message"] for i in issues]
    assert ERROR_INVALID_NAME in messages


def test_lint_name_error_empty():
    issues = lint_name("")
    messages = [i["message"] for i in issues]
    assert ERROR_EMPTY_NAME in messages
    assert any(i["level"] == "error" for i in issues)


# --- lint_value ---

def test_lint_value_normal_string():
    assert lint_value("hello") == []


def test_lint_value_empty_string_warns():
    issues = lint_value("")
    assert any(i["message"] == WARN_EMPTY_VALUE for i in issues)


def test_lint_value_none_warns():
    issues = lint_value(None)
    assert any(i["message"] == WARN_EMPTY_VALUE for i in issues)


def test_lint_value_leading_whitespace_warns():
    issues = lint_value(" value")
    assert any(i["message"] == WARN_WHITESPACE_VALUE for i in issues)


def test_lint_value_trailing_whitespace_warns():
    issues = lint_value("value ")
    assert any(i["message"] == WARN_WHITESPACE_VALUE for i in issues)


# --- lint_variables ---

def test_lint_variables_clean_dict():
    variables = {"DB_HOST": "localhost", "PORT": "5432"}
    assert lint_variables(variables) == {}


def test_lint_variables_flags_bad_name():
    variables = {"bad-name": "value", "GOOD": "ok"}
    results = lint_variables(variables)
    assert "bad-name" in results
    assert "GOOD" not in results


def test_lint_variables_flags_empty_value():
    variables = {"MY_VAR": ""}
    results = lint_variables(variables)
    assert "MY_VAR" in results


# --- format_lint_results ---

def test_format_lint_results_no_issues():
    assert format_lint_results({}) == "No issues found."


def test_format_lint_results_shows_level_and_name():
    results = {"bad-var": [{"level": "error", "message": ERROR_INVALID_NAME}]}
    output = format_lint_results(results)
    assert "[ERROR]" in output
    assert "bad-var" in output
    assert ERROR_INVALID_NAME in output
