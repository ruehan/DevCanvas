"""화면 종류별 레이아웃 템플릿 (ADR-0011).

layout: 공간 배치 설명(문자열).
component_tree: 렌더 순서 컴포넌트 목록(공간 배치와 대응).
"""

from __future__ import annotations

from devcanvas_api.pipeline.schemas import ScreenKind

_LAYOUTS: dict[ScreenKind, str] = {
    ScreenKind.LIST: "FilterBar(검색·필터) 상단 → DataTable 본문 → Pagination 하단",
    ScreenKind.DETAIL: "Header(제목·액션) 상단 → Tabs(이력·메모) 본문",
    ScreenKind.DASHBOARD: "KpiCard 행 상단 → Chart 중간 → RecentActivityTable 하단",
}

_COMPONENT_TREES: dict[ScreenKind, list[str]] = {
    ScreenKind.LIST: ["FilterBar", "DataTable", "Pagination"],
    ScreenKind.DETAIL: ["Header", "Tabs"],
    ScreenKind.DASHBOARD: ["KpiCard", "Chart", "RecentActivityTable"],
}


def layout(kind: ScreenKind) -> str:
    return _LAYOUTS[kind]


def component_tree(kind: ScreenKind) -> list[str]:
    return list(_COMPONENT_TREES[kind])
