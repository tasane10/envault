"""Tests for envault.diff module."""

import pytest

from envault.diff import diff_variables, format_diff


BASE = {"DB_HOST": "localhost", "DB_PORT": "5432", "SECRET": "abc"}
TARGET = {"DB_HOST": "prod.db", "DB_PORT": "5432", "API_KEY": "xyz"}


def test_diff_variables_detects_changed():
    diff = diff_variables(BASE, TARGET)
    assert "DB_HOST" in diff
    assert diff["DB_HOST"] == ("localhost", "prod.db")


def test_diff_variables_detects_removed():
    diff = diff_variables(BASE, TARGET)
    assert "SECRET" in diff
    assert diff["SECRET"] == ("abc", None)


def test_diff_variables_detects_added():
    diff = diff_variables(BASE, TARGET)
    assert "API_KEY" in diff
    assert diff["API_KEY"] == (None, "xyz")


def test_diff_variables_ignores_equal_keys():
    diff = diff_variables(BASE, TARGET)
    assert "DB_PORT" not in diff


def test_diff_variables_empty_when_identical():
    diff = diff_variables(BASE, BASE)
    assert diff == {}


def test_diff_variables_both_empty():
    assert diff_variables({}, {}) == {}


def test_format_diff_no_differences():
    result = format_diff({})
    assert "No differences" in result


def test_format_diff_masks_values_by_default():
    diff = diff_variables(BASE, TARGET)
    output = format_diff(diff, show_values=False)
    assert "localhost" not in output
    assert "prod.db" not in output
    assert "***" in output


def test_format_diff_shows_values_when_requested():
    diff = diff_variables(BASE, TARGET)
    output = format_diff(diff, show_values=True)
    assert "localhost" in output
    assert "prod.db" in output


def test_format_diff_labels_added_removed_changed():
    diff = diff_variables(BASE, TARGET)
    output = format_diff(diff, show_values=False)
    assert "added" in output
    assert "removed" in output
    assert "changed" in output
