"""main 앱 팩토리 테스트."""

from __future__ import annotations

from fastapi.testclient import TestClient

from devcanvas_api.main import create_app


def test_health_endpoint() -> None:
    client = TestClient(create_app())
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_cors_allows_dev_origin() -> None:
    """CORS 미들웨어가 프론트(dev) origin 을 허용한다 (ADR-0014)."""
    client = TestClient(create_app())
    response = client.options(
        "/generations",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST",
        },
    )
    # preflight 성공 + CORS 헤더 노출
    assert response.status_code in (200, 204)
    allow_origin = response.headers.get("access-control-allow-origin")
    assert allow_origin is not None
    assert allow_origin in ("*", "http://localhost:3000")
