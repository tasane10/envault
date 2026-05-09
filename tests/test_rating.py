"""Tests for envault/rating.py"""

import pytest
from envault.rating import (
    get_ratings, set_rating, remove_rating, get_rating,
    list_rated, filter_by_min_rating
)


base_vars = {"API_KEY": "secret", "DB_HOST": "localhost", "DEBUG": "true"}


def test_get_ratings_empty_when_no_meta():
    assert get_ratings(base_vars) == {}


def test_get_ratings_returns_existing():
    variables = {"API_KEY": "x", "__meta": {"ratings": {"API_KEY": 4}}}
    assert get_ratings(variables) == {"API_KEY": 4}


def test_get_ratings_returns_copy():
    variables = {"API_KEY": "x", "__meta": {"ratings": {"API_KEY": 3}}}
    result = get_ratings(variables)
    result["NEW"] = 5
    assert "NEW" not in get_ratings(variables)


def test_set_rating_stores_score():
    result = set_rating(base_vars, "API_KEY", 5)
    assert result["__meta"]["ratings"]["API_KEY"] == 5


def test_set_rating_does_not_mutate_original():
    set_rating(base_vars, "API_KEY", 3)
    assert "__meta" not in base_vars


def test_set_rating_raises_for_missing_key():
    with pytest.raises(KeyError):
        set_rating(base_vars, "MISSING", 3)


def test_set_rating_raises_for_meta_key():
    variables = {"__meta": {}}
    with pytest.raises(ValueError, match="metadata key"):
        set_rating(variables, "__meta", 3)


def test_set_rating_raises_for_invalid_score():
    with pytest.raises(ValueError, match="Rating must be"):
        set_rating(base_vars, "API_KEY", 6)


def test_set_rating_raises_for_zero_score():
    with pytest.raises(ValueError):
        set_rating(base_vars, "API_KEY", 0)


def test_remove_rating_removes_key():
    rated = set_rating(base_vars, "API_KEY", 4)
    unrated = remove_rating(rated, "API_KEY")
    assert "API_KEY" not in get_ratings(unrated)


def test_remove_rating_noop_when_not_rated():
    result = remove_rating(base_vars, "API_KEY")
    assert get_ratings(result) == {}


def test_get_rating_returns_none_when_not_set():
    assert get_rating(base_vars, "API_KEY") is None


def test_get_rating_returns_score_when_set():
    rated = set_rating(base_vars, "DB_HOST", 2)
    assert get_rating(rated, "DB_HOST") == 2


def test_list_rated_sorted_by_score_desc():
    v = set_rating(base_vars, "API_KEY", 3)
    v = set_rating(v, "DB_HOST", 5)
    v = set_rating(v, "DEBUG", 1)
    result = list_rated(v)
    scores = [s for _, s in result]
    assert scores == sorted(scores, reverse=True)


def test_list_rated_empty_when_none():
    assert list_rated(base_vars) == []


def test_filter_by_min_rating_returns_matching():
    v = set_rating(base_vars, "API_KEY", 4)
    v = set_rating(v, "DB_HOST", 2)
    result = filter_by_min_rating(v, 3)
    assert "API_KEY" in result
    assert "DB_HOST" not in result


def test_filter_by_min_rating_excludes_meta():
    v = set_rating(base_vars, "API_KEY", 5)
    result = filter_by_min_rating(v, 1)
    assert all(not k.startswith("__") for k in result)
