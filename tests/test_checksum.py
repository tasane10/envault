"""Tests for envault.checksum."""

import pytest
from pathlib import Path

from envault.checksum import (
    compute_variables_checksum,
    get_checksum_path,
    save_checksum,
    load_checksum,
    verify_checksum,
    update_checksum,
)


VARS = {"API_KEY": "secret", "DEBUG": "true"}


def test_compute_checksum_returns_hex_string():
    result = compute_variables_checksum(VARS)
    assert isinstance(result, str)
    assert len(result) == 64  # SHA-256 hex


def test_compute_checksum_is_stable():
    assert compute_variables_checksum(VARS) == compute_variables_checksum(VARS)


def test_compute_checksum_order_independent():
    a = {"B": "2", "A": "1"}
    b = {"A": "1", "B": "2"}
    assert compute_variables_checksum(a) == compute_variables_checksum(b)


def test_compute_checksum_excludes_meta_keys():
    with_meta = {"KEY": "val", "__tags__": "x"}
    without_meta = {"KEY": "val"}
    assert compute_variables_checksum(with_meta) == compute_variables_checksum(without_meta)


def test_compute_checksum_changes_with_different_values():
    a = compute_variables_checksum({"KEY": "v1"})
    b = compute_variables_checksum({"KEY": "v2"})
    assert a != b


def test_compute_checksum_empty_dict():
    result = compute_variables_checksum({})
    assert isinstance(result, str) and len(result) == 64


def test_get_checksum_path_has_checksum_suffix(tmp_path):
    vault = tmp_path / "vault.json.enc"
    cp = get_checksum_path(vault)
    assert cp.suffix == ".checksum"
    assert cp.parent == tmp_path


def test_save_and_load_checksum_roundtrip(tmp_path):
    vault = tmp_path / "vault.enc"
    save_checksum(vault, "abc123")
    assert load_checksum(vault) == "abc123"


def test_load_checksum_returns_none_when_missing(tmp_path):
    vault = tmp_path / "vault.enc"
    assert load_checksum(vault) is None


def test_verify_checksum_true_when_matching(tmp_path):
    vault = tmp_path / "vault.enc"
    digest = compute_variables_checksum(VARS)
    save_checksum(vault, digest)
    assert verify_checksum(vault, VARS) is True


def test_verify_checksum_false_when_tampered(tmp_path):
    vault = tmp_path / "vault.enc"
    save_checksum(vault, "wrongdigest")
    assert verify_checksum(vault, VARS) is False


def test_verify_checksum_false_when_no_sidecar(tmp_path):
    vault = tmp_path / "vault.enc"
    assert verify_checksum(vault, VARS) is False


def test_update_checksum_saves_and_returns_digest(tmp_path):
    vault = tmp_path / "vault.enc"
    digest = update_checksum(vault, VARS)
    assert digest == compute_variables_checksum(VARS)
    assert load_checksum(vault) == digest
