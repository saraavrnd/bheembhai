import pytest
from playwright.sync_api import Page

pytestmark = pytest.mark.e2e


def test_home_page_renders(page: Page, running_server: str) -> None:
    page.goto(running_server, wait_until="networkidle")

    assert page.locator("h1").text_content().strip() == "BeemBhai"
    assert page.get_by_role("link", name="Health check").get_attribute("href") == "/api/v1/health"
    assert page.get_by_role("link", name="API docs").get_attribute("href") == "/api/v1/docs"
