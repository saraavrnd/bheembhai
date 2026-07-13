from __future__ import annotations

from dataclasses import dataclass

from fastapi.testclient import TestClient

import app.main as app_main
from app.auth.repository import STANDARD_ROLE, SqlAlchemyUserRepository
from app.auth.service import AuthService
from app.auth.tokens import AuthTokenService
from app.core.settings import get_settings
from app.main import create_app
from app.notifications.email import EmailMessage


class FakePasswordHasher:
    def hash(self, password: str) -> str:
        return f"hashed::{password}"


@dataclass
class FakeEmailSender:
    messages: list[EmailMessage]

    def send(self, message: EmailMessage) -> None:
        self.messages.append(message)


def build_registration_service(
    database_url: str,
) -> tuple[AuthService, SqlAlchemyUserRepository, FakeEmailSender]:
    repository = SqlAlchemyUserRepository.from_database_url(database_url)
    repository.ensure_schema()
    email_sender = FakeEmailSender(messages=[])
    service = AuthService(
        repository=repository,
        password_hasher=FakePasswordHasher(),
        token_service=AuthTokenService("test-secret"),
        public_base_url="http://localhost:8000",
        email_sender=email_sender,
    )
    return service, repository, email_sender


def _build_test_app(monkeypatch, service: AuthService, database_url: str):
    monkeypatch.setenv("DATABASE_URL", database_url)
    get_settings.cache_clear()
    monkeypatch.setattr(
        app_main,
        "build_auth_service",
        lambda *args, **kwargs: service,
    )
    return create_app()


def test_register_endpoint_creates_user_and_returns_user_shape(monkeypatch, tmp_path) -> None:
    database_url = f"sqlite+pysqlite:///{tmp_path / 'register.db'}"
    service, repository, email_sender = build_registration_service(database_url)
    app = _build_test_app(monkeypatch, service, database_url)

    with TestClient(app) as client:
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "Visitor@Example.com",
                "password": "SignupPassword123!",
            },
        )

    stored = repository.find_by_email("visitor@example.com")
    assert response.status_code == 201
    assert stored is not None
    assert response.json() == {
        "id": stored.id,
        "email": "visitor@example.com",
        "platformRole": "STANDARD",
        "emailVerifiedAt": None,
    }
    assert stored.password_hash == "hashed::SignupPassword123!"
    assert stored.platform_role == STANDARD_ROLE
    assert stored.email_verified_at is None
    assert len(email_sender.messages) == 1


def test_register_endpoint_rejects_invalid_input(monkeypatch, tmp_path) -> None:
    database_url = f"sqlite+pysqlite:///{tmp_path / 'register.db'}"
    service, repository, email_sender = build_registration_service(database_url)
    app = _build_test_app(monkeypatch, service, database_url)

    with TestClient(app) as client:
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "not-an-email",
                "password": "short",
            },
        )

    assert response.status_code == 422
    assert repository.find_by_email("not-an-email") is None
    assert len(email_sender.messages) == 0
