"""UI 생성기 규칙 기반 테스트 (ADR-0011)."""

from __future__ import annotations

import pytest

from devcanvas_api.pipeline.schemas import (
    RequirementSpec,
    ScreenKind,
    ScreenType,
    UXPlan,
)
from devcanvas_api.pipeline.ui.generator import build_ui_generation
from devcanvas_api.pipeline.ux.planner import build_ux_plan


@pytest.fixture()
def dashboard_plan() -> UXPlan:
    req = RequirementSpec(data_entities=["Customer", "Contract"])
    return build_ux_plan(req, ScreenType.DASHBOARD)


def test_one_layout_per_screen(dashboard_plan: UXPlan) -> None:
    gen = build_ui_generation(dashboard_plan)
    assert len(gen.layouts) == len(dashboard_plan.screens)
    # 화면 이름이 ux_plan 의 화면과 일치
    layout_screens = {lay.screen for lay in gen.layouts}
    plan_screens = {s.name for s in dashboard_plan.screens}
    assert layout_screens == plan_screens


def test_layouts_non_empty(dashboard_plan: UXPlan) -> None:
    gen = build_ui_generation(dashboard_plan)
    for layout in gen.layouts:
        assert layout.layout  # 공간 배치 설명 채워짐
        assert layout.component_tree  # 렌더 순서 컴포넌트 채워짐


def test_layout_differs_by_kind(dashboard_plan: UXPlan) -> None:
    gen = build_ui_generation(dashboard_plan)
    by_screen = {lay.screen: lay for lay in gen.layouts}
    # dashboard plan: 대시보드 + 고객(list/detail) + 계약(list/detail)
    dash = next(
        s for s in dashboard_plan.screens if s.kind == ScreenKind.DASHBOARD
    )
    list_screen = next(
        s for s in dashboard_plan.screens if s.kind == ScreenKind.LIST
    )
    assert by_screen[dash.name].layout != by_screen[list_screen.name].layout


@pytest.mark.parametrize("kind", list(ScreenKind))
def test_each_kind_has_layout_template(kind: ScreenKind) -> None:
    from devcanvas_api.pipeline.ui import templates as t

    assert t.layout(kind)
    assert len(t.component_tree(kind)) >= 1


@pytest.mark.parametrize("kind", list(ScreenKind))
def test_component_tree_subset_of_screen_components(kind: ScreenKind) -> None:
    # component_tree 는 상위 screen.components 의 부분집합이어야 한다 (리뷰 P1)
    from devcanvas_api.pipeline.ui import templates as ui_templates
    from devcanvas_api.pipeline.ux import templates as ux_templates

    tree = set(ui_templates.component_tree(kind))
    components = set(ux_templates.components(kind))
    assert tree <= components


def test_empty_plan_yields_empty_generation() -> None:
    gen = build_ui_generation(UXPlan())
    assert gen.layouts == []
