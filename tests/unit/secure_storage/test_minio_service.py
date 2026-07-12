import io
from dataclasses import dataclass

from app.secure_storage.encryption import EnvelopeCipher
from app.secure_storage.minio_service import MinioSecureStorageService


@dataclass
class FakeObjectResponse:
    payload: bytes

    def read(self) -> bytes:
        return self.payload

    def close(self) -> None:
        return None

    def release_conn(self) -> None:
        return None


class FakeBucketClient:
    def __init__(self) -> None:
        self.buckets: set[str] = set()
        self.objects: dict[tuple[str, str], bytes] = {}

    def bucket_exists(self, bucket_name: str) -> bool:
        return bucket_name in self.buckets

    def make_bucket(self, bucket_name: str) -> None:
        self.buckets.add(bucket_name)

    def put_object(
        self,
        bucket_name: str,
        object_name: str,
        data: io.BytesIO,
        length: int,
        content_type: str | None = None,
    ) -> object:
        self.objects[(bucket_name, object_name)] = data.read(length)
        return object()

    def get_object(self, bucket_name: str, object_name: str) -> FakeObjectResponse:
        return FakeObjectResponse(self.objects[(bucket_name, object_name)])


def test_minio_secure_storage_encrypts_before_persisting() -> None:
    client = FakeBucketClient()
    cipher = EnvelopeCipher.from_secret("super-secret")
    service = MinioSecureStorageService(client=client, cipher=cipher)

    reference = service.put_secret("Brevo Api Key", "brevo-api-key")

    assert reference == "minio://secure-storage/secrets/brevo-api-key.json"
    stored_payload = client.objects[("secure-storage", "secrets/brevo-api-key.json")]
    assert b"brevo-api-key" not in stored_payload
    assert service.get_secret(reference) == "brevo-api-key"
