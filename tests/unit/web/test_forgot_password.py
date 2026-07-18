from __future__ import annotations

from dataclasses import dataclass, field
from types import SimpleNamespace

from fastapi.testclient import TestClient

import app.main as app_main
from app.main import create_app


@dataclass
class FakeForgotPasswordService:
    error: Exception | None = None
    request_calls: list[str] = field(default_factory=list)

    def request_password_reset(self, email: str) -> bool:
        self.request_calls.append(email)
        if self.error is not None:
            raise self.error
        return True


def _build_test_app(monkeypatch, auth_service: FakeForgotPasswordService):
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


def test_forgot_password_page_renders_form(monkeypatch) -> None:
    app = _build_test_app(monkeypatch, FakeForgotPasswordService())

    with TestClient(app) as client:
        response = client.get("/forgot-password")

    assert response.status_code == 200
    assert "Forgot password" in response.text
    assert "Enter your account email" in response.text
    assert 'name="email"' in response.text
    assert 'href="/login"' in response.text


def test_forgot_password_submit_shows_generic_success_message(monkeypatch) -> None:
    service = FakeForgotPasswordService()
    app = _build_test_app(monkeypatch, service)

    with TestClient(app) as client:
        response = client.post("/forgot-password", data={"email": "visitor@example.com"})

    assert response.status_code == 200
    assert service.request_calls == ["visitor@example.com"]
    assert "Check your email" in response.text
    assert "If an account exists for visitor@example.com" in response.text


def test_forgot_password_submit_does_not_leak_whether_account_exists(monkeypatch) -> None:
    # request_password_reset returns False silently for unknown/unverified accounts;
    # the route must render the same success copy regardless, to avoid user enumeration.
    class SilentFalseService(FakeForgotPasswordService):
        def request_password_reset(self, email: str) -> bool:
            self.request_calls.append(email)
            return False

    service = SilentFalseService()
    app = _build_test_app(monkeypatch, service)

    with TestClient(app) as client:
        response = client.post("/forgot-password", data={"email": "unknown@example.com"})

    assert response.status_code == 200
    assert service.request_calls == ["unknown@example.com"]
    assert "Check your email" in response.text
    assert "If an account exists for unknown@example.com" in response.text


def test_forgot_password_submit_rejects_invalid_email(monkeypatch) -> None:
    service = FakeForgotPasswordService()
    app = _build_test_app(monkeypatch, service)

    with TestClient(app) as client:
        response = client.post("/forgot-password", data={"email": "not-an-email"})

    assert response.status_code == 200
    assert service.request_calls == []
    assert "Enter a valid email address." in response.text
    assert "alert-danger" in response.text


def test_forgot_password_submit_shows_friendly_error_on_send_failure(monkeypatch) -> None:
    service = FakeForgotPasswordService(error=RuntimeError("brevo unavailable"))
    app = _build_test_app(monkeypatch, service)

    with TestClient(app) as client:
        response = client.post("/forgot-password", data={"email": "visitor@example.com"})

    assert response.status_code == 200
    assert service.request_calls == ["visitor@example.com"]
    assert "We couldn&#39;t send the reset email" in response.text
    assert "alert-danger" in response.text
