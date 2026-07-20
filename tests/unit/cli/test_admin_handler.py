from __future__ import annotations

import json
from types import SimpleNamespace

import pytest

from app.auth.repository import UserRecord
from app.auth.service import UserMutationResult
from app.cli import admin_handler


class FakeService:
    def __init__(self) -> None:
        self.bootstrap_calls: list[tuple[str, str, bool]] = []
        self.upsert_calls: list[tuple[str, str, str]] = []
        self.deactivate_calls: list[str] = []
        self.activate_calls: list[str] = []

    def bootstrap_platform_admin(
        self, *, email: str, password: str, verified: bool = False
    ) -> UserMutationResult:
        self.bootstrap_calls.append((email, password, verified))
        user = UserRecord(
            id="11111111-1111-1111-1111-111111111111",
            email=email,
            password_hash="hashed::" + password,
            platform_role="admin",
            email_verified_at=None,
        )
        return UserMutationResult(
            user=user, action="created", verification_email_sent=not verified
        )

    def upsert_user(
        self,
        *,
        email: str,
        password: str,
        platform_role: str = "standard",
    ) -> UserMutationResult:
        self.upsert_calls.append((email, password, platform_role))
        user = UserRecord(
            id="22222222-2222-2222-2222-222222222222",
            email=email,
            password_hash="hashed::" + password,
            platform_role=platform_role,
            email_verified_at=None,
        )
        return UserMutationResult(user=user, action="created", verification_email_sent=False)

    def deactivate_user(self, *, email: str) -> UserRecord:
        self.deactivate_calls.append(email)
        return UserRecord(
            id="33333333-3333-3333-3333-333333333333",
            email=email,
            password_hash="hashed::existing",
            platform_role="admin",
            email_verified_at=None,
            is_active=False,
        )

    def activate_user(self, *, email: str) -> UserRecord:
        self.activate_calls.append(email)
        return UserRecord(
            id="33333333-3333-3333-3333-333333333333",
            email=email,
            password_hash="hashed::existing",
            platform_role="admin",
            email_verified_at=None,
            is_active=True,
        )


def test_bootstrap_admin_requires_email_and_password() -> None:
    with pytest.raises(SystemExit) as exc:
        admin_handler.main(["bootstrap-admin", "--email", "admin@example.com"])

    assert exc.value.code == 2


def test_bootstrap_admin_delegates_to_service(monkeypatch, capsys) -> None:
    fake_service = FakeService()
    monkeypatch.setattr(admin_handler, "build_auth_service", lambda settings: fake_service)
    monkeypatch.setattr(admin_handler, "get_settings", lambda: SimpleNamespace())

    exit_code = admin_handler.main(
        [
            "bootstrap-admin",
            "--email",
            "admin@example.com",
            "--password",
            "SeedPassword123!",
        ]
    )

    captured = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert fake_service.bootstrap_calls == [("admin@example.com", "SeedPassword123!", False)]
    assert captured["command"] == "bootstrap-admin"
    assert captured["action"] == "created"
    assert captured["user"]["email"] == "admin@example.com"


def test_bootstrap_admin_passes_verified_flag_through(monkeypatch, capsys) -> None:
    fake_service = FakeService()
    monkeypatch.setattr(admin_handler, "build_auth_service", lambda settings: fake_service)
    monkeypatch.setattr(admin_handler, "get_settings", lambda: SimpleNamespace())

    exit_code = admin_handler.main(
        [
            "bootstrap-admin",
            "--email",
            "admin@example.com",
            "--password",
            "SeedPassword123!",
            "--verified",
        ]
    )

    captured = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert fake_service.bootstrap_calls == [("admin@example.com", "SeedPassword123!", True)]
    assert captured["verification_email_sent"] is False


def test_upsert_user_uses_the_explicit_role(monkeypatch, capsys) -> None:
    fake_service = FakeService()
    monkeypatch.setattr(admin_handler, "build_auth_service", lambda settings: fake_service)
    monkeypatch.setattr(admin_handler, "get_settings", lambda: SimpleNamespace())

    exit_code = admin_handler.main(
        [
            "upsert-user",
            "--email",
            "operator@example.com",
            "--password",
            "SecretPassword123!",
            "--role",
            "admin",
        ]
    )

    captured = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert fake_service.upsert_calls == [("operator@example.com", "SecretPassword123!", "admin")]
    assert captured["command"] == "upsert-user"
    assert captured["user"]["platform_role"] == "admin"


def test_deactivate_user_delegates_to_service(monkeypatch, capsys) -> None:
    fake_service = FakeService()
    monkeypatch.setattr(admin_handler, "build_auth_service", lambda settings: fake_service)
    monkeypatch.setattr(admin_handler, "get_settings", lambda: SimpleNamespace())

    exit_code = admin_handler.main(["deactivate-user", "--email", "admin@example.com"])

    captured = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert fake_service.deactivate_calls == ["admin@example.com"]
    assert captured["command"] == "deactivate-user"
    assert captured["action"] == "deactivated"
    assert captured["user"]["email"] == "admin@example.com"
    assert captured["user"]["is_active"] is False


def test_activate_user_delegates_to_service(monkeypatch, capsys) -> None:
    fake_service = FakeService()
    monkeypatch.setattr(admin_handler, "build_auth_service", lambda settings: fake_service)
    monkeypatch.setattr(admin_handler, "get_settings", lambda: SimpleNamespace())

    exit_code = admin_handler.main(["activate-user", "--email", "admin@example.com"])

    captured = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert fake_service.activate_calls == ["admin@example.com"]
    assert captured["command"] == "activate-user"
    assert captured["action"] == "activated"
    assert captured["user"]["email"] == "admin@example.com"
    assert captured["user"]["is_active"] is True
