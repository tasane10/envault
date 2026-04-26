"""Tests for envault.export module."""

import json
import pytest

from envault.export import export_variables, export_dotenv, export_bash, export_json


SAMPLE = {
    "DATABASE_URL": "postgres://localhost/db",
    "SECRET_KEY": 'abc"def',
    "PORT": "5432",
}


def test_export_dotenv_format():
    result = export_dotenv(SAMPLE)
    assert 'DATABASE_URL="postgres://localhost/db"' in result
    assert 'PORT="5432"' in result


def test_export_dotenv_escapes_quotes():
    result = export_dotenv({"KEY": 'val"ue'})
    assert 'KEY="val\\"ue"' in result


def test_export_bash_format():
    result = export_bash(SAMPLE)
    assert 'export DATABASE_URL="postgres://localhost/db"' in result
    assert 'export PORT="5432"' in result


def test_export_bash_escapes_quotes():
    result = export_bash({"KEY": 'val"ue'})
    assert 'export KEY="val\\"ue"' in result


def test_export_json_valid_json():
    result = export_json(SAMPLE)
    parsed = json.loads(result)
    assert parsed["PORT"] == "5432"
    assert parsed["DATABASE_URL"] == "postgres://localhost/db"


def test_export_json_sorted_keys():
    result = export_json({"Z": "1", "A": "2"})
    parsed = json.loads(result)
    assert list(parsed.keys()) == sorted(parsed.keys())


def test_export_variables_dispatches_dotenv():
    result = export_variables({"FOO": "bar"}, "dotenv")
    assert 'FOO="bar"' in result


def test_export_variables_dispatches_bash():
    result = export_variables({"FOO": "bar"}, "bash")
    assert 'export FOO="bar"' in result


def test_export_variables_dispatches_json():
    result = export_variables({"FOO": "bar"}, "json")
    assert json.loads(result) == {"FOO": "bar"}


def test_export_variables_unsupported_format_raises():
    with pytest.raises(ValueError, match="Unsupported format"):
        export_variables({"FOO": "bar"}, "xml")


def test_export_empty_dict_produces_empty_string():
    for fmt in ("dotenv", "bash"):
        result = export_variables({}, fmt)
        assert result == ""


def test_export_empty_dict_json_is_valid():
    result = export_variables({}, "json")
    assert json.loads(result) == {}
