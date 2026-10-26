import pytest
from api.core.crypto import CryptoError, decrypt_byok_key, encrypt_byok_key

TEST_MASTER_KEY = "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"


def test_byok_aes_256_gcm_roundtrip():
    raw_key = "sk-proj-test1234567890abcdefghijklmnopqrstuvwxyz"
    encrypted = encrypt_byok_key(raw_key, TEST_MASTER_KEY)

    assert encrypted != raw_key
    assert "sk-proj" not in encrypted

    decrypted = decrypt_byok_key(encrypted, TEST_MASTER_KEY)
    assert decrypted == raw_key


def test_byok_encryption_rejects_invalid_master_key():
    with pytest.raises(CryptoError) as exc_info:
        encrypt_byok_key("sk-test", "short-invalid-key")
    assert "32 bytes" in str(exc_info.value)


def test_byok_decryption_detects_ciphertext_tampering():
    raw_key = "sk-proj-secret-key"
    encrypted = encrypt_byok_key(raw_key, TEST_MASTER_KEY)

    # Tamper with base64 payload
    tampered = encrypted[:-2] + ("AA" if not encrypted.endswith("AA") else "BB")
    with pytest.raises(CryptoError):
        decrypt_byok_key(tampered, TEST_MASTER_KEY)
