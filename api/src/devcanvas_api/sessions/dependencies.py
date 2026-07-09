"""세션 의존성."""

from __future__ import annotations

from functools import lru_cache

from devcanvas_api.sessions.store import SessionStore


@lru_cache
def get_session_store() -> SessionStore:
    """인메모리 세션 스토어 싱글턴(ADR-0017)."""
    return SessionStore()
