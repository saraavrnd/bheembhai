from __future__ import annotations

from pathlib import Path

import pytest
from playwright.sync_api import Page

pytestmark = pytest.mark.e2e

SNAPSHOT_DIR = Path(__file__).parent / "__snapshots__" / "auth"

SCREENS = ["signup", "login", "forgot-password", "reset-password", "verify-email"]
VIEWPORTS = {
    "desktop": {"width": 1440, "height": 900},
    "mobile": {"width": 390, "height": 844},
}

MAX_DIFF_RATIO = 0.02


def _baseline_path(screen: str, viewport_name: str) -> Path:
    return SNAPSHOT_DIR / f"{screen}-{viewport_name}.png"


def _diff_ratio(baseline_bytes: bytes, actual_bytes: bytes) -> float:
    from io import BytesIO

    from PIL import Image

    baseline = Image.open(BytesIO(baseline_bytes)).convert("RGB")
    actual = Image.open(BytesIO(actual_bytes)).convert("RGB")

    if baseline.size != actual.size:
        actual = actual.resize(baseline.size)

    width, height = baseline.size
    baseline_pixels = baseline.load()
    actual_pixels = actual.load()

    total = width * height
    differing = 0
    threshold = 24  # per-channel tolerance for anti-aliasing noise
    for y in range(height):
        for x in range(width):
            br, bg, bb = baseline_pixels[x, y]
            ar, ag, ab = actual_pixels[x, y]
            if abs(br - ar) > threshold or abs(bg - ag) > threshold or abs(bb - ab) > threshold:
                differing += 1

    return differing / total


@pytest.mark.parametrize("screen", SCREENS)
@pytest.mark.parametrize("viewport_name", list(VIEWPORTS))
def test_auth_screen_matches_approved_visual_baseline(
    page: Page, running_server: str, screen: str, viewport_name: str
) -> None:
    baseline_file = _baseline_path(screen, viewport_name)
    if not baseline_file.exists():
        relative_baseline = baseline_file.relative_to(Path(__file__).parent.parent.parent)
        pytest.fail(
            f"No approved visual baseline at {relative_baseline} yet. "
            "This is expected until `implement` renders the rebuilt screen, a human visually "
            "confirms it matches the approved mockup, and the baseline screenshot is captured "
            "(see story-design.md's screenshot-baseline workflow). Do not fabricate a baseline "
            "to make this pass."
        )

    viewport = VIEWPORTS[viewport_name]
    page.set_viewport_size(viewport)
    page.goto(f"{running_server}/{screen}", wait_until="networkidle")
    actual_bytes = page.screenshot(full_page=True)

    diff_ratio = _diff_ratio(baseline_file.read_bytes(), actual_bytes)
    assert diff_ratio <= MAX_DIFF_RATIO, (
        f"{screen} ({viewport_name}) visually drifted from its approved baseline: "
        f"{diff_ratio:.2%} of pixels differ (tolerance {MAX_DIFF_RATIO:.0%})"
    )
