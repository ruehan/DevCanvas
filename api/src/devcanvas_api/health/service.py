"""헬스체크 비즈니스 로직."""

from __future__ import annotations

from datetime import UTC, datetime


def get_status() -> dict[str, str]:
    """애플리케이션 상태를 반환한다."""
    return {
        "status": "ok",
        "timestamp": datetime.now(UTC).isoformat(),
    }
