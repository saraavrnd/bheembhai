from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

import pytest
from argon2 import PasswordHasher
from playwright.sync_api import Page

from app.auth.repository import STANDARD_ROLE, SqlAlchemyUserRepository

pytestmark = pytest.mark.e2e

BASE_DATABASE_URL = (
    "postgresql+psycopg://beembhai:beembhai@127.0.0.1:5432/beembhai"
)


def build_repository() -> SqlAlchemyUserRepository:
    import os

    database_url = os.getenv("TEST_DATABASE_URL", BASE_DATABASE_URL)
    repository = SqlAlchemyUserRepository.from_database_url(database_url)
    repository.ensure_schema()
    return repository


def test_login_page_renders(page: Page, running_server: str) -> None:
    page.goto(f"{running_server}/login", wait_until="networkidle")

    assert page.get_by_role("heading", name="Sign in").is_visible()
    assert page.get_by_label("Email").is_visible()
    assert page.get_by_role("textbox", name="Password", exact=True).is_visible()
    assert page.get_by_role("button", name="Sign in").is_visible()


def test_login_page_signs_verified_user_in(page: Page, running_server: str) -> None:
    email = f"visitor-{uuid4().hex[:8]}@example.com"
    password = "LoginPassword123!"
    repository = build_repository()
    repository.create_user(
        email=email,
        password_hash=PasswordHasher().hash(password),
        platform_role=STANDARD_ROLE,
        email_verified_at=datetime.now(UTC),
    )

    page.goto(f"{running_server}/login", wait_until="networkidle")
    page.get_by_label("Email").fill(email)
    page.get_by_role("textbox", name="Password", exact=True).fill(password)
    page.get_by_role("button", name="Sign in").click()

    assert page.get_by_role("heading", name="Signed in").is_visible()
    cookies = page.context.cookies()
    assert any(cookie["name"] == "bb_session" for cookie in cookies)
