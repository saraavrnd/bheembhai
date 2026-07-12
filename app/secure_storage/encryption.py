from __future__ import annotations

import base64
import hashlib
import json
import os
from dataclasses import dataclass

from cryptography.hazmat.primitives.ciphers.aead import AESGCM


@dataclass(frozen=True, slots=True)
class EnvelopeCipher:
    key_material: bytes
    key_id: str = "v1"

    @classmethod
    def from_secret(cls, secret: str, key_id: str = "v1") -> EnvelopeCipher:
        digest = hashlib.sha256(secret.encode("utf-8")).digest()
        return cls(key_material=digest, key_id=key_id)

    def encrypt(self, plaintext: bytes, aad: bytes = b"") -> bytes:
        nonce = os.urandom(12)
        ciphertext = AESGCM(self.key_material).encrypt(nonce, plaintext, aad)
        envelope = {
            "version": self.key_id,
            "nonce": base64.b64encode(nonce).decode("ascii"),
            "ciphertext": base64.b64encode(ciphertext).decode("ascii"),
        }
        return json.dumps(envelope, separators=(",", ":")).encode("utf-8")

    def decrypt(self, payload: bytes, aad: bytes = b"") -> bytes:
        envelope = json.loads(payload.decode("utf-8"))
        nonce = base64.b64decode(envelope["nonce"])
        ciphertext = base64.b64decode(envelope["ciphertext"])
        return AESGCM(self.key_material).decrypt(nonce, ciphertext, aad)
