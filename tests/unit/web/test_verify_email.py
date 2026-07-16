from __future__ import annotations

from fastapi.testclient import TestClient

import app.main as app_main
from app.auth.repository import UserRecord
from app.auth.tokens import InvalidTokenError
from app.main import create_app


class FakeAuthService:
    def __init__(
        self,
        *,
        user: UserRecord | None = None,
        verification_error: Exception | None = None,
        password_reset_error: Exception | None = None,
    ) -> None:
        self.user = user
        self.verification_error = verification_error
        self.password_reset_error = password_reset_error
        self.verification_tokens: list[str] = []
        self.reset_tokens: list[tuple[str, str]] = []

    def confirm_email_verification(self, token: str) -> UserRecord:
        self.verification_tokens.append(token)
        if self.verification_error is not None:
            raise self.verification_error
        assert self.user is not None
        return self.user

    def confirm_password_reset(self, token: str, new_password: str) -> UserRecord:
        self.reset_tokens.append((token, new_password))
        if self.password_reset_error is not None:
            raise self.password_reset_error
        assert self.user is not None
        return self.user


def _build_test_app(monkeypatch, service: FakeAuthService):
    monkeypatch.setattr(app_main, "build_browser_auth_service", lambda settings: service)
    return create_app()


def test_create_app_builds_browser_auth_service_once(monkeypatch) -> None:
    calls = {"build": 0}

    sentinel = object()

    def fake_build_browser_auth_service(settings: object) -> object:
        calls["build"] += 1
        return sentinel

    monkeypatch.setattr(app_main, "build_browser_auth_service", fake_build_browser_auth_service)

    app = create_app()

    assert calls["build"] == 0

    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert calls["build"] == 1
    assert app.state.browser_auth_service is sentinel


def test_verify_email_page_mentions_fragment_handshake(monkeypatch) -> None:
    service = FakeAuthService(
        user=UserRecord(
            id="user-1",
            email="admin@example.com",
            password_hash="hashed",
            platform_role="admin",
            email_verified_at=None,
        )
    )
    app = _build_test_app(monkeypatch, service)

    with TestClient(app) as client:
        response = client.get("/verify-email")

    assert response.status_code == 200
    assert "window.location.hash" in response.text
    assert "verify-form" in response.text
    assert "Verification link flow" in response.text
    assert "Email sent" in response.text
    assert "Link clicked" in response.text
    assert "Email verified" in response.text
    assert "Verified" in response.text
    assert "Resend email" in response.text


def test_verify_email_submit_confirms_valid_token(monkeypatch) -> None:
    service = FakeAuthService(
        user=UserRecord(
            id="user-1",
            email="admin@example.com",
            password_hash="hashed",
            platform_role="admin",
            email_verified_at=None,
        )
    )
    app = _build_test_app(monkeypatch, service)

    with TestClient(app) as client:
        response = client.post("/verify-email", data={"token": "abc123"})

    assert response.status_code == 200
    assert service.verification_tokens == ["abc123"]
    assert "Email verified" in response.text
    assert "admin@example.com" in response.text


def test_verify_email_submit_shows_failure_for_invalid_token(monkeypatch) -> None:
    service = FakeAuthService(verification_error=InvalidTokenError("invalid or expired token"))
    app = _build_test_app(monkeypatch, service)

    with TestClient(app) as client:
        response = client.post("/verify-email", data={"token": "bad-token"})

    assert response.status_code == 200
    assert service.verification_tokens == ["bad-token"]
    assert "Verification failed" in response.text
    assert "expired" in response.text


def test_reset_password_page_mentions_fragment_handshake(monkeypatch) -> None:
    service = FakeAuthService(
        user=UserRecord(
            id="user-2",
            email="admin@example.com",
            password_hash="hashed",
            platform_role="admin",
            email_verified_at=None,
        )
    )
    app = _build_test_app(monkeypatch, service)

    with TestClient(app) as client:
        response = client.get("/reset-password")

    assert response.status_code == 200
    assert "window.location.hash" in response.text
    assert "new_password" in response.text
    assert "Reset password" in response.text
    assert "Token loaded" in response.text
    assert "Password updated" in response.text
    assert "Update password" in response.text
    assert "Go home" in response.text


def test_reset_password_submit_confirms_new_password(monkeypatch) -> None:
    service = FakeAuthService(
        user=UserRecord(
            id="user-2",
            email="admin@example.com",
            password_hash="hashed",
            platform_role="admin",
            email_verified_at=None,
        )
    )
    app = _build_test_app(monkeypatch, service)

    with TestClient(app) as client:
        response = client.post(
            "/reset-password",
            data={"token": "reset-token", "new_password": "NewPassword123!"},
        )

    assert response.status_code == 200
    assert service.reset_tokens == [("reset-token", "NewPassword123!")]
    assert "Password updated" in response.text


def test_reset_password_submit_shows_failure_for_invalid_token(monkeypatch) -> None:
    service = FakeAuthService(password_reset_error=InvalidTokenError("invalid or expired token"))
    app = _build_test_app(monkeypatch, service)

    with TestClient(app) as client:
        response = client.post(
            "/reset-password",
            data={"token": "bad-reset-token", "new_password": "NewPassword123!"},
        )

    assert response.status_code == 200
    assert service.reset_tokens == [("bad-reset-token", "NewPassword123!")]
    assert "Reset failed" in response.text
    assert "expired" in response.text
