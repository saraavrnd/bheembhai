from __future__ import annotations

import pytest

from app.main import create_app


def pytest_configure(config):
    config.addinivalue_line("markers", "e2e: end-to-end browser-driven tests")


@pytest.fixture()
def app():
    return create_app()
