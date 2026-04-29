"""Unit tests for envault.share."""

from __future__ import annotations

import json
import time

import pytest

from envault.share import (
    bundle_from_file,
    bundle_to_file,
    create_share_bundle,
    generate_share_token,
    open_share_bundle,
)

PASSWORD = "s3cr3t"

SAMPLE_VARS = {
    "DB_HOST": "localhost",
    "DB_PORT": "5432",
    "__meta__tags": "should-be-excluded",
}


# ---------------------------------------------------------------------------
# generate_share_token
# ---------------------------------------------------------------------------

def test_generate_share_token_is_32_chars():
    assert len(generate_share_token()) == 32


def test_generate_share_token_is_unique():
    assert generate_share_token() != generate_share_token()


# ---------------------------------------------------------------------------
# create_share_bundle
# ---------------------------------------------------------------------------

def test_create_share_bundle_has_required_keys():
    bundle = create_share_bundle(SAMPLE_VARS, PASSWORD)
    assert "token" in bundle
    assert "payload" in bundle
    assert "created_at" in bundle


def test_create_share_bundle_excludes_meta_keys():
    bundle = create_share_bundle(SAMPLE_VARS, PASSWORD)
    recovered = open_share_bundle(bundle, PASSWORD)
    assert "__meta__tags" not in recovered


def test_create_share_bundle_key_whitelist():
    bundle = create_share_bundle(SAMPLE_VARS, PASSWORD, keys=["DB_HOST"])
    recovered = open_share_bundle(bundle, PASSWORD)
    assert recovered == {"DB_HOST": "localhost"}


def test_create_share_bundle_with_ttl_sets_expires_at():
    before = int(time.time())
    bundle = create_share_bundle(SAMPLE_VARS, PASSWORD, ttl_seconds=3600)
    assert bundle["expires_at"] >= before + 3600


def test_create_share_bundle_no_ttl_omits_expires_at():
    bundle = create_share_bundle(SAMPLE_VARS, PASSWORD)
    assert "expires_at" not in bundle


# ---------------------------------------------------------------------------
# open_share_bundle
# ---------------------------------------------------------------------------

def test_open_share_bundle_roundtrip():
    bundle = create_share_bundle(SAMPLE_VARS, PASSWORD)
    recovered = open_share_bundle(bundle, PASSWORD)
    assert recovered["DB_HOST"] == "localhost"
    assert recovered["DB_PORT"] == "5432"


def test_open_share_bundle_wrong_password_raises():
    bundle = create_share_bundle(SAMPLE_VARS, PASSWORD)
    with pytest.raises(Exception):
        open_share_bundle(bundle, "wrongpassword")


def test_open_share_bundle_expired_raises():
    bundle = create_share_bundle(SAMPLE_VARS, PASSWORD, ttl_seconds=1)
    bundle["expires_at"] = int(time.time()) - 1  # force expiry
    with pytest.raises(ValueError, match="expired"):
        open_share_bundle(bundle, PASSWORD)


# ---------------------------------------------------------------------------
# bundle_to_file / bundle_from_file
# ---------------------------------------------------------------------------

def test_bundle_file_roundtrip(tmp_path):
    path = str(tmp_path / "share.json")
    bundle = create_share_bundle(SAMPLE_VARS, PASSWORD)
    bundle_to_file(bundle, path)
    loaded = bundle_from_file(path)
    assert loaded["token"] == bundle["token"]
    recovered = open_share_bundle(loaded, PASSWORD)
    assert recovered["DB_HOST"] == "localhost"


def test_bundle_to_file_creates_parent_dirs(tmp_path):
    path = str(tmp_path / "nested" / "dir" / "share.json")
    bundle = create_share_bundle(SAMPLE_VARS, PASSWORD)
    bundle_to_file(bundle, path)  # should not raise
    assert bundle_from_file(path)["token"] == bundle["token"]
