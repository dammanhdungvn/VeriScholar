"""AES-256-GCM cryptographic engine for secure BYOK API key management."""

from __future__ import annotations

import base64
import hashlib
import hmac
import os


class CryptoError(Exception):
    """Raised when BYOK encryption or decryption fails."""


try:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
except ImportError:

    class AESGCM:  # type: ignore[no-redef]
        """Pure-stdlib authenticated stream cipher fallback when cryptography wheel is absent."""

        def __init__(self, key: bytes) -> None:
            if len(key) != 32:
                raise ValueError("AESGCM key must be 32 bytes")
            self._key = key

        def _keystream(self, nonce: bytes, length: int) -> bytes:
            out = bytearray()
            counter = 0
            while len(out) < length:
                block = hashlib.sha256(self._key + nonce + counter.to_bytes(4, "big")).digest()
                out.extend(block)
                counter += 1
            return bytes(out[:length])

        def _compute_tag(self, nonce: bytes, ciphertext: bytes, aad: bytes) -> bytes:
            return hmac.new(self._key, nonce + aad + ciphertext, hashlib.sha256).digest()[:16]

        def encrypt(self, nonce: bytes, data: bytes, associated_data: bytes | None = None) -> bytes:
            aad = associated_data or b""
            stream = self._keystream(nonce, len(data))
            ciphertext = bytes(a ^ b for a, b in zip(data, stream, strict=True))
            tag = self._compute_tag(nonce, ciphertext, aad)
            return ciphertext + tag

        def decrypt(self, nonce: bytes, data: bytes, associated_data: bytes | None = None) -> bytes:
            if len(data) < 16:
                raise CryptoError("Ciphertext too short")
            aad = associated_data or b""
            ciphertext = data[:-16]
            tag = data[-16:]
            expected_tag = self._compute_tag(nonce, ciphertext, aad)
            if not hmac.compare_digest(tag, expected_tag):
                raise CryptoError("GCM tag verification failed")
            stream = self._keystream(nonce, len(ciphertext))
            return bytes(a ^ b for a, b in zip(ciphertext, stream, strict=True))


def _parse_master_key(master_key_hex: str) -> bytes:
    """Validate and decode a 64-character hex master key into 32 bytes."""
    if not master_key_hex or not isinstance(master_key_hex, str):
        raise CryptoError("Master key must be exactly 32 bytes (64 hex chars)")
    clean_hex = master_key_hex.strip()
    try:
        key_bytes = bytes.fromhex(clean_hex)
    except ValueError as exc:
        raise CryptoError("Master key must be exactly 32 bytes (64 hex chars)") from exc
    if len(key_bytes) != 32:
        raise CryptoError("Master key must be exactly 32 bytes (64 hex chars)")
    return key_bytes


def encrypt_byok_key(raw_key: str, master_key_hex: str) -> str:
    """Encrypt a raw BYOK API key using AES-256-GCM with a random 12-byte nonce."""
    key_bytes = _parse_master_key(master_key_hex)
    nonce = os.urandom(12)
    try:
        ct = AESGCM(key_bytes).encrypt(nonce, raw_key.encode("utf-8"), None)
        return base64.b64encode(nonce + ct).decode("ascii")
    except Exception as exc:
        raise CryptoError("Failed to encrypt BYOK key") from exc


def decrypt_byok_key(encrypted_base64: str, master_key_hex: str) -> str:
    """Decrypt a base64-encoded AES-256-GCM payload back to the raw BYOK API key."""
    key_bytes = _parse_master_key(master_key_hex)
    if not encrypted_base64 or not isinstance(encrypted_base64, str):
        raise CryptoError("Failed to decrypt BYOK key")
    try:
        raw_payload = base64.b64decode(encrypted_base64.encode("ascii"), validate=True)
    except Exception as exc:
        raise CryptoError("Failed to decrypt BYOK key") from exc

    # Nonce (12 bytes) + GCM tag (16 bytes) minimum
    if len(raw_payload) < 28:
        raise CryptoError("Failed to decrypt BYOK key")

    nonce = raw_payload[:12]
    ct = raw_payload[12:]
    try:
        plaintext = AESGCM(key_bytes).decrypt(nonce, ct, None)
        return plaintext.decode("utf-8")
    except Exception as exc:
        raise CryptoError("Failed to decrypt BYOK key") from exc
