import pytest
from envault.schema import (
    FieldSchema, ValidationError, validate_variables, format_validation_results
)


def test_validate_required_present_passes():
    schema = {"API_KEY": FieldSchema(required=True)}
    errors = validate_variables({"API_KEY": "secret"}, schema)
    assert errors == []


def test_validate_required_missing_returns_error():
    schema = {"API_KEY": FieldSchema(required=True)}
    errors = validate_variables({}, schema)
    assert len(errors) == 1
    assert errors[0].key == "API_KEY"
    assert "required" in errors[0].message.lower()


def test_validate_pattern_match_passes():
    schema = {"PORT": FieldSchema(pattern=r"^\d+$")}
    errors = validate_variables({"PORT": "8080"}, schema)
    assert errors == []


def test_validate_pattern_mismatch_returns_error():
    schema = {"PORT": FieldSchema(pattern=r"^\d+$")}
    errors = validate_variables({"PORT": "abc"}, schema)
    assert len(errors) == 1
    assert "pattern" in errors[0].message.lower()


def test_validate_min_length_passes():
    schema = {"TOKEN": FieldSchema(min_length=4)}
    errors = validate_variables({"TOKEN": "abcd"}, schema)
    assert errors == []


def test_validate_min_length_fails():
    schema = {"TOKEN": FieldSchema(min_length=10)}
    errors = validate_variables({"TOKEN": "short"}, schema)
    assert len(errors) == 1
    assert "min_length" in errors[0].message.lower()


def test_validate_max_length_passes():
    schema = {"CODE": FieldSchema(max_length=5)}
    errors = validate_variables({"CODE": "abc"}, schema)
    assert errors == []


def test_validate_max_length_fails():
    schema = {"CODE": FieldSchema(max_length=3)}
    errors = validate_variables({"CODE": "toolong"}, schema)
    assert len(errors) == 1
    assert "max_length" in errors[0].message.lower()


def test_validate_allowed_values_passes():
    schema = {"ENV": FieldSchema(allowed_values=["dev", "staging", "prod"])}
    errors = validate_variables({"ENV": "dev"}, schema)
    assert errors == []


def test_validate_allowed_values_fails():
    schema = {"ENV": FieldSchema(allowed_values=["dev", "prod"])}
    errors = validate_variables({"ENV": "unknown"}, schema)
    assert len(errors) == 1
    assert "allowed" in errors[0].message.lower()


def test_validate_multiple_errors():
    schema = {
        "A": FieldSchema(required=True),
        "B": FieldSchema(pattern=r"^\d+$"),
    }
    errors = validate_variables({"B": "nope"}, schema)
    keys = [e.key for e in errors]
    assert "A" in keys
    assert "B" in keys


def test_validate_skips_unknown_keys():
    schema = {"KNOWN": FieldSchema(required=True)}
    errors = validate_variables({"KNOWN": "val", "EXTRA": "x"}, schema)
    assert errors == []


def test_format_validation_results_contains_key_and_message():
    errors = [ValidationError(key="API_KEY", message="is required")]
    output = format_validation_results(errors)
    assert "API_KEY" in output
    assert "is required" in output


def test_format_validation_results_multiple():
    errors = [
        ValidationError(key="A", message="msg1"),
        ValidationError(key="B", message="msg2"),
    ]
    output = format_validation_results(errors)
    assert "A" in output
    assert "B" in output
