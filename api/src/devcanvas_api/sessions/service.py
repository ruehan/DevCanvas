"""세션 비즈니스 로직 (ADR-0017/0018)."""

from __future__ import annotations

from devcanvas_api.pipeline.edit_agent import EDIT_STEPS, apply_edit
from devcanvas_api.pipeline.llm import LLMAdapter
from devcanvas_api.pipeline.orchestrator import run_pipeline
from devcanvas_api.pipeline.schemas import GenerationInput, GenerationResult
from devcanvas_api.sessions.schemas import Message, MessageRole, Session
from devcanvas_api.sessions.store import SessionStore

# 첫 턴(전체 파이프라인)의 에이전트 단계
PIPELINE_STEPS = [
    "요구사항 분석",
    "UX 설계",
    "디자인 시스템",
    "UI 생성",
    "코드 생성",
    "리뷰",
    "핸드오프",
]


def post_message(
    session: Session, prompt: str, llm: LLMAdapter, store: SessionStore
) -> tuple[Message, GenerationResult]:
    """사용자 메시지를 추가하고 처리(첫 턴=전체 파이프라인, 이후=편집)한다.

    변이 후 store.save 로 명시적 영속화(Postgres 이관 시 실 기록).
    """
    session.messages.append(Message(role=MessageRole.USER, content=prompt))

    if session.current_result is None:
        result = run_pipeline(GenerationInput(prompt=prompt), llm)
        steps = PIPELINE_STEPS
        summary = "전체 화면·상태·토큰·코드를 생성했어요."
    else:
        result = apply_edit(session.current_result, prompt, llm)
        steps = EDIT_STEPS
        summary = f"요청을 반영해 결과를 수정했어요: {prompt}"

    session.current_result = result
    agent_message = Message(role=MessageRole.AGENT, content=summary, steps=steps)
    session.messages.append(agent_message)
    store.save(session)
    return agent_message, result
