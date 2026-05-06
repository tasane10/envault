"""Tests for envault.compress."""

import json
import pytest
from envault.compress import compress_variables, decompress_variables, compress_ratio


SAMPLE = {
    "DATABASE_URL": "postgres://user:pass@localhost/db",
    "SECRET_KEY": "supersecretvalue",
    "DEBUG": "false",
}


def test_compress_returns_string():
    blob = compress_variables(SAMPLE)
    assert isinstance(blob, str)
    assert len(blob) > 0


def test_compress_decompress_roundtrip():
    blob = compress_variables(SAMPLE)
    result = decompress_variables(blob)
    assert result == SAMPLE


def test_compress_empty_dict():
    blob = compress_variables({})
    result = decompress_variables(blob)
    assert result == {}


def test_compress_produces_valid_base64():
    import base64
    blob = compress_variables(SAMPLE)
    # Should not raise
    base64.b64decode(blob)


def test_decompress_invalid_base64_raises():
    with pytest.raises(ValueError, match="Invalid base64"):
        decompress_variables("!!!not-base64!!!")


def test_decompress_invalid_gzip_raises():
    import base64
    bad_blob = base64.b64encode(b"not gzip data").decode()
    with pytest.raises(ValueError, match="Invalid gzip"):
        decompress_variables(bad_blob)


def test_decompress_invalid_json_raises():
    import base64
    import gzip
    bad_json = gzip.compress(b"{invalid json")
    bad_blob = base64.b64encode(bad_json).decode()
    with pytest.raises(json.JSONDecodeError):
        decompress_variables(bad_blob)


def test_compress_ratio_returns_float():
    ratio = compress_ratio(SAMPLE)
    assert isinstance(ratio, float)


def test_compress_ratio_empty_dict_returns_one():
    ratio = compress_ratio({})
    assert ratio == 1.0


def test_compress_ratio_large_repetitive_data_is_small():
    big = {f"KEY_{i}": "AAAAAAAAAAAAAAAAAAAAAAAAAAAA" for i in range(50)}
    ratio = compress_ratio(big)
    assert ratio < 1.0
