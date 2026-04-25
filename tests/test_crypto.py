"""Tests for envault.crypto encryption/decryption utilities."""

import pytest
from envault.crypto import encrypt, decrypt


PASSWORD = "super-secret-passphrase"
PLAINTEXT = "DATABASE_URL=postgres://user:pass@localhost/db"


def test_encrypt_returns_string():
    result = encrypt(PLAINTEXT, PASSWORD)
    assert isinstance(result, str)
    assert len(result) > 0


def test_encrypt_produces_different_ciphertexts():
    """Each encryption call should produce a unique ciphertext (random salt/nonce)."""
    result1 = encrypt(PLAINTEXT, PASSWORD)
    result2 = encrypt(PLAINTEXT, PASSWORD)
    assert result1 != result2


def test_decrypt_roundtrip():
    encoded = encrypt(PLAINTEXT, PASSWORD)
    recovered = decrypt(encoded, PASSWORD)
    assert recovered == PLAINTEXT


def test_decrypt_wrong_password_raises():
    encoded = encrypt(PLAINTEXT, PASSWORD)
    with pytest.raises(ValueError, match="Decryption failed"):
        decrypt(encoded, "wrong-password")


def test_decrypt_corrupted_payload_raises():
    encoded = encrypt(PLAINTEXT, PASSWORD)
    # Flip a character near the end to corrupt the ciphertext
    corrupted = encoded[:-4] + "AAAA"
    with pytest.raises(ValueError):
        decrypt(corrupted, PASSWORD)


def test_decrypt_invalid_base64_raises():
    with pytest.raises(ValueError, match="Invalid encoded payload"):
        decrypt("not-valid-base64!!!", PASSWORD)


def test_decrypt_too_short_payload_raises():
    import base64
    short_payload = base64.b64encode(b"tooshort").decode()
    with pytest.raises(ValueError, match="too short"):
        decrypt(short_payload, PASSWORD)


def test_encrypt_empty_string():
    encoded = encrypt("", PASSWORD)
    recovered = decrypt(encoded, PASSWORD)
    assert recovered == ""


def test_encrypt_unicode_content():
    unicode_text = "API_KEY=测试密鑰🔑"
    encoded = encrypt(unicode_text, PASSWORD)
    recovered = decrypt(encoded, PASSWORD)
    assert recovered == unicode_text
