from __future__ import annotations

from fastapi.testclient import TestClient

import app.main as app_main


def test_app_startup_serves_health_without_bootstrapping_admin() -> None:
    build_calls = {"count": 0}
    sentinel = object()

    def fake_build_browser_auth_service(settings: object) -> object:
        build_calls["count"] += 1
        return sentinel

    original_builder = app_main.build_browser_auth_service
    app_main.build_browser_auth_service = fake_build_browser_auth_service
    try:
        app = app_main.create_app()
        with TestClient(app) as client:
            response = client.get("/health")
    finally:
        app_main.build_browser_auth_service = original_builder

    assert build_calls["count"] == 1
    assert app.state.browser_auth_service is sentinel
    assert response.status_code == 200
