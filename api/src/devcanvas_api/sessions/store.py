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

    def save(self, session: Session) -> None:
        """세션을 영속화한다. 인메모리 구현은 no-op(같은 참조를 쓰므로).
        Postgres 구현은 여기서 직렬화/기록한다 — service 는 이 호출점으로 영속성에 무지.
        """
        # 인메모리: get()이 같은 참조를 반환하므로 이미 반영됨. 명시적 호출점만 유지.
        self._sessions[session.id] = session
