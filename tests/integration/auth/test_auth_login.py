from __future__ import annotations

import os
from uuid import uuid4

import httpx

from app.auth.repository import SqlAlchemyUserRepository
from app.auth.tokens import AuthTokenService

BASE_DATABASE_URL = (
    "postgresql+psycopg://beembhai:beembhai@127.0.0.1:5432/beembhai"
)


def build_repository() -> SqlAlchemyUserRepository:
    database_url = os.getenv("TEST_DATABASE_URL", BASE_DATABASE_URL)
    repository = SqlAlchemyUserRepository.from_database_url(database_url)
    repository.ensure_schema()
    return repository


def test_login_endpoint_sets_session_and_me_returns_current_user(deployed_api: str) -> None:
    email = f"visitor-{uuid4().hex[:8]}@example.com"
    password = "LoginPassword123!"
    repository = build_repository()
    token_service = AuthTokenService("test-secret-key")

    register_response = httpx.post(
        f"{deployed_api}/api/v1/auth/register",
        json={"email": email, "password": password},
        timeout=10.0,
    )
    stored = repository.find_by_email(email)
    assert register_response.status_code == 201
    assert stored is not None

    verify_response = httpx.post(
        f"{deployed_api}/api/v1/auth/email/verify",
        json={
            "token": token_service.create_email_verification_token(
                user_id=stored.id,
                email=stored.email,
            )
        },
        timeout=10.0,
    )
    assert verify_response.status_code == 204
    verified_user = repository.find_by_email(email)
    assert verified_user is not None

    client = httpx.Client(base_url=deployed_api, timeout=10.0)
    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": email.upper(), "password": password},
    )
    me_response = client.get("/api/v1/me")
    logout_response = client.post("/api/v1/auth/logout")
    me_after_logout = client.get("/api/v1/me")

    assert login_response.status_code == 200
    assert login_response.json() == {
        "user": {
            "id": verified_user.id,
            "email": verified_user.email,
            "platformRole": "STANDARD",
            "emailVerifiedAt": verified_user.email_verified_at.isoformat().replace(
                "+00:00", "Z"
            ),
        }
    }
    assert me_response.status_code == 200
    assert me_response.json()["user"]["email"] == verified_user.email
    assert logout_response.status_code == 204
    assert me_after_logout.status_code == 401


def test_login_endpoint_rejects_unverified_user(deployed_api: str) -> None:
    email = f"visitor-{uuid4().hex[:8]}@example.com"
    password = "LoginPassword123!"
    response = httpx.post(
        f"{deployed_api}/api/v1/auth/register",
        json={"email": email, "password": password},
        timeout=10.0,
    )

    assert response.status_code == 201

    login_response = httpx.post(
        f"{deployed_api}/api/v1/auth/login",
        json={"email": email, "password": password},
        timeout=10.0,
    )

    assert login_response.status_code == 403
    assert login_response.json()["detail"] == "email address is not verified"


def test_password_reset_flow_updates_password_and_rejects_old_password(
    deployed_api: str,
) -> None:
    email = f"verified-{uuid4().hex[:8]}@example.com"
    password = "LoginPassword123!"
    new_password = "NewLoginPassword456!"
    repository = build_repository()
    token_service = AuthTokenService("test-secret-key")

    register_response = httpx.post(
        f"{deployed_api}/api/v1/auth/register",
        json={"email": email, "password": password},
        timeout=10.0,
    )
    assert register_response.status_code == 201
    stored = repository.find_by_email(email)
    assert stored is not None

    verify_response = httpx.post(
        f"{deployed_api}/api/v1/auth/email/verify",
        json={
            "token": token_service.create_email_verification_token(
                user_id=stored.id,
                email=stored.email,
            )
        },
        timeout=10.0,
    )
    assert verify_response.status_code == 204

    reset_request_response = httpx.post(
        f"{deployed_api}/api/v1/auth/password-reset/request",
        json={"email": email},
        timeout=10.0,
    )
    assert reset_request_response.status_code == 204

    reset_confirm_response = httpx.post(
        f"{deployed_api}/api/v1/auth/password-reset/confirm",
        json={
            "token": token_service.create_password_reset_token(
                user_id=stored.id,
                email=stored.email,
            ),
            "newPassword": new_password,
        },
        timeout=10.0,
    )
    assert reset_confirm_response.status_code == 204

    client = httpx.Client(base_url=deployed_api, timeout=10.0)
    old_password_login = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    new_password_login = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": new_password},
    )

    assert old_password_login.status_code == 401
    assert new_password_login.status_code == 200
