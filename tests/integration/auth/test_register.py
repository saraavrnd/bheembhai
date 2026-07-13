from __future__ import annotations

import os
from uuid import uuid4

import httpx

from app.auth.repository import STANDARD_ROLE, SqlAlchemyUserRepository

BASE_DATABASE_URL = (
    "postgresql+psycopg://beembhai:beembhai@127.0.0.1:5432/beembhai"
)


def build_repository() -> SqlAlchemyUserRepository:
    database_url = os.getenv("TEST_DATABASE_URL", BASE_DATABASE_URL)
    repository = SqlAlchemyUserRepository.from_database_url(database_url)
    repository.ensure_schema()
    return repository


def test_register_endpoint_creates_user_and_returns_user_shape(deployed_api: str) -> None:
    email = f"visitor-{uuid4().hex[:8]}@example.com"
    repository = build_repository()

    response = httpx.post(
        f"{deployed_api}/api/v1/auth/register",
        json={
            "email": email.upper(),
            "password": "SignupPassword123!",
        },
        timeout=10.0,
    )

    stored = repository.find_by_email(email)
    assert response.status_code == 201
    assert stored is not None
    assert response.json() == {
        "id": stored.id,
        "email": email,
        "platformRole": "STANDARD",
        "emailVerifiedAt": None,
    }
    assert stored.password_hash != "SignupPassword123!"
    assert stored.platform_role == STANDARD_ROLE
    assert stored.email_verified_at is None


def test_register_endpoint_rejects_invalid_input(deployed_api: str) -> None:
    repository = build_repository()

    response = httpx.post(
        f"{deployed_api}/api/v1/auth/register",
        json={
            "email": "not-an-email",
            "password": "short",
        },
        timeout=10.0,
    )

    assert response.status_code == 422
    assert repository.find_by_email("not-an-email") is None


def test_register_endpoint_rejects_duplicate_email(deployed_api: str) -> None:
    email = f"visitor-{uuid4().hex[:8]}@example.com"
    repository = build_repository()

    first_response = httpx.post(
        f"{deployed_api}/api/v1/auth/register",
        json={
            "email": email,
            "password": "SignupPassword123!",
        },
        timeout=10.0,
    )
    duplicate_response = httpx.post(
        f"{deployed_api}/api/v1/auth/register",
        json={
            "email": email.upper(),
            "password": "SignupPassword123!",
        },
        timeout=10.0,
    )

    assert first_response.status_code == 201
    assert duplicate_response.status_code == 409
    assert duplicate_response.json()["detail"] == "email already exists"
    assert repository.find_by_email(email) is not None
