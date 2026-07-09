"""인메모리 세션 스토어 (ADR-0017)."""

from __future__ import annotations

from devcanvas_api.sessions.schemas import Session


class SessionStore:
    """프로세스 내 세션 저장. Postgres 이관 시 구현만 교체(인터페이스 유지)."""

    def __init__(self) -> None:
        self._sessions: dict[str, Session] = {}

    def create(self) -> Session:
        session = Session()
        self._sessions[session.id] = session
        return session

    def get(self, session_id: str) -> Session | None:
        return self._sessions.get(session_id)
