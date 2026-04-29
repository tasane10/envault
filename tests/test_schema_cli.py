import json
import pytest
from click.testing import CliRunner
from unittest.mock import patch, MagicMock
from envault.schema_cli import schema_cmd


@pytest.fixture
def runner():
    return CliRunner()


def _invoke(runner, args, input_text="password\n"):
    return runner.invoke(schema_cmd, args, input=input_text, catch_exceptions=False)


def _write_schema(tmp_path, schema_dict):
    p = tmp_path / "schema.json"
    p.write_text(json.dumps(schema_dict))
    return str(p)


def test_validate_cmd_all_pass(runner, tmp_path):
    schema_file = _write_schema(tmp_path, {
        "API_KEY": {"required": True}
    })
    with patch("envault.schema_cli.load_vault", return_value={"API_KEY": "abc"}), \
         patch("envault.schema_cli.get_vault_path", return_value=tmp_path / "vault"):
        result = _invoke(runner, ["validate", "--schema-file", schema_file])
    assert result.exit_code == 0
    assert "passed" in result.output


def test_validate_cmd_fails_on_missing_required(runner, tmp_path):
    schema_file = _write_schema(tmp_path, {
        "API_KEY": {"required": True}
    })
    with patch("envault.schema_cli.load_vault", return_value={}), \
         patch("envault.schema_cli.get_vault_path", return_value=tmp_path / "vault"):
        result = runner.invoke(schema_cmd, ["validate", "--schema-file", schema_file],
                               input="password\n", catch_exceptions=False)
    assert result.exit_code == 1
    assert "API_KEY" in result.output


def test_validate_cmd_fails_on_pattern_mismatch(runner, tmp_path):
    schema_file = _write_schema(tmp_path, {
        "PORT": {"pattern": "^[0-9]+$"}
    })
    with patch("envault.schema_cli.load_vault", return_value={"PORT": "not-a-number"}), \
         patch("envault.schema_cli.get_vault_path", return_value=tmp_path / "vault"):
        result = runner.invoke(schema_cmd, ["validate", "--schema-file", schema_file],
                               input="password\n", catch_exceptions=False)
    assert result.exit_code == 1
    assert "PORT" in result.output


def test_show_cmd_displays_fields(runner, tmp_path):
    schema_file = _write_schema(tmp_path, {
        "DB_URL": {"required": True, "min_length": 5},
        "ENV": {"allowed_values": ["dev", "prod"]}
    })
    result = runner.invoke(schema_cmd, ["show", "--schema-file", schema_file],
                           catch_exceptions=False)
    assert result.exit_code == 0
    assert "DB_URL" in result.output
    assert "required" in result.output
    assert "min_length=5" in result.output
    assert "ENV" in result.output


def test_show_cmd_empty_schema(runner, tmp_path):
    schema_file = _write_schema(tmp_path, {})
    result = runner.invoke(schema_cmd, ["show", "--schema-file", schema_file],
                           catch_exceptions=False)
    assert result.exit_code == 0
    assert "empty" in result.output
