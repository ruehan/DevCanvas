"""세션 엔드포인트 (ADR-0017)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from devcanvas_api.generations.dependencies import get_llm_adapter
from devcanvas_api.pipeline.llm import LLMAdapter
from devcanvas_api.sessions.dependencies import get_session_store
from devcanvas_api.sessions.schemas import (
    CreateSessionResponse,
    PostMessageRequest,
    PostMessageResponse,
    Session,
)
from devcanvas_api.sessions.service import post_message
from devcanvas_api.sessions.store import SessionStore

router = APIRouter(prefix="/sessions", tags=["sessions"])

_store_dep = Depends(get_session_store)
_llm_dep = Depends(get_llm_adapter)


@router.post("", response_model=CreateSessionResponse)
def create_session(store: SessionStore = _store_dep) -> CreateSessionResponse:
    """새 세션을 생성한다."""
    session = store.create()
    return CreateSessionResponse(id=session.id)


@router.get("/{session_id}", response_model=Session)
def get_session(session_id: str, store: SessionStore = _store_dep) -> Session:
    """세션 상태를 반환한다."""
    session = store.get(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="세션을 찾을 수 없습니다")
    return session


@router.post("/{session_id}/messages", response_model=PostMessageResponse)
def post_session_message(
    session_id: str,
    request: PostMessageRequest,
    store: SessionStore = _store_dep,
    llm: LLMAdapter = _llm_dep,
) -> PostMessageResponse:
    """사용자 메시지를 추가하고 처리(첫 턴=전체 파이프라인, 이후=편집)한다."""
    session = store.get(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="세션을 찾을 수 없습니다")
    agent_message, result = post_message(session, request.prompt, llm)
    return PostMessageResponse(
        agent_message=agent_message, result=result, session_id=session.id
    )
