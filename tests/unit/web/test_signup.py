from __future__ import annotations

from dataclasses import dataclass, field
from types import SimpleNamespace

from fastapi.testclient import TestClient

import app.main as app_main
from app.auth.repository import UserRecord
from app.auth.service import UserMutationResult
from app.main import create_app


@dataclass
class FakeSignupService:
    result: UserMutationResult | None = None
    error: Exception | None = None
    register_calls: list[tuple[str, str]] = field(default_factory=list)

    def register_user(self, *, email: str, password: str) -> UserMutationResult:
        self.register_calls.append((email, password))
        if self.error is not None:
            raise self.error
        assert self.result is not None
        return self.result


def _build_test_app(monkeypatch, signup_service: FakeSignupService):
    monkeypatch.setattr(app_main, "build_auth_service", lambda settings: signup_service)
    monkeypatch.setattr(app_main, "build_browser_auth_service", lambda settings: object())
    monkeypatch.setattr(
        app_main,
        "get_settings",
        lambda: SimpleNamespace(
            app_name="BeemBhai",
            version="0.1.0",
            api_version="v1",
            database_url="sqlite+pysqlite://",
            secret_key="test-secret",
            public_base_url="http://localhost:8000",
        ),
    )
    return create_app()


def test_signup_page_renders_form(monkeypatch) -> None:
    service = FakeSignupService(
        result=UserMutationResult(
            user=UserRecord(
                id="user-1",
                email="visitor@example.com",
                password_hash="hashed",
                platform_role="standard",
                email_verified_at=None,
            ),
            action="created",
            verification_email_sent=True,
        )
    )
    app = _build_test_app(monkeypatch, service)

    with TestClient(app) as client:
        response = client.get("/signup")

    assert response.status_code == 200
    assert "Create account" in response.text
    assert "Join BeemBhai, the governed agent-orchestration platform" in response.text
    assert 'name="email"' in response.text
    assert 'name="password"' in response.text
    assert 'name="confirm_password"' in response.text
    assert "At least 8 characters with a mix of letters, numbers &amp; symbols." in response.text
    assert "Already have an account?" in response.text
    assert "Enterprise grade security" in response.text
    assert "Data privacy by design" in response.text
    assert "99.9% platform uptime" in response.text


def test_signup_submit_shows_validation_errors(monkeypatch) -> None:
    service = FakeSignupService(
        result=UserMutationResult(
            user=UserRecord(
                id="user-1",
                email="visitor@example.com",
                password_hash="hashed",
                platform_role="standard",
                email_verified_at=None,
            ),
            action="created",
            verification_email_sent=True,
        )
    )
    app = _build_test_app(monkeypatch, service)

    with TestClient(app) as client:
        response = client.post(
            "/signup",
            data={"email": "bad-email", "password": "short"},
        )

    assert response.status_code == 200
    assert service.register_calls == []
    assert "Enter a valid email address." in response.text
    assert "Password must be at least 12 characters." in response.text
    assert "status-pill--error" in response.text


def test_signup_submit_shows_duplicate_email_error(monkeypatch) -> None:
    service = FakeSignupService(
        result=UserMutationResult(
            user=UserRecord(
                id="user-1",
                email="visitor@example.com",
                password_hash="hashed",
                platform_role="standard",
                email_verified_at=None,
            ),
            action="skipped",
            verification_email_sent=False,
            skipped_reason="duplicate_email",
        )
    )
    app = _build_test_app(monkeypatch, service)

    with TestClient(app) as client:
        response = client.post(
            "/signup",
            data={"email": "visitor@example.com", "password": "SignupPassword123!"},
        )

    assert response.status_code == 200
    assert service.register_calls == [("visitor@example.com", "SignupPassword123!")]
    assert "An account with that email already exists." in response.text
    assert "status-pill--error" in response.text
