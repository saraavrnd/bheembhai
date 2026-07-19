from __future__ import annotations

from dataclasses import dataclass, field
from types import SimpleNamespace

from fastapi.testclient import TestClient

import app.main as app_main
from app.auth.repository import UserRecord
from app.main import create_app


@dataclass
class FakeLoginService:
    user: UserRecord | None = None
    error: Exception | None = None
    authenticate_calls: list[tuple[str, str]] = field(default_factory=list)

    def authenticate_user(self, *, email: str, password: str) -> UserRecord:
        self.authenticate_calls.append((email, password))
        if self.error is not None:
            raise self.error
        assert self.user is not None
        return self.user


def _build_test_app(monkeypatch, auth_service: FakeLoginService):
    monkeypatch.setattr(app_main, "build_auth_service", lambda settings: auth_service)
    monkeypatch.setattr(app_main, "build_browser_auth_service", lambda settings: object())
    monkeypatch.setattr(
        app_main,
        "get_settings",
        lambda: SimpleNamespace(
            app_name="BheemBhai",
            version="0.1.0",
            api_version="v1",
            database_url="sqlite+pysqlite://",
            secret_key="test-secret",
            public_base_url="http://localhost:8000",
        ),
    )
    return create_app()


def test_login_page_renders_form(monkeypatch) -> None:
    service = FakeLoginService(
        user=UserRecord(
            id="user-1",
            email="visitor@example.com",
            password_hash="hashed",
            platform_role="standard",
            email_verified_at=None,
        )
    )
    app = _build_test_app(monkeypatch, service)

    with TestClient(app) as client:
        response = client.get("/login")

    assert response.status_code == 200
    assert "Sign in" in response.text
    assert "Sign in to BheemBhai" in response.text
    assert "Verify your email before signing in" not in response.text
    assert "Contact support" not in response.text
    assert 'href="/forgot-password"' in response.text
    assert 'href="/signup"' in response.text
    assert "Don&#39;t have an account?" in response.text
    assert 'class="auth-input__icon"' in response.text
    assert 'name="email"' in response.text
    assert 'name="password"' in response.text


def test_login_submit_sets_session_cookie_and_success_state(monkeypatch) -> None:
    service = FakeLoginService(
        user=UserRecord(
            id="user-1",
            email="visitor@example.com",
            password_hash="hashed",
            platform_role="standard",
            email_verified_at=None,
        )
    )
    app = _build_test_app(monkeypatch, service)

    with TestClient(app) as client:
        response = client.post(
            "/login",
            data={"email": "visitor@example.com", "password": "LoginPassword123!"},
        )

    assert response.status_code == 200
    assert service.authenticate_calls == [("visitor@example.com", "LoginPassword123!")]
    assert "Signed in" in response.text
    assert client.cookies.get("bb_session") is not None


def test_login_submit_shows_unverified_account_error(monkeypatch) -> None:
    app = _build_test_app(
        monkeypatch,
        FakeLoginService(error=PermissionError("email not verified")),
    )

    with TestClient(app) as client:
        response = client.post(
            "/login",
            data={"email": "visitor@example.com", "password": "LoginPassword123!"},
        )

    assert response.status_code == 200
    assert "Verify your email before signing in" in response.text
    assert "alert-danger" in response.text
    assert "<h1" in response.text
    assert "Sign in failed" not in response.text
    assert response.text.count("Verify your email before signing in") == 1


def test_login_submit_shows_invalid_credentials_error(monkeypatch) -> None:
    app = _build_test_app(
        monkeypatch,
        FakeLoginService(error=ValueError("invalid credentials")),
    )

    with TestClient(app) as client:
        response = client.post(
            "/login",
            data={"email": "visitor@example.com", "password": "wrong-password"},
        )

    assert response.status_code == 200
    assert "Incorrect email or password" in response.text
    assert "alert-danger" in response.text
    assert "Sign in failed" not in response.text
    assert response.text.count("Incorrect email or password") == 1
