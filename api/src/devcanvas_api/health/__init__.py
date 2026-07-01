"""헬스체크 도메인 — 애플리케이션 생존 확인.

도메인 모듈 구조(CONVENTIONS.md)의 참고 예시:
router는 얇게, 비즈니스 로직은 service에 둔다.
"""

from devcanvas_api.health.router import router

__all__ = ["router"]
