from __future__ import annotations

import io
from dataclasses import dataclass
from typing import Protocol

from minio import Minio

from app.secure_storage.encryption import EnvelopeCipher


class BucketClient(Protocol):
    def bucket_exists(self, bucket_name: str) -> bool: ...

    def make_bucket(self, bucket_name: str) -> None: ...

    def put_object(
        self,
        bucket_name: str,
        object_name: str,
        data: io.BytesIO,
        length: int,
        content_type: str | None = None,
    ) -> object: ...

    def get_object(self, bucket_name: str, object_name: str) -> object: ...


@dataclass(slots=True)
class MinioSecureStorageService:
    client: BucketClient
    cipher: EnvelopeCipher
    bucket_name: str = "secure-storage"
    object_prefix: str = "secrets"

    @classmethod
    def from_settings(
        cls,
        minio_endpoint: str,
        access_key: str,
        secret_key: str,
        cipher: EnvelopeCipher,
        bucket_name: str = "secure-storage",
    ) -> MinioSecureStorageService:
        client = Minio(
            endpoint=minio_endpoint.replace("http://", "").replace("https://", ""),
            access_key=access_key,
            secret_key=secret_key,
            secure=minio_endpoint.startswith("https://"),
        )
        return cls(client=client, cipher=cipher, bucket_name=bucket_name)

    def ensure_bucket(self) -> None:
        if not self.client.bucket_exists(self.bucket_name):
            self.client.make_bucket(self.bucket_name)

    def put_secret(self, name: str, value: str) -> str:
        self.ensure_bucket()
        object_name = self._object_name(name)
        encrypted_payload = self.cipher.encrypt(
            value.encode("utf-8"), aad=object_name.encode("utf-8")
        )
        self.client.put_object(
            self.bucket_name,
            object_name,
            io.BytesIO(encrypted_payload),
            len(encrypted_payload),
            content_type="application/json",
        )
        return f"minio://{self.bucket_name}/{object_name}"

    def get_secret(self, reference: str) -> str:
        bucket_name, object_name = self._parse_reference(reference)
        response = self.client.get_object(bucket_name, object_name)
        try:
            payload = response.read()
        finally:
            response.close()
            response.release_conn()
        plaintext = self.cipher.decrypt(payload, aad=object_name.encode("utf-8"))
        return plaintext.decode("utf-8")

    def _object_name(self, name: str) -> str:
        normalized = name.strip().replace(" ", "-").lower()
        return f"{self.object_prefix}/{normalized}.json"

    @staticmethod
    def _parse_reference(reference: str) -> tuple[str, str]:
        if not reference.startswith("minio://"):
            raise ValueError("Unsupported secure storage reference")
        bucket_and_object = reference.removeprefix("minio://")
        bucket_name, object_name = bucket_and_object.split("/", 1)
        return bucket_name, object_name
