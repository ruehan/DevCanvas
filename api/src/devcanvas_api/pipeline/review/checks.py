"""리뷰 체크 — 생성 코드에 대한 결정적 린트 (ADR-0013).

각 체크는 CodeFile 목록을 순회하며 패턴 매칭으로 ReviewFinding 을 생산한다.
체크는 독립적이고 부작용 없음.
"""

from __future__ import annotations

from devcanvas_api.pipeline.schemas import CodeFile, ReviewFinding, ReviewSeverity

_P1 = ReviewSeverity.P1
_P2 = ReviewSeverity.P2


def _is_page(f: CodeFile) -> bool:
    return f.path.endswith("page.tsx")


def check_state(f: CodeFile) -> list[ReviewFinding]:
    """상태 분기 누락 — page 에 상태(loading/empty/error) 키워드가 아예 없거나 TODO 로 남아있음."""
    if not _is_page(f):
        return []
    content = f.content
    has_state_keyword = any(k in content for k in ("loading", "empty", "error"))
    has_todo_state = "TODO" in content and "상태" in content
    if not has_state_keyword:
        return [
            ReviewFinding(
                severity=_P1,
                category="state",
                message=f"{f.path}: 상태(loading/empty/error) 분기가 전혀 없음 (State Matrix 누락)",
            )
        ]
    if has_todo_state:
        return [
            ReviewFinding(
                severity=_P1,
                category="state",
                message=f"{f.path}: 상태 분기가 TODO 로 남아있음 — 구현 필요 (State Matrix)",
            )
        ]
    return []


def check_a11y(f: CodeFile) -> list[ReviewFinding]:
    """접근성 — page 에 aria-* 속성 없음."""
    if not _is_page(f):
        return []
    if "aria-" not in f.content:
        return [
            ReviewFinding(
                severity=_P2,
                category="a11y",
                message=f"{f.path}: aria-* 속성 없음 — 접근성 라벨 권장",
            )
        ]
    return []


def check_component_stubs(f: CodeFile) -> list[ReviewFinding]:
    """컴포넌트 미구현 — 컴포넌트 스텁에 TODO."""
    if not f.path.startswith("components/"):
        return []
    if "TODO" in f.content:
        return [
            ReviewFinding(
                severity=_P2,
                category="component",
                message=f"{f.path}: 컴포넌트 본체 미구현(TODO) — shadcn/ui 구현 필요",
            )
        ]
    return []


def check_mock_usage(f: CodeFile) -> list[ReviewFinding]:
    """mock 데이터 사용 — page 가 @/lib/mock-data import (실제 API 교체 필요)."""
    if not _is_page(f):
        return []
    if "@/lib/mock-data" in f.content:
        return [
            ReviewFinding(
                severity=_P2,
                category="data",
                message=f"{f.path}: mock 데이터 사용 중 — 실제 API 로 교체 필요",
            )
        ]
    return []


def check_any_type(f: CodeFile) -> list[ReviewFinding]:
    """any 타입 사용."""
    if ": any" in f.content:
        return [
            ReviewFinding(
                severity=_P1,
                category="types",
                message=f"{f.path}: any 타입 사용 — 구체적 타입 권장",
            )
        ]
    return []


CHECKS = (
    check_state,
    check_a11y,
    check_component_stubs,
    check_mock_usage,
    check_any_type,
)
