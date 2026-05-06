"""Tests for envault.cascade module."""

import pytest
from envault.cascade import resolve_cascade, explain_cascade, list_overrides


BASE = {"DB_HOST": "localhost", "DB_PORT": "5432", "APP_ENV": "development"}
PROD = {"DB_HOST": "prod.db.internal", "APP_ENV": "production"}
SECRETS = {"DB_PASSWORD": "s3cr3t", "__meta": "ignored"}


def test_resolve_cascade_highest_priority_wins():
    loaded = {"prod": PROD, "base": BASE}
    result = resolve_cascade(["prod", "base"], loaded)
    assert result["DB_HOST"] == "prod.db.internal"
    assert result["APP_ENV"] == "production"


def test_resolve_cascade_fills_missing_from_lower_priority():
    loaded = {"prod": PROD, "base": BASE}
    result = resolve_cascade(["prod", "base"], loaded)
    assert result["DB_PORT"] == "5432"


def test_resolve_cascade_excludes_meta_keys():
    loaded = {"secrets": SECRETS}
    result = resolve_cascade(["secrets"], loaded)
    assert "__meta" not in result
    assert "DB_PASSWORD" in result


def test_resolve_cascade_empty_profiles_returns_empty():
    result = resolve_cascade([], {})
    assert result == {}


def test_resolve_cascade_missing_profile_treated_as_empty():
    loaded = {"base": BASE}
    result = resolve_cascade(["missing", "base"], loaded)
    assert result == {k: v for k, v in BASE.items()}


def test_resolve_cascade_single_profile():
    loaded = {"base": BASE}
    result = resolve_cascade(["base"], loaded)
    assert result == BASE


def test_explain_cascade_returns_source_profile():
    loaded = {"prod": PROD, "base": BASE}
    result = explain_cascade(["prod", "base"], loaded)
    assert result["DB_HOST"] == ("prod.db.internal", "prod")
    assert result["DB_PORT"] == ("5432", "base")


def test_explain_cascade_excludes_meta_keys():
    loaded = {"secrets": SECRETS}
    result = explain_cascade(["secrets"], loaded)
    assert "__meta" not in result


def test_explain_cascade_single_profile_all_from_that_profile():
    loaded = {"base": BASE}
    result = explain_cascade(["base"], loaded)
    for key in BASE:
        assert result[key][1] == "base"


def test_list_overrides_detects_overridden_keys():
    loaded = {"prod": PROD, "base": BASE}
    overrides = list_overrides(["prod", "base"], loaded)
    keys = [o["key"] for o in overrides]
    assert "DB_HOST" in keys
    assert "APP_ENV" in keys


def test_list_overrides_records_correct_profiles():
    loaded = {"prod": PROD, "base": BASE}
    overrides = list_overrides(["prod", "base"], loaded)
    db_host_override = next(o for o in overrides if o["key"] == "DB_HOST")
    assert db_host_override["overriding_profile"] == "prod"
    assert db_host_override["overridden_profile"] == "base"


def test_list_overrides_no_overlap_returns_empty():
    loaded = {"secrets": {"DB_PASSWORD": "x"}, "base": {"APP_ENV": "dev"}}
    overrides = list_overrides(["secrets", "base"], loaded)
    assert overrides == []


def test_list_overrides_value_is_from_overriding_profile():
    loaded = {"prod": PROD, "base": BASE}
    overrides = list_overrides(["prod", "base"], loaded)
    db_host_override = next(o for o in overrides if o["key"] == "DB_HOST")
    assert db_host_override["value"] == "prod.db.internal"
