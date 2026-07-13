from __future__ import annotations

import httpx


def test_health_endpoint_returns_ok(deployed_api: str) -> None:
    response = httpx.get(f"{deployed_api}/health", timeout=10.0)
    versioned_response = httpx.get(f"{deployed_api}/api/v1/health", timeout=10.0)

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    assert versioned_response.status_code == 200
    assert versioned_response.json() == {"status": "ok"}
