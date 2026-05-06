"""Tests for envault.webhook."""
from __future__ import annotations

import pytest
from unittest.mock import patch, MagicMock

from envault.webhook import (
    get_webhooks,
    set_webhook,
    remove_webhook,
    list_webhooks,
    fire_webhook,
    notify,
)


BASE: dict = {"FOO": "bar"}


def test_get_webhooks_empty_when_no_meta():
    assert get_webhooks(BASE) == {}


def test_set_webhook_stores_url():
    result = set_webhook(BASE, "set", "https://example.com/hook")
    assert "https://example.com/hook" in result["__meta__"]["__webhooks__"]["set"]


def test_set_webhook_does_not_mutate_original():
    original = dict(BASE)
    set_webhook(original, "set", "https://example.com/hook")
    assert "__meta__" not in original


def test_set_webhook_unknown_event_raises():
    with pytest.raises(ValueError, match="Unknown event"):
        set_webhook(BASE, "unknown_event", "https://example.com/hook")


def test_set_webhook_deduplicates_url():
    v = set_webhook(BASE, "set", "https://example.com/hook")
    v = set_webhook(v, "set", "https://example.com/hook")
    assert v["__meta__"]["__webhooks__"]["set"].count("https://example.com/hook") == 1


def test_set_webhook_multiple_events():
    v = set_webhook(BASE, "set", "https://a.com")
    v = set_webhook(v, "delete", "https://b.com")
    hooks = get_webhooks(v)
    assert "set" in hooks
    assert "delete" in hooks


def test_remove_webhook_removes_url():
    v = set_webhook(BASE, "set", "https://example.com/hook")
    v = remove_webhook(v, "set", "https://example.com/hook")
    hooks = get_webhooks(v)
    assert "set" not in hooks


def test_remove_webhook_missing_url_is_noop():
    v = set_webhook(BASE, "set", "https://example.com/hook")
    v2 = remove_webhook(v, "set", "https://other.com")
    assert get_webhooks(v2)["set"] == ["https://example.com/hook"]


def test_list_webhooks_returns_flat_list():
    v = set_webhook(BASE, "set", "https://a.com")
    v = set_webhook(v, "delete", "https://b.com")
    items = list_webhooks(v)
    assert {"event": "set", "url": "https://a.com"} in items
    assert {"event": "delete", "url": "https://b.com"} in items


def test_list_webhooks_empty_when_none():
    assert list_webhooks(BASE) == []


def test_fire_webhook_returns_true_on_success():
    mock_resp = MagicMock()
    mock_resp.__enter__ = lambda s: s
    mock_resp.__exit__ = MagicMock(return_value=False)
    with patch("urllib.request.urlopen", return_value=mock_resp):
        assert fire_webhook("https://example.com", "set", {}) is True


def test_fire_webhook_returns_false_on_error():
    import urllib.error
    with patch("urllib.request.urlopen", side_effect=urllib.error.URLError("refused")):
        assert fire_webhook("https://example.com", "set", {}) is False


def test_notify_calls_all_registered_urls():
    v = set_webhook(BASE, "set", "https://a.com")
    v = set_webhook(v, "set", "https://b.com")
    with patch("envault.webhook.fire_webhook", return_value=True) as mock_fire:
        results = notify(v, "set", {"key": "FOO"})
    assert len(results) == 2
    assert all(r["success"] for r in results)
    assert mock_fire.call_count == 2


def test_notify_returns_empty_when_no_hooks():
    results = notify(BASE, "set", {})
    assert results == []
