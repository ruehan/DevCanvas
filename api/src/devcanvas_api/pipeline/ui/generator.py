"""UI 생성기 — UXPlan 에서 화면별 ScreenLayout 규칙 기반 도출 (ADR-0011)."""

from __future__ import annotations

from devcanvas_api.pipeline.schemas import ScreenLayout, UIGeneration, UXPlan
from devcanvas_api.pipeline.ui import templates


def build_ui_generation(ux_plan: UXPlan) -> UIGeneration:
    """UXPlan 의 각 화면에서 종류별 ScreenLayout(배치 + 렌더 순서)을 도출한다."""
    layouts = [
        ScreenLayout(
            screen=screen.name,
            layout=templates.layout(screen.kind),
            component_tree=templates.component_tree(screen.kind),
        )
        for screen in ux_plan.screens
    ]
    return UIGeneration(layouts=layouts)
