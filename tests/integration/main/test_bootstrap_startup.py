from __future__ import annotations

from fastapi.testclient import TestClient

import app.main as app_main


def test_app_startup_serves_health_without_bootstrapping_admin() -> None:
    with TestClient(app_main.create_app()) as client:
        response = client.get("/health")

    assert response.status_code == 200
