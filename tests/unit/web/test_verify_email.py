from __future__ import annotations

from types import SimpleNamespace

from fastapi.testclient import TestClient

from app.auth.repository import UserRecord
from app.auth.tokens import InvalidTokenError
from app.main import create_app
from app.web import router as web_router


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


def _patch_browser_service(monkeypatch, service: FakeAuthService) -> None:
    monkeypatch.setattr(web_router, "_browser_auth_service", lambda settings: service)
    monkeypatch.setattr(
        web_router,
        "get_settings",
        lambda: SimpleNamespace(app_name="BeemBhai", database_url="sqlite+pysqlite://"),
    )


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
    _patch_browser_service(monkeypatch, service)

    client = TestClient(create_app())
    response = client.get("/verify-email")

    assert response.status_code == 200
    assert "window.location.hash" in response.text
    assert "verify-form" in response.text


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
    _patch_browser_service(monkeypatch, service)

    client = TestClient(create_app())
    response = client.post("/verify-email", data={"token": "abc123"})

    assert response.status_code == 200
    assert service.verification_tokens == ["abc123"]
    assert "Email verified" in response.text
    assert "admin@example.com" in response.text


def test_verify_email_submit_shows_failure_for_invalid_token(monkeypatch) -> None:
    service = FakeAuthService(verification_error=InvalidTokenError("invalid or expired token"))
    _patch_browser_service(monkeypatch, service)

    client = TestClient(create_app())
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
    _patch_browser_service(monkeypatch, service)

    client = TestClient(create_app())
    response = client.get("/reset-password")

    assert response.status_code == 200
    assert "window.location.hash" in response.text
    assert "new_password" in response.text


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
    _patch_browser_service(monkeypatch, service)

    client = TestClient(create_app())
    response = client.post(
        "/reset-password",
        data={"token": "reset-token", "new_password": "NewPassword123!"},
    )

    assert response.status_code == 200
    assert service.reset_tokens == [("reset-token", "NewPassword123!")]
    assert "Password updated" in response.text


def test_reset_password_submit_shows_failure_for_invalid_token(monkeypatch) -> None:
    service = FakeAuthService(password_reset_error=InvalidTokenError("invalid or expired token"))
    _patch_browser_service(monkeypatch, service)

    client = TestClient(create_app())
    response = client.post(
        "/reset-password",
        data={"token": "bad-reset-token", "new_password": "NewPassword123!"},
    )

    assert response.status_code == 200
    assert service.reset_tokens == [("bad-reset-token", "NewPassword123!")]
    assert "Reset failed" in response.text
    assert "expired" in response.text
