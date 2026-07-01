"""화면 종류별 템플릿 (ADR-0010).

list/detail/dashboard 종류의 컴포넌트·데이터컬럼·필터·액션·상태 템플릿.
엔티티 이름으로 매개변수화해 구체적인 상태 내용을 만든다.
"""

from __future__ import annotations

from devcanvas_api.pipeline.schemas import ScreenKind, ScreenState

# 종류별 기본 컴포넌트
_COMPONENTS: dict[ScreenKind, list[str]] = {
    ScreenKind.LIST: [
        "DataTable",
        "SearchInput",
        "FilterBar",
        "Pagination",
        "StatusBadge",
    ],
    ScreenKind.DETAIL: [
        "Card",
        "Tabs",
        "Descriptions",
        "EmptyState",
        "ActionButton",
    ],
    ScreenKind.DASHBOARD: [
        "KpiCard",
        "Chart",
        "RecentActivityTable",
        "FilterBar",
    ],
}

_GENERIC_COLUMNS: dict[ScreenKind, list[str]] = {
    ScreenKind.LIST: ["이름", "상태", "생성일", "수정일"],
    ScreenKind.DETAIL: ["항목", "값", "수정일"],
    ScreenKind.DASHBOARD: ["지표", "값", "추세"],
}

_FILTERS: dict[ScreenKind, list[str]] = {
    ScreenKind.LIST: ["상태", "기간", "검색"],
    ScreenKind.DETAIL: [],
    ScreenKind.DASHBOARD: ["기간"],
}


def components(kind: ScreenKind) -> list[str]:
    return list(_COMPONENTS[kind])


def data_columns(kind: ScreenKind) -> list[str]:
    return list(_GENERIC_COLUMNS[kind])


def filters(kind: ScreenKind) -> list[str]:
    return list(_FILTERS[kind])


def actions(kind: ScreenKind, entity: str) -> list[str]:
    if kind == ScreenKind.LIST:
        return [f"{entity} 상세 보기", "내보내기"]
    if kind == ScreenKind.DETAIL:
        return ["편집", "삭제"]
    return ["필터 적용", "내보내기"]  # dashboard


def state(kind: ScreenKind, entity: str) -> ScreenState:
    """종류·엔티티별 State Matrix 항목."""
    if kind == ScreenKind.LIST:
        return ScreenState(
            loading=f"{entity} 테이블 skeleton",
            empty=f"{entity} 데이터가 없습니다. 첫 {entity}를 등록하세요.",
            error=f"{entity} 목록 로드 실패. 재시도 버튼 + 오류 메시지.",
            permission=f"{entity} 조회 권한이 필요합니다.",
            mobile=f"{entity} 테이블을 카드형 리스트로 전환",
        )
    if kind == ScreenKind.DETAIL:
        return ScreenState(
            loading=f"{entity} 상세 skeleton",
            empty=f"{entity}를 선택하세요.",
            error=f"{entity} 상세 로드 실패. 재시도.",
            permission=f"{entity} 상세 조회 권한이 필요합니다.",
            mobile=f"{entity} 상세를 단일 컬럼 스택으로 전환",
        )
    # dashboard
    return ScreenState(
        loading="KPI/차트 skeleton",
        empty="지표 데이터가 연결되지 않았습니다.",
        error="지표 로드 실패. 재시도.",
        permission="대시보드 접근 권한이 필요합니다.",
        mobile="KPI 카드를 세로 스택으로 전환",
    )
