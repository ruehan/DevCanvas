"""세션 도메인 테스트 (ADR-0017)."""

from __future__ import annotations

from devcanvas_api.pipeline.llm import DummyLLMAdapter
from devcanvas_api.sessions.schemas import MessageRole
from devcanvas_api.sessions.service import post_message
from devcanvas_api.sessions.store import SessionStore


def test_store_create_and_get() -> None:
    store = SessionStore()
    session = store.create()
    assert session.id
    fetched = store.get(session.id)
    assert fetched is session
    assert store.get("nope") is None


def test_first_message_runs_full_pipeline() -> None:
    store = SessionStore()
    session = store.create()
    agent_msg, result = post_message(session, "고객 관리 페이지", DummyLLMAdapter(), store)
    assert len(session.messages) == 2
    assert session.messages[0].role == MessageRole.USER
    assert session.messages[1].role == MessageRole.AGENT
    assert len(session.messages[1].steps) == 7  # 전체 파이프라인
    assert session.current_result is result
    assert result.requirement.features


def test_second_message_runs_edit() -> None:
    store = SessionStore()
    session = store.create()
    post_message(session, "고객 관리 페이지", DummyLLMAdapter(), store)

    agent_msg, result = post_message(session, "버튼을 더 둥글게", DummyLLMAdapter(), store)
    assert len(session.messages) == 4
    # 편집 턴은 단일 LLM 호출 → 1단계(리뷰 P3-2)
    assert agent_msg.steps == ["결과 수정"]
    assert session.current_result is result


def test_agent_message_summarizes_action() -> None:
    store = SessionStore()
    session = store.create()
    agent_msg, _ = post_message(session, "고객 관리 페이지", DummyLLMAdapter(), store)
    assert agent_msg.content


def test_post_message_persists_via_store() -> None:
    # store.save 호출 검증 — spy 로 확인
    store = SessionStore()
    session = store.create()
    saved: list[str] = []
    original_save = store.save

    def spy_save(s: object) -> None:
        saved.append(getattr(s, "id", ""))
        original_save(s)  # type: ignore[arg-type]

    store.save = spy_save  # type: ignore[method-assign,assignment]
    post_message(session, "고객 관리 페이지", DummyLLMAdapter(), store)
    assert saved == [session.id]
