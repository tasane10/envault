"""Vault compression utilities — gzip-based compress/decompress for vault exports."""

import gzip
import json
import base64
from typing import Dict, Any


def compress_variables(variables: Dict[str, Any]) -> str:
    """Serialize and compress a variables dict to a base64-encoded gzip string."""
    payload = json.dumps(variables, sort_keys=True).encode("utf-8")
    compressed = gzip.compress(payload, compresslevel=9)
    return base64.b64encode(compressed).decode("ascii")


def decompress_variables(blob: str) -> Dict[str, Any]:
    """Decompress a base64-encoded gzip string back to a variables dict.

    Raises:
        ValueError: If the blob is not valid base64 or gzip data.
        json.JSONDecodeError: If the decompressed payload is not valid JSON.
    """
    try:
        raw = base64.b64decode(blob)
    except Exception as exc:
        raise ValueError(f"Invalid base64 payload: {exc}") from exc
    try:
        payload = gzip.decompress(raw)
    except Exception as exc:
        raise ValueError(f"Invalid gzip payload: {exc}") from exc
    return json.loads(payload.decode("utf-8"))


def compress_ratio(variables: Dict[str, Any]) -> float:
    """Return the compression ratio (compressed / original) as a float.

    A value < 1.0 means the compressed form is smaller.
    """
    original = json.dumps(variables, sort_keys=True).encode("utf-8")
    compressed_b64 = compress_variables(variables)
    compressed_bytes = base64.b64decode(compressed_b64)
    if not original:
        return 1.0
    return len(compressed_bytes) / len(original)
