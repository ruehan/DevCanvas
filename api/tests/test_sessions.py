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
    agent_msg, result = post_message(session, "고객 관리 페이지", DummyLLMAdapter())
    # 사용자 + 에이전트 메시지 2개
    assert len(session.messages) == 2
    assert session.messages[0].role == MessageRole.USER
    assert session.messages[0].content == "고객 관리 페이지"
    assert session.messages[1].role == MessageRole.AGENT
    # 첫 턴은 7단계 전체 파이프라인
    assert len(session.messages[1].steps) == 7
    # 결과 저장됨
    assert session.current_result is result
    assert result.requirement.features  # 파이프라인 결과 채워짐


def test_second_message_runs_edit_agent() -> None:
    store = SessionStore()
    session = store.create()
    post_message(session, "고객 관리 페이지", DummyLLMAdapter())

    agent_msg, result = post_message(session, "버튼을 더 둥글게", DummyLLMAdapter())
    # 메시지 4개(각 턴마다 user+agent)
    assert len(session.messages) == 4
    # 편집 턴 단계는 2개
    assert len(agent_msg.steps) == 2
    assert session.current_result is result
    # 더미는 fixture 반환이라 내용은 동일할 수 있으나, 호출 경로가 edit_agent 임을 단계로 확인
    assert agent_msg.steps == ["요청 분석", "결과 수정"]


def test_agent_message_summarizes_action() -> None:
    store = SessionStore()
    session = store.create()
    agent_msg, _ = post_message(session, "고객 관리 페이지", DummyLLMAdapter())
    assert agent_msg.content  # 요약 문구 채워짐
