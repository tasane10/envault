"""Tests for envault.rotate."""

import json
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from envault.rotate import rotate_key, rotate_key_all_profiles
from envault.storage import save_vault, load_vault


@pytest.fixture()
def vault_file(tmp_path):
    path = tmp_path / "vault.json.enc"
    save_vault(str(path), "old-pass", {"KEY1": "value1", "KEY2": "value2"})
    return path


def test_rotate_key_re_encrypts_with_new_password(vault_file):
    result = rotate_key("old-pass", "new-pass", vault_path=str(vault_file))
    assert result["rotated"] == 2
    # Old password should no longer work
    with pytest.raises(Exception):
        load_vault(str(vault_file), "old-pass")
    # New password should work
    data = load_vault(str(vault_file), "new-pass")
    assert data == {"KEY1": "value1", "KEY2": "value2"}


def test_rotate_key_returns_summary(vault_file):
    result = rotate_key("old-pass", "new-pass", profile="default", vault_path=str(vault_file))
    assert result["profile"] == "default"
    assert result["rotated"] == 2


def test_rotate_key_wrong_old_password_raises(vault_file):
    with pytest.raises(Exception):
        rotate_key("wrong-pass", "new-pass", vault_path=str(vault_file))


def test_rotate_key_empty_vault(tmp_path):
    path = tmp_path / "empty.enc"
    save_vault(str(path), "old-pass", {})
    result = rotate_key("old-pass", "new-pass", vault_path=str(path))
    assert result["rotated"] == 0
    data = load_vault(str(path), "new-pass")
    assert data == {}


def test_rotate_key_records_audit_event(vault_file):
    with patch("envault.rotate.record_event") as mock_record:
        rotate_key("old-pass", "new-pass", profile="prod", vault_path=str(vault_file))
        mock_record.assert_called_once()
        call_kwargs = mock_record.call_args[1]
        assert call_kwargs["action"] == "rotate_key"
        assert call_kwargs["profile"] == "prod"


def test_rotate_key_all_profiles(tmp_path):
    from envault.profiles import get_profile_vault_path

    for name in ("default", "staging", "prod"):
        p = get_profile_vault_path(name, base_dir=str(tmp_path))
        p.parent.mkdir(parents=True, exist_ok=True)
        save_vault(str(p), "old-pass", {"X": name})

    results = rotate_key_all_profiles("old-pass", "new-pass", base_dir=str(tmp_path))
    assert len(results) == 3
    profile_names = {r["profile"] for r in results}
    assert profile_names == {"default", "staging", "prod"}
