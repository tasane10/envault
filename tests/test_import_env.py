"""Tests for envault.import_env module."""

import json
import pytest
from pathlib import Path

from envault.import_env import parse_dotenv, parse_json_env, import_variables


# ---------------------------------------------------------------------------
# parse_dotenv
# ---------------------------------------------------------------------------

def test_parse_dotenv_basic():
    content = "KEY=value\nFOO=bar"
    result = parse_dotenv(content)
    assert result == {"KEY": "value", "FOO": "bar"}


def test_parse_dotenv_ignores_comments_and_blank_lines():
    content = "\n# this is a comment\nKEY=value\n"
    result = parse_dotenv(content)
    assert result == {"KEY": "value"}


def test_parse_dotenv_strips_double_quotes():
    result = parse_dotenv('DB_URL="postgres://localhost/db"')
    assert result["DB_URL"] == "postgres://localhost/db"


def test_parse_dotenv_strips_single_quotes():
    result = parse_dotenv("SECRET='my secret value'")
    assert result["SECRET"] == "my secret value"


def test_parse_dotenv_handles_export_prefix():
    result = parse_dotenv("export API_KEY=abc123")
    assert result["API_KEY"] == "abc123"


def test_parse_dotenv_skips_lines_without_equals():
    result = parse_dotenv("INVALID_LINE\nVALID=yes")
    assert result == {"VALID": "yes"}
    assert "INVALID_LINE" not in result


# ---------------------------------------------------------------------------
# parse_json_env
# ---------------------------------------------------------------------------

def test_parse_json_env_basic():
    content = json.dumps({"KEY": "value", "PORT": 8080})
    result = parse_json_env(content)
    assert result == {"KEY": "value", "PORT": "8080"}


def test_parse_json_env_raises_on_non_dict():
    with pytest.raises(ValueError, match="top-level object"):
        parse_json_env(json.dumps(["not", "a", "dict"]))


def test_parse_json_env_raises_on_invalid_json():
    with pytest.raises(json.JSONDecodeError):
        parse_json_env("not json at all")


# ---------------------------------------------------------------------------
# import_variables
# ---------------------------------------------------------------------------

def test_import_variables_dotenv_file(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("APP_ENV=production\nDEBUG=false")
    result = import_variables(str(env_file))
    assert result == {"APP_ENV": "production", "DEBUG": "false"}


def test_import_variables_json_file(tmp_path):
    json_file = tmp_path / "vars.json"
    json_file.write_text(json.dumps({"TOKEN": "xyz", "TIMEOUT": 30}))
    result = import_variables(str(json_file))
    assert result == {"TOKEN": "xyz", "TIMEOUT": "30"}


def test_import_variables_explicit_format_override(tmp_path):
    # File has no .json extension but contains JSON
    env_file = tmp_path / "myenv"
    env_file.write_text(json.dumps({"X": "1"}))
    result = import_variables(str(env_file), fmt="json")
    assert result == {"X": "1"}


def test_import_variables_file_not_found():
    with pytest.raises(FileNotFoundError):
        import_variables("/nonexistent/path/.env")


def test_import_variables_unsupported_format(tmp_path):
    f = tmp_path / "vars.toml"
    f.write_text("key = 'value'")
    with pytest.raises(ValueError, match="Unsupported import format"):
        import_variables(str(f), fmt="toml")
