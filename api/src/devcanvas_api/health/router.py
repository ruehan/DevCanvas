"""헬스체크 엔드포인트."""

from __future__ import annotations

from fastapi import APIRouter

from devcanvas_api.health.service import get_status

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict[str, str]:
    """헬스체크 엔드포인트."""
    return get_status()
