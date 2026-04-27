"""Tests for envault.search module."""

import pytest
from unittest.mock import patch
from envault.search import search_variables, format_search_results


MOCK_PROFILES = {
    "default": {"DATABASE_URL": "postgres://localhost/db", "SECRET_KEY": "abc123", "DEBUG": "true"},
    "production": {"DATABASE_URL": "postgres://prod/db", "SECRET_KEY": "xyz789", "LOG_LEVEL": "warn"},
}


def _mock_list_profiles():
    return list(MOCK_PROFILES.keys())


def _mock_load_profile(profile, password):
    if password != "correct":
        raise ValueError("Wrong password")
    return MOCK_PROFILES[profile]


@pytest.fixture(autouse=True)
def patch_profile_funcs():
    with patch("envault.search.list_profiles", side_effect=_mock_list_profiles), \
         patch("envault.search.load_profile", side_effect=_mock_load_profile):
        yield


def test_search_matches_key():
    results = search_variables("DATABASE", "correct")
    assert "default" in results
    assert "DATABASE_URL" in results["default"]


def test_search_matches_value():
    results = search_variables("abc123", "correct")
    assert "default" in results
    assert "SECRET_KEY" in results["default"]


def test_search_is_case_insensitive():
    results = search_variables("secret_key", "correct")
    assert "default" in results
    assert "SECRET_KEY" in results["default"]


def test_search_keys_only_excludes_value_matches():
    results = search_variables("abc123", "correct", keys_only=True)
    assert results == {}


def test_search_values_only_excludes_key_matches():
    results = search_variables("DATABASE", "correct", values_only=True)
    assert results == {}


def test_search_specific_profile():
    results = search_variables("LOG_LEVEL", "correct", profile="production")
    assert "production" in results
    assert "default" not in results


def test_search_skips_profiles_with_wrong_password():
    with patch("envault.search.load_profile", side_effect=ValueError("bad")):
        results = search_variables("anything", "wrong")
    assert results == {}


def test_search_invalid_regex_raises():
    with pytest.raises(ValueError, match="Invalid search pattern"):
        search_variables("[invalid", "correct")


def test_format_search_results_empty():
    output = format_search_results({})
    assert output == "No matches found."


def test_format_search_results_shows_profile_header():
    results = {"default": {"FOO": "bar"}}
    output = format_search_results(results)
    assert "[default]" in output
    assert "FOO=bar" in output


def test_format_search_results_hides_values():
    results = {"default": {"FOO": "bar"}}
    output = format_search_results(results, show_values=False)
    assert "FOO" in output
    assert "bar" not in output
