"""세션 엔드포인트 테스트 (ADR-0017)."""

from __future__ import annotations

from fastapi.testclient import TestClient

from devcanvas_api.generations.dependencies import get_llm_adapter
from devcanvas_api.main import create_app
from devcanvas_api.pipeline.llm import DummyLLMAdapter
from devcanvas_api.sessions.dependencies import get_session_store
from devcanvas_api.sessions.store import SessionStore


def _client() -> TestClient:
    app = create_app()
    # 격리된 동일 스토어 인스턴스 + 더미 LLM 주입
    store = SessionStore()
    app.dependency_overrides[get_session_store] = lambda: store
    app.dependency_overrides[get_llm_adapter] = lambda: DummyLLMAdapter()
    return TestClient(app)


def test_create_and_get_session() -> None:
    client = _client()
    created = client.post("/sessions")
    assert created.status_code == 200
    sid = created.json()["id"]

    got = client.get(f"/sessions/{sid}")
    assert got.status_code == 200
    assert got.json()["id"] == sid


def test_first_message_returns_full_result() -> None:
    client = _client()
    sid = client.post("/sessions").json()["id"]

    resp = client.post(f"/sessions/{sid}/messages", json={"prompt": "고객 관리 페이지"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["result"]["requirement"]["features"]  # 파이프라인 결과
    assert len(body["agent_message"]["steps"]) == 7  # 전체 파이프라인


def test_second_message_runs_edit() -> None:
    client = _client()
    sid = client.post("/sessions").json()["id"]
    client.post(f"/sessions/{sid}/messages", json={"prompt": "고객 관리 페이지"})

    resp = client.post(f"/sessions/{sid}/messages", json={"prompt": "버튼 더 둥글게"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["agent_message"]["steps"] == ["요청 분석", "결과 수정"]


def test_missing_session_404() -> None:
    client = _client()
    resp = client.post("/sessions/nope/messages", json={"prompt": "x"})
    assert resp.status_code == 404
