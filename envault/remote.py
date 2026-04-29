"""Remote sync support for envault.

Provides functionality to push and pull vault variables to/from a remote
endpoint (e.g. a shared HTTP API or S3-compatible store). Supports simple
HTTP-based sync using a pre-shared token for authentication.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any

# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------


class RemoteError(Exception):
    """Raised when a remote sync operation fails."""


# ---------------------------------------------------------------------------
# Low-level HTTP helpers
# ---------------------------------------------------------------------------


def _make_headers(token: str) -> dict[str, str]:
    """Return standard request headers including the bearer token."""
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }


def _http_get(url: str, token: str) -> Any:
    """Perform a GET request and return the parsed JSON body.

    Raises:
        RemoteError: on HTTP or network errors.
    """
    req = urllib.request.Request(url, headers=_make_headers(token), method="GET")
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:  # noqa: S310
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as exc:
        raise RemoteError(f"HTTP {exc.code} from {url}: {exc.reason}") from exc
    except urllib.error.URLError as exc:
        raise RemoteError(f"Network error reaching {url}: {exc.reason}") from exc


def _http_post(url: str, token: str, payload: Any) -> Any:
    """Perform a POST request with a JSON body and return the parsed response.

    Raises:
        RemoteError: on HTTP or network errors.
    """
    data = json.dumps(payload).encode()
    req = urllib.request.Request(url, data=data, headers=_make_headers(token), method="POST")
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:  # noqa: S310
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as exc:
        raise RemoteError(f"HTTP {exc.code} from {url}: {exc.reason}") from exc
    except urllib.error.URLError as exc:
        raise RemoteError(f"Network error reaching {url}: {exc.reason}") from exc


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def push_variables(
    base_url: str,
    token: str,
    profile: str,
    variables: dict[str, str],
) -> dict[str, Any]:
    """Push a mapping of variables to the remote vault endpoint.

    Args:
        base_url: Root URL of the remote envault server (no trailing slash).
        token:    Bearer token for authentication.
        profile:  Profile name to push into.
        variables: Plain-text key/value pairs to upload (meta keys excluded).

    Returns:
        The server response dict, typically ``{"stored": <count>}``.

    Raises:
        RemoteError: on any network or server error.
    """
    # Strip metadata keys before sending
    clean = {k: v for k, v in variables.items() if not k.startswith("__")}
    url = f"{base_url.rstrip('/')}/profiles/{profile}/variables"
    return _http_post(url, token, {"variables": clean})


def pull_variables(
    base_url: str,
    token: str,
    profile: str,
) -> dict[str, str]:
    """Pull variables for *profile* from the remote vault endpoint.

    Args:
        base_url: Root URL of the remote envault server (no trailing slash).
        token:    Bearer token for authentication.
        profile:  Profile name to fetch.

    Returns:
        A plain ``{key: value}`` dict of the remote variables.

    Raises:
        RemoteError: on any network or server error.
    """
    url = f"{base_url.rstrip('/')}/profiles/{profile}/variables"
    data = _http_get(url, token)
    if not isinstance(data, dict) or "variables" not in data:
        raise RemoteError(f"Unexpected response format from {url}")
    return data["variables"]


def list_remote_profiles(base_url: str, token: str) -> list[str]:
    """Return a list of profile names available on the remote server.

    Args:
        base_url: Root URL of the remote envault server.
        token:    Bearer token for authentication.

    Returns:
        A sorted list of profile name strings.

    Raises:
        RemoteError: on any network or server error.
    """
    url = f"{base_url.rstrip('/')}/profiles"
    data = _http_get(url, token)
    if not isinstance(data, dict) or "profiles" not in data:
        raise RemoteError(f"Unexpected response format from {url}")
    return sorted(data["profiles"])
