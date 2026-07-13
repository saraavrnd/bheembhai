from __future__ import annotations

import os
from tempfile import mkdtemp

import pytest

_TEST_DB_DIR = mkdtemp(prefix="beembhai-tests-")
os.environ.setdefault("DATABASE_URL", f"sqlite+pysqlite:///{_TEST_DB_DIR}/beembhai.db")
os.environ.setdefault("BEEBHAI_SECRET_KEY", "test-secret-key")
os.environ.setdefault("BREVO_API_KEY", "test-brevo-key")
os.environ.setdefault("BREVO_SENDER_EMAIL", "no-reply@example.com")
os.environ.setdefault("BREVO_SENDER_NAME", "BeemBhai")


def pytest_configure(config):
    config.addinivalue_line("markers", "e2e: end-to-end browser-driven tests")


@pytest.fixture()
def app():
    from app.main import create_app

    return create_app()
