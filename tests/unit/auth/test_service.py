from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

import pytest
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.auth.repository import ADMIN_ROLE, STANDARD_ROLE, SqlAlchemyUserRepository
from app.auth.service import AuthService
from app.auth.tokens import AuthTokenService, InvalidTokenError
from app.notifications.email import EmailDeliveryError, EmailMessage


class FakePasswordHasher:
    def hash(self, password: str) -> str:
        return f"hashed::{password}"


@dataclass
class FakeEmailSender:
    messages: list[EmailMessage]

    def send(self, message: EmailMessage) -> None:
        self.messages.append(message)


@dataclass
class FailingEmailSender:
    error: Exception

    def send(self, message: EmailMessage) -> None:  # pragma: no cover - trivial
        raise self.error


def build_service() -> tuple[AuthService, SqlAlchemyUserRepository, FakeEmailSender]:
    engine = create_engine(
        "sqlite+pysqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    repository = SqlAlchemyUserRepository(
        engine=engine,
        session_factory=sessionmaker(bind=engine, autoflush=False, expire_on_commit=False),
    )
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


def build_service_with_sender(
    email_sender: FakeEmailSender | FailingEmailSender,
) -> tuple[AuthService, SqlAlchemyUserRepository]:
    engine = create_engine(
        "sqlite+pysqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    repository = SqlAlchemyUserRepository(
        engine=engine,
        session_factory=sessionmaker(bind=engine, autoflush=False, expire_on_commit=False),
    )
    repository.ensure_schema()
    service = AuthService(
        repository=repository,
        password_hasher=FakePasswordHasher(),
        token_service=AuthTokenService("test-secret"),
        public_base_url="http://localhost:8000",
        email_sender=email_sender,
    )
    return service, repository


def token_from_message(message: EmailMessage) -> str:
    assert message.text_content is not None
    return message.text_content.split("#token=", 1)[1]


def test_bootstrap_creates_first_platform_admin_and_sends_activation_email() -> None:
    service, repository, email_sender = build_service()

    result = service.bootstrap_platform_admin(
        email="admin@example.com",
        password="SeedPassword123!",
    )

    stored = repository.find_by_email("admin@example.com")
    assert result.action == "created"
    assert result.verification_email_sent is True
    assert result.user.email == "admin@example.com"
    assert stored is not None
    assert stored.password_hash == "hashed::SeedPassword123!"
    assert stored.platform_role == ADMIN_ROLE
    assert stored.email_verified_at is None
    assert len(email_sender.messages) == 1
    assert email_sender.messages[0].to_email == "admin@example.com"
    assert email_sender.messages[0].text_content is not None
    assert "verify-email#token=" in email_sender.messages[0].text_content


def test_bootstrap_is_idempotent_when_admin_already_exists() -> None:
    service, repository, email_sender = build_service()
    repository.create_user(
        email="admin@example.com",
        password_hash="existing-hash",
        platform_role=ADMIN_ROLE,
        email_verified_at=datetime.now(UTC),
    )

    result = service.bootstrap_platform_admin(
        email="different@example.com",
        password="NewPassword456!",
    )

    stored = repository.find_first_admin()
    assert result.action == "skipped"
    assert result.skipped_reason == "platform_admin_exists"
    assert result.user.email == "admin@example.com"
    assert stored is not None
    assert stored.password_hash == "existing-hash"
    assert stored.platform_role == ADMIN_ROLE
    assert len(email_sender.messages) == 0


def test_bootstrap_rolls_back_when_verification_email_delivery_fails() -> None:
    failing_sender = FailingEmailSender(error=EmailDeliveryError("simulated Brevo failure"))
    service, repository = build_service_with_sender(failing_sender)

    with pytest.raises(EmailDeliveryError):
        service.bootstrap_platform_admin(
            email="admin@example.com",
            password="SeedPassword123!",
        )

    assert repository.find_by_email("admin@example.com") is None

    retry_service = AuthService(
        repository=repository,
        password_hasher=FakePasswordHasher(),
        token_service=AuthTokenService("test-secret"),
        public_base_url="http://localhost:8000",
        email_sender=FakeEmailSender(messages=[]),
    )

    retry_result = retry_service.bootstrap_platform_admin(
        email="admin@example.com",
        password="SeedPassword123!",
    )

    assert retry_result.action == "created"
    assert repository.find_by_email("admin@example.com") is not None


def test_upsert_user_updates_existing_record_without_duplicate() -> None:
    service, repository, email_sender = build_service()
    repository.create_user(
        email="member@example.com",
        password_hash="original-hash",
        platform_role=STANDARD_ROLE,
        email_verified_at=datetime.now(UTC),
    )

    result = service.upsert_user(
        email="member@example.com",
        password="UpdatedPassword789!",
        platform_role=ADMIN_ROLE,
    )

    stored = repository.find_by_email("member@example.com")
    assert result.action == "updated"
    assert stored is not None
    assert stored.password_hash == "hashed::UpdatedPassword789!"
    assert stored.platform_role == ADMIN_ROLE
    assert stored.email_verified_at is not None
    assert len(email_sender.messages) == 0


def test_register_user_creates_standard_user_and_sends_verification_email() -> None:
    service, repository, email_sender = build_service()

    result = service.register_user(
        email="  New.User@Example.com ",
        password="SignupPassword123!",
    )

    stored = repository.find_by_email("new.user@example.com")
    assert result.action == "created"
    assert result.verification_email_sent is True
    assert result.user.email == "new.user@example.com"
    assert result.user.password_hash == "hashed::SignupPassword123!"
    assert result.user.platform_role == STANDARD_ROLE
    assert result.user.email_verified_at is None
    assert stored is not None
    assert stored.password_hash == "hashed::SignupPassword123!"
    assert stored.platform_role == STANDARD_ROLE
    assert stored.email_verified_at is None
    assert len(email_sender.messages) == 1
    assert email_sender.messages[0].to_email == "new.user@example.com"
    assert email_sender.messages[0].text_content is not None
    assert "verify-email#token=" in email_sender.messages[0].text_content


def test_register_user_rejects_duplicate_email_without_creating_duplicate_user() -> None:
    service, repository, email_sender = build_service()
    existing = repository.create_user(
        email="member@example.com",
        password_hash="original-hash",
        platform_role=STANDARD_ROLE,
    )

    result = service.register_user(
        email="MEMBER@example.com",
        password="SignupPassword456!",
    )

    stored = repository.find_by_email("member@example.com")
    assert result.action == "skipped"
    assert result.skipped_reason == "duplicate_email"
    assert result.user.id == existing.id
    assert result.user.email == "member@example.com"
    assert stored is not None
    assert stored.password_hash == "original-hash"
    assert len(email_sender.messages) == 0


def test_register_user_translates_racing_duplicate_into_conflict(monkeypatch) -> None:
    service, repository, email_sender = build_service()
    existing = repository.create_user(
        email="member@example.com",
        password_hash="original-hash",
        platform_role=STANDARD_ROLE,
    )

    def raise_duplicate(self, session, *, email, password_hash, platform_role, email_verified_at):
        raise IntegrityError("insert", {}, Exception("duplicate key"))

    monkeypatch.setattr(type(repository), "create_user_in_session", raise_duplicate)

    result = service.register_user(
        email="member@example.com",
        password="SignupPassword456!",
    )

    assert result.action == "skipped"
    assert result.skipped_reason == "duplicate_email"
    assert result.user.id == existing.id
    assert len(email_sender.messages) == 0


def test_email_verification_request_and_confirmation_activate_user() -> None:
    service, repository, email_sender = build_service()
    repository.create_user(
        email="pending@example.com",
        password_hash="pending-hash",
        platform_role=STANDARD_ROLE,
    )

    assert service.request_email_verification("pending@example.com") is True
    assert len(email_sender.messages) == 1

    token = token_from_message(email_sender.messages[0])
    verified = service.confirm_email_verification(token)

    assert verified.email == "pending@example.com"
    assert verified.email_verified_at is not None
    assert repository.find_by_email("pending@example.com").email_verified_at is not None


def test_password_reset_request_and_confirmation_update_password() -> None:
    service, repository, email_sender = build_service()
    repository.create_user(
        email="verified@example.com",
        password_hash="original-hash",
        platform_role=STANDARD_ROLE,
        email_verified_at=datetime.now(UTC),
    )

    assert service.request_password_reset("verified@example.com") is True
    assert len(email_sender.messages) == 1
    token = token_from_message(email_sender.messages[0])

    updated = service.confirm_password_reset(token, "NewPassword456!")

    assert updated.password_hash == "hashed::NewPassword456!"
    assert repository.find_by_email("verified@example.com").password_hash == (
        "hashed::NewPassword456!"
    )


def test_invalid_verification_token_is_rejected() -> None:
    service, _, _ = build_service()

    with pytest.raises(InvalidTokenError):
        service.confirm_email_verification("invalid-token")
