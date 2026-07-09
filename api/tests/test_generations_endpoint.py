"""generations 엔드포인트 테스트."""

from __future__ import annotations

from fastapi.testclient import TestClient

from devcanvas_api.main import create_app
from devcanvas_api.pipeline.dependencies import get_llm_adapter
from devcanvas_api.pipeline.llm import DummyLLMAdapter


def test_post_generations_returns_full_result() -> None:
    app = create_app()
    app.dependency_overrides[get_llm_adapter] = lambda: DummyLLMAdapter()
    client = TestClient(app)

    response = client.post(
        "/generations",
        json={
            "prompt": "고객 관리 관리자 페이지",
            "screen_type": "admin",
            "data_fields": ["고객명", "결제 상태"],
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["input"]["prompt"] == "고객 관리 관리자 페이지"
    assert body["input"]["screen_type"] == "admin"
    assert body["requirement"]["features"]
    assert body["ux_plan"]["screens"]
    assert body["ux_plan"]["states"]
    assert body["design_system"]["tokens"]["colors"]
    assert body["ui"]["layouts"]
    assert body["code"]
    assert body["handoff"]["file_tree"]
