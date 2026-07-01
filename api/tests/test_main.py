"""main 앱 팩토리 테스트."""

from __future__ import annotations

from fastapi.testclient import TestClient

from devcanvas_api.main import create_app


def test_health_endpoint() -> None:
    client = TestClient(create_app())
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
