"""Tests for envault.schema module."""

import pytest
from envault.schema import (
    FieldSchema,
    ValidationError,
    validate_variables,
    format_validation_results,
)


VARS = {
    "DATABASE_URL": "postgres://localhost/db",
    "PORT": "8080",
    "ENV": "production",
}


def test_validate_required_present_passes():
    schema = {"DATABASE_URL": FieldSchema(required=True)}
    errors = validate_variables(VARS, schema)
    assert errors == []


def test_validate_required_missing_returns_error():
    schema = {"SECRET_KEY": FieldSchema(required=True)}
    errors = validate_variables(VARS, schema)
    assert len(errors) == 1
    assert errors[0].key == "SECRET_KEY"
    assert "missing" in errors[0].message


def test_validate_pattern_match_passes():
    schema = {"PORT": FieldSchema(pattern=r"\d+")}
    errors = validate_variables(VARS, schema)
    assert errors == []


def test_validate_pattern_mismatch_returns_error():
    schema = {"DATABASE_URL": FieldSchema(pattern=r"\d+")}
    errors = validate_variables(VARS, schema)
    assert len(errors) == 1
    assert "pattern" in errors[0].message


def test_validate_min_length_passes():
    schema = {"DATABASE_URL": FieldSchema(min_length=5)}
    errors = validate_variables(VARS, schema)
    assert errors == []


def test_validate_min_length_fails():
    schema = {"PORT": FieldSchema(min_length=10)}
    errors = validate_variables(VARS, schema)
    assert len(errors) == 1
    assert "too short" in errors[0].message


def test_validate_max_length_fails():
    schema = {"DATABASE_URL": FieldSchema(max_length=5)}
    errors = validate_variables(VARS, schema)
    assert len(errors) == 1
    assert "too long" in errors[0].message


def test_validate_allowed_values_passes():
    schema = {"ENV": FieldSchema(allowed_values=["production", "staging", "development"])}
    errors = validate_variables(VARS, schema)
    assert errors == []


def test_validate_allowed_values_fails():
    schema = {"ENV": FieldSchema(allowed_values=["staging", "development"])}
    errors = validate_variables(VARS, schema)
    assert len(errors) == 1
    assert "not in allowed values" in errors[0].message


def test_validate_skips_meta_keys():
    vars_with_meta = {**VARS, "__tags": {"PORT": ["infra"]}}
    schema = {"__tags": FieldSchema(required=True, min_length=1)}
    # meta keys are excluded from data passed to validation
    errors = validate_variables(vars_with_meta, schema)
    assert any(e.key == "__tags" for e in errors)  # required but not in data subset


def test_format_validation_results_no_errors():
    result = format_validation_results([])
    assert "passed" in result


def test_format_validation_results_shows_errors():
    errors = [
        ValidationError(key="FOO", message="Required variable 'FOO' is missing."),
        ValidationError(key="BAR", message="Value too short (min 8 chars)."),
    ]
    result = format_validation_results(errors)
    assert "[ERROR] FOO" in result
    assert "[ERROR] BAR" in result
