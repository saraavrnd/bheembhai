from __future__ import annotations

import pytest
from playwright.sync_api import Page

pytestmark = pytest.mark.e2e

SCREENS = [
    ("/signup", "Create account", "Already have an account?"),
    ("/login", "Sign in", "Sign in to BheemBhai"),
    ("/forgot-password", "Forgot password", "Enter your account email"),
    ("/verify-email", "Verify your email", "We're verifying your email address"),
    ("/reset-password", "Reset password", "Choose a new password"),
]


def _assert_no_horizontal_scroll(page: Page) -> None:
    scroll_width = page.evaluate("document.documentElement.scrollWidth")
    client_width = page.evaluate("document.documentElement.clientWidth")
    assert scroll_width <= client_width + 1


@pytest.mark.parametrize("path, heading, marker", SCREENS)
def test_auth_mockup_pages_render(
    page: Page, running_server: str, path: str, heading: str, marker: str
) -> None:
    page.set_viewport_size({"width": 1440, "height": 1400})
    page.goto(f"{running_server}{path}", wait_until="networkidle")

    assert page.get_by_role("heading", name=heading).is_visible()
    assert page.get_by_text(marker).is_visible()


@pytest.mark.parametrize("path", [screen[0] for screen in SCREENS])
def test_auth_mockup_pages_stay_within_mobile_viewport(
    page: Page, running_server: str, path: str
) -> None:
    page.set_viewport_size({"width": 390, "height": 1200})
    page.goto(f"{running_server}{path}", wait_until="networkidle")

    _assert_no_horizontal_scroll(page)


def test_signup_page_hides_trust_footer(page: Page, running_server: str) -> None:
    page.set_viewport_size({"width": 1440, "height": 1400})
    page.goto(f"{running_server}/signup", wait_until="networkidle")

    assert page.get_by_text("Enterprise grade security").count() == 0
    assert page.get_by_text("Data privacy by design").count() == 0
    assert page.get_by_text("99.9% platform uptime").count() == 0


def test_login_page_shows_recovery_and_signup_links_not_contact_support(
    page: Page, running_server: str
) -> None:
    page.set_viewport_size({"width": 1440, "height": 1400})
    page.goto(f"{running_server}/login", wait_until="networkidle")

    assert page.get_by_role("link", name="Forgot password?").is_visible()
    assert page.get_by_role("link", name="Sign up").is_visible()
    assert page.get_by_role("link", name="Contact support").count() == 0


def test_verify_email_page_shows_missing_token_alert_without_fragment(
    page: Page, running_server: str
) -> None:
    page.set_viewport_size({"width": 1440, "height": 1400})
    page.goto(f"{running_server}/verify-email", wait_until="networkidle")

    assert page.locator("#verify-token-alert").is_visible()
    assert page.get_by_role("link", name="Go home").count() == 0
    assert page.get_by_role("button", name="Resend email").count() == 0


def test_reset_password_page_shows_missing_token_alert_without_fragment(
    page: Page, running_server: str
) -> None:
    page.set_viewport_size({"width": 1440, "height": 1400})
    page.goto(f"{running_server}/reset-password", wait_until="networkidle")

    assert page.locator("#reset-token-alert").is_visible()
    assert page.get_by_role("link", name="Go home").count() == 0
    assert page.get_by_text("Token loaded").count() == 0
    assert page.get_by_text("Password updated").count() == 0


def test_reset_password_page_shows_confirm_password_field_with_token(
    page: Page, running_server: str
) -> None:
    page.set_viewport_size({"width": 1440, "height": 1400})
    page.goto(f"{running_server}/reset-password#token=fake-token", wait_until="networkidle")

    assert page.locator("#reset-token-alert").is_hidden()
    assert page.get_by_label("New password", exact=True).is_visible()
    assert page.get_by_label("Confirm new password").is_visible()
    assert page.get_by_role("button", name="Update password").is_visible()
