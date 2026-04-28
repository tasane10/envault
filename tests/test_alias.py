"""Unit tests for envault.alias."""

from __future__ import annotations

import pytest

from envault.alias import (
    get_aliases,
    list_aliases,
    remove_alias,
    resolve_alias,
    set_alias,
)


BASE_VARS = {"DB_URL": "postgres://localhost", "API_KEY": "secret"}


def test_get_aliases_empty_when_no_meta():
    assert get_aliases(BASE_VARS) == {}


def test_set_alias_stores_mapping():
    result = set_alias(BASE_VARS, "db", "DB_URL")
    assert get_aliases(result) == {"db": "DB_URL"}


def test_set_alias_does_not_mutate_original():
    original = dict(BASE_VARS)
    set_alias(original, "db", "DB_URL")
    assert "__meta__" not in original


def test_set_alias_multiple_aliases():
    v = set_alias(BASE_VARS, "db", "DB_URL")
    v = set_alias(v, "api", "API_KEY")
    aliases = get_aliases(v)
    assert aliases == {"db": "DB_URL", "api": "API_KEY"}


def test_set_alias_raises_for_missing_key():
    with pytest.raises(KeyError, match="MISSING"):
        set_alias(BASE_VARS, "x", "MISSING")


def test_set_alias_raises_when_alias_equals_key():
    with pytest.raises(ValueError, match="differ"):
        set_alias(BASE_VARS, "DB_URL", "DB_URL")


def test_remove_alias_removes_entry():
    v = set_alias(BASE_VARS, "db", "DB_URL")
    v = remove_alias(v, "db")
    assert get_aliases(v) == {}


def test_remove_alias_raises_for_missing_alias():
    with pytest.raises(KeyError, match="ghost"):
        remove_alias(BASE_VARS, "ghost")


def test_resolve_alias_returns_real_key():
    v = set_alias(BASE_VARS, "db", "DB_URL")
    assert resolve_alias(v, "db") == "DB_URL"


def test_resolve_alias_returns_name_unchanged_when_not_alias():
    assert resolve_alias(BASE_VARS, "DB_URL") == "DB_URL"


def test_list_aliases_sorted():
    v = set_alias(BASE_VARS, "z_alias", "API_KEY")
    v = set_alias(v, "a_alias", "DB_URL")
    pairs = list_aliases(v)
    assert pairs == [("a_alias", "DB_URL"), ("z_alias", "API_KEY")]


def test_list_aliases_empty():
    assert list_aliases(BASE_VARS) == []
