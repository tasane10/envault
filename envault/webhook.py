"""Webhook notification support for envault events."""
from __future__ import annotations

import json
import urllib.request
import urllib.error
from typing import Any

META_KEY = "__webhooks__"
SUPPORTED_EVENTS = {"set", "delete", "rotate", "import", "restore"}


def get_webhooks(variables: dict[str, Any]) -> dict[str, list[str]]:
    """Return the webhooks mapping {event: [url, ...]} from vault metadata."""
    meta = variables.get("__meta__", {})
    return dict(meta.get(META_KEY, {}))


def set_webhook(variables: dict[str, Any], event: str, url: str) -> dict[str, Any]:
    """Register *url* for *event*. Returns a new variables dict."""
    if event not in SUPPORTED_EVENTS:
        raise ValueError(f"Unknown event '{event}'. Supported: {sorted(SUPPORTED_EVENTS)}")
    meta = dict(variables.get("__meta__", {}))
    hooks: dict[str, list[str]] = dict(meta.get(META_KEY, {}))
    urls = list(hooks.get(event, []))
    if url not in urls:
        urls.append(url)
    hooks[event] = urls
    meta[META_KEY] = hooks
    return {**variables, "__meta__": meta}


def remove_webhook(variables: dict[str, Any], event: str, url: str) -> dict[str, Any]:
    """Remove *url* from *event*. Returns a new variables dict."""
    meta = dict(variables.get("__meta__", {}))
    hooks: dict[str, list[str]] = dict(meta.get(META_KEY, {}))
    urls = [u for u in hooks.get(event, []) if u != url]
    if urls:
        hooks[event] = urls
    else:
        hooks.pop(event, None)
    meta[META_KEY] = hooks
    return {**variables, "__meta__": meta}


def list_webhooks(variables: dict[str, Any]) -> list[dict[str, str]]:
    """Return a flat list of {event, url} dicts."""
    hooks = get_webhooks(variables)
    return [{"event": event, "url": url} for event, urls in sorted(hooks.items()) for url in urls]


def fire_webhook(url: str, event: str, payload: dict[str, Any]) -> bool:
    """POST *payload* as JSON to *url*. Returns True on success."""
    body = json.dumps({"event": event, **payload}).encode()
    req = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json", "User-Agent": "envault/1.0"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=5):
            return True
    except (urllib.error.URLError, OSError):
        return False


def notify(variables: dict[str, Any], event: str, payload: dict[str, Any]) -> list[dict[str, Any]]:
    """Fire all webhooks registered for *event*. Returns results list."""
    hooks = get_webhooks(variables)
    results = []
    for url in hooks.get(event, []):
        ok = fire_webhook(url, event, payload)
        results.append({"url": url, "success": ok})
    return results
