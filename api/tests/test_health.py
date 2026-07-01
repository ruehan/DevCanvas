"""헬스체크 도메인 테스트."""

from __future__ import annotations

from devcanvas_api.health.service import get_status


def test_get_status_returns_ok() -> None:
    result = get_status()
    assert result["status"] == "ok"
    assert "timestamp" in result


def test_get_status_timestamp_is_iso() -> None:
    result = get_status()
    # ISO 8601 형식 기본 접두사 검증
    assert result["timestamp"][0:4].isdigit()
