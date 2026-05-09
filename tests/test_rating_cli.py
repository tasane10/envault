"""Tests for envault/rating_cli.py"""

import pytest
from click.testing import CliRunner
from unittest.mock import patch, MagicMock
from envault.rating_cli import rating_cmd


@pytest.fixture
def runner():
    return CliRunner()


def _invoke(runner, args, password="pass", variables=None):
    if variables is None:
        variables = {"API_KEY": "secret", "DB_HOST": "localhost"}
    with patch("envault.rating_cli.prompt_password", return_value=password), \
         patch("envault.rating_cli.load_vault", return_value=dict(variables)), \
         patch("envault.rating_cli.save_vault") as mock_save:
        result = runner.invoke(rating_cmd, args, catch_exceptions=False)
        return result, mock_save


def test_set_rating_success(runner):
    result, mock_save = _invoke(runner, ["set", "API_KEY", "4"])
    assert result.exit_code == 0
    assert "Rated" in result.output
    assert "4/5" in result.output
    mock_save.assert_called_once()


def test_set_rating_missing_key_fails(runner):
    result, _ = _invoke(runner, ["set", "MISSING", "3"])
    assert result.exit_code != 0
    assert "Error" in result.output


def test_set_rating_invalid_score_fails(runner):
    result, _ = _invoke(runner, ["set", "API_KEY", "9"])
    assert result.exit_code != 0


def test_remove_rating_success(runner):
    variables = {"API_KEY": "x", "__meta": {"ratings": {"API_KEY": 3}}}
    result, mock_save = _invoke(runner, ["remove", "API_KEY"], variables=variables)
    assert result.exit_code == 0
    assert "removed" in result.output
    mock_save.assert_called_once()


def test_show_rating_not_rated(runner):
    result, _ = _invoke(runner, ["show", "API_KEY"])
    assert result.exit_code == 0
    assert "not rated" in result.output


def test_show_rating_with_score(runner):
    variables = {"API_KEY": "x", "__meta": {"ratings": {"API_KEY": 5}}}
    result, _ = _invoke(runner, ["show", "API_KEY"], variables=variables)
    assert result.exit_code == 0
    assert "5/5" in result.output


def test_list_ratings_no_ratings(runner):
    result, _ = _invoke(runner, ["list"])
    assert result.exit_code == 0
    assert "No rated" in result.output


def test_list_ratings_shows_entries(runner):
    variables = {
        "API_KEY": "x",
        "DB_HOST": "y",
        "__meta": {"ratings": {"API_KEY": 5, "DB_HOST": 2}}
    }
    result, _ = _invoke(runner, ["list"], variables=variables)
    assert result.exit_code == 0
    assert "API_KEY" in result.output
    assert "DB_HOST" in result.output
