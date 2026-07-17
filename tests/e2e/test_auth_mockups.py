from __future__ import annotations

import pytest
from playwright.sync_api import Page

pytestmark = pytest.mark.e2e

SCREENS = [
    ("/signup", "Create account", "Already have an account?"),
    ("/login", "Sign in", "Verify your email before signing in"),
    ("/verify-email", "Verify your email", "Verification link flow"),
    ("/reset-password", "Reset password", "Token loaded"),
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


def test_signup_page_shows_trust_footer(page: Page, running_server: str) -> None:
    page.set_viewport_size({"width": 1440, "height": 1400})
    page.goto(f"{running_server}/signup", wait_until="networkidle")

    assert page.get_by_text("Enterprise grade security").is_visible()
    assert page.get_by_text("Data privacy by design").is_visible()
    assert page.get_by_text("99.9% platform uptime").is_visible()


def test_login_page_shows_support_and_recovery_links(page: Page, running_server: str) -> None:
    page.set_viewport_size({"width": 1440, "height": 1400})
    page.goto(f"{running_server}/login", wait_until="networkidle")

    assert page.get_by_role("link", name="Forgot password?").is_visible()
    assert page.get_by_role("link", name="Contact support").is_visible()


def test_verify_email_page_shows_primary_and_secondary_actions(
    page: Page, running_server: str
) -> None:
    page.set_viewport_size({"width": 1440, "height": 1400})
    page.goto(f"{running_server}/verify-email", wait_until="networkidle")

    assert page.get_by_role("link", name="Go home").is_visible()
    assert page.get_by_role("button", name="Resend email").is_visible()


def test_reset_password_page_shows_both_status_panels_together(
    page: Page, running_server: str
) -> None:
    page.set_viewport_size({"width": 1440, "height": 1400})
    page.goto(f"{running_server}/reset-password", wait_until="networkidle")

    assert page.get_by_role("button", name="Update password").is_visible()
    assert page.get_by_role("link", name="Go home").is_visible()
    assert page.get_by_text("Token loaded").is_visible()
    assert page.get_by_text("Password updated").is_visible()
