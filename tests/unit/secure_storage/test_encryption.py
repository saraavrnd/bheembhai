from app.secure_storage.encryption import EnvelopeCipher


def test_envelope_cipher_round_trip() -> None:
    cipher = EnvelopeCipher.from_secret("super-secret")
    payload = cipher.encrypt(b"brevo-api-key", aad=b"secret-reference")

    assert b"brevo-api-key" not in payload
    assert cipher.decrypt(payload, aad=b"secret-reference") == b"brevo-api-key"
