from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache


@dataclass(frozen=True, slots=True)
class Settings:
    app_name: str = "BeemBhai"
    environment: str = "development"
    version: str = "0.1.0"
    api_version: str = "v1"
    public_base_url: str = "http://localhost:8000"
    secret_key: str = "change-me"
    database_url: str = "sqlite+pysqlite:///./.local/beembhai.db"
    secure_storage_key: str = "change-me-secure-storage"
    minio_endpoint: str = "http://minio:9000"
    minio_access_key: str = "beembhai"
    minio_secret_key: str = "beembhai-secret"
    minio_secure_storage_bucket: str = "secure-storage"
    brevo_api_key: str = ""
    brevo_sender_email: str = ""
    brevo_sender_name: str = "BeemBhai"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    brevo_api_key = os.getenv("BREVO_API_KEY") or os.getenv("EMAIL_BREVO_API_KEY", "")
    brevo_sender_email = (
        os.getenv("BREVO_SENDER_EMAIL")
        or os.getenv("EMAIL_FROM_ADDRESS", "")
        or os.getenv("EMAIL_BREVO_FROM_ADDRESS", "")
    )
    brevo_sender_name = os.getenv("BREVO_SENDER_NAME") or os.getenv(
        "EMAIL_BREVO_SENDER_NAME", "BeemBhai"
    )

    return Settings(
        app_name=os.getenv("BEEBHAI_APP_NAME", "BeemBhai"),
        environment=os.getenv("BEEBHAI_ENVIRONMENT", "development"),
        version=os.getenv("BEEBHAI_APP_VERSION", "0.1.0"),
        api_version=os.getenv("BEEBHAI_API_VERSION", "v1"),
        public_base_url=os.getenv("BEEBHAI_PUBLIC_BASE_URL", "http://localhost:8000"),
        secret_key=os.getenv("BEEBHAI_SECRET_KEY", "change-me"),
        database_url=os.getenv(
            "DATABASE_URL", "sqlite+pysqlite:///./.local/beembhai.db"
        ),
        secure_storage_key=os.getenv("BEEBHAI_SECURE_STORAGE_KEY", "change-me-secure-storage"),
        minio_endpoint=os.getenv("MINIO_ENDPOINT", "http://minio:9000"),
        minio_access_key=os.getenv("MINIO_ACCESS_KEY", "beembhai"),
        minio_secret_key=os.getenv("MINIO_SECRET_KEY", "beembhai-secret"),
        minio_secure_storage_bucket=os.getenv("MINIO_SECURE_STORAGE_BUCKET", "secure-storage"),
        brevo_api_key=brevo_api_key,
        brevo_sender_email=brevo_sender_email,
        brevo_sender_name=brevo_sender_name,
    )
