from __future__ import annotations

from uuid import uuid4

import pytest
from playwright.sync_api import Page

pytestmark = pytest.mark.e2e


def test_signup_page_renders(page: Page, running_server: str) -> None:
    page.goto(f"{running_server}/signup", wait_until="networkidle")

    assert page.get_by_role("heading", name="Sign up").is_visible()
    assert page.get_by_label("Email").is_visible()
    assert page.get_by_label("Password").is_visible()
    assert page.get_by_role("button", name="Create account").is_visible()


def test_signup_page_successfully_registers_a_new_user(page: Page, running_server: str) -> None:
    page.goto(f"{running_server}/signup", wait_until="networkidle")

    page.get_by_label("Email").fill(f"visitor-{uuid4().hex[:8]}@example.com")
    page.get_by_label("Password").fill("SignupPassword123!")
    page.get_by_role("button", name="Create account").click()

    assert page.get_by_role("heading", name="Check your email").is_visible()
    success_text = page.locator(".signup-success").text_content()
    assert success_text is not None
    assert "We created your account" in success_text
    assert "Check your inbox" in success_text
    assert "verify your email" in success_text
