from __future__ import annotations

import pytest
from playwright.sync_api import Page

pytestmark = pytest.mark.e2e

AUTH_PATHS = ["/signup", "/login", "/forgot-password", "/reset-password", "/verify-email"]

# /verify-email's pending state (no token in the URL) intentionally renders no primary-action
# button -- it's a silent auto-verify page with only a hidden form / missing-token alert, by
# design (BEEM-20 item 18 removed the "Resend email" button). Exclude it from the
# primary-button-color check, which needs a visible .btn-primary to sample.
AUTH_PATHS_WITH_PRIMARY_BUTTON = [path for path in AUTH_PATHS if path != "/verify-email"]


def _resolve_css_custom_property_as_color(page: Page, property_name: str) -> str:
    return page.evaluate(
        """(propertyName) => {
            const raw = getComputedStyle(document.documentElement)
                .getPropertyValue(propertyName)
                .trim();
            if (!raw) return "";
            const probe = document.createElement("div");
            probe.style.color = raw;
            document.body.appendChild(probe);
            const resolved = getComputedStyle(probe).color;
            probe.remove();
            return resolved;
        }""",
        property_name,
    )


@pytest.mark.parametrize("path", AUTH_PATHS)
def test_auth_pages_load_real_bootstrap_container_breakpoints(
    page: Page, running_server: str, path: str
) -> None:
    """Bootstrap 5's .container resolves a fixed max-width per breakpoint; the bespoke
    theme.css `.container` rule used `width: min(...)` instead, so this only passes once
    the real Bootstrap stylesheet is actually loaded."""
    page.set_viewport_size({"width": 1440, "height": 900})
    page.goto(f"{running_server}{path}", wait_until="networkidle")

    max_width = page.evaluate(
        """() => {
            const el = document.querySelector('.container');
            if (!el) return null;
            return getComputedStyle(el).maxWidth;
        }"""
    )

    assert max_width == "1320px", (
        f"expected Bootstrap's >=1400px .container max-width (1320px) on {path}, "
        f"got {max_width!r} -- real Bootstrap does not appear to be loaded"
    )


@pytest.mark.parametrize("path", AUTH_PATHS_WITH_PRIMARY_BUTTON)
def test_auth_primary_button_color_matches_bb_primary_token(
    page: Page, running_server: str, path: str
) -> None:
    """docs/ui-conventions.md's Color Roles table names the primary-action token
    `--bb-primary`; theme.css currently only defines `--bb-accent`, so this fails until
    the token is introduced (or renamed) and the primary button is wired to it."""
    page.goto(f"{running_server}{path}", wait_until="networkidle")

    token_color = _resolve_css_custom_property_as_color(page, "--bb-primary")
    assert token_color, "--bb-primary is not defined on :root"

    button = page.locator(".btn-primary").first
    assert button.count() > 0, f"no .btn-primary primary action button found on {path}"
    button_color = button.evaluate("(el) => getComputedStyle(el).backgroundColor")

    assert button_color == token_color, (
        f"primary button background-color ({button_color}) does not resolve to the "
        f"--bb-primary token ({token_color}) on {path}"
    )


def test_login_password_toggle_uses_feather_icon_sprite(page: Page, running_server: str) -> None:
    """ui-conventions.md calls for standardizing on one real icon set from the shell.
    The current toggle renders an emoji glyph (◔); this checks for a feather-icons
    <svg><use> reference instead."""
    page.goto(f"{running_server}/login", wait_until="networkidle")

    toggle_icon = page.locator(
        "button[aria-label='Show password'] svg use[href*='feather-sprite.svg']"
    )
    assert toggle_icon.count() > 0, (
        "password-visibility toggle does not reference the feather-icons sprite"
    )
