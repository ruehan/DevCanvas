"""UX 플래너 규칙 기반 생성 테스트 (ADR-0010)."""

from __future__ import annotations

import pytest

from devcanvas_api.pipeline.schemas import (
    RequirementSpec,
    ScreenKind,
    ScreenState,
    ScreenType,
)
from devcanvas_api.pipeline.ux.planner import build_ux_plan


@pytest.fixture()
def sample_requirement() -> RequirementSpec:
    return RequirementSpec(
        features=["고객 목록 조회", "결제 상태 필터"],
        users=["관리자"],
        screens=["고객 목록"],
        data_entities=["Customer", "Contract"],
    )


# ---------- 화면 도출 ----------


def test_dashboard_screen_type_yields_dashboard_primary(
    sample_requirement: RequirementSpec,
) -> None:
    plan = build_ux_plan(sample_requirement, ScreenType.DASHBOARD)
    kinds = [s.kind for s in plan.screens]
    assert ScreenKind.DASHBOARD in kinds


def test_admin_screen_type_has_no_dashboard(sample_requirement: RequirementSpec) -> None:
    plan = build_ux_plan(sample_requirement, ScreenType.ADMIN)
    kinds = [s.kind for s in plan.screens]
    assert ScreenKind.DASHBOARD not in kinds
    # admin/internal_tool 은 list 가 주화면
    assert ScreenKind.LIST in kinds


def test_each_entity_produces_list_and_detail(
    sample_requirement: RequirementSpec,
) -> None:
    plan = build_ux_plan(sample_requirement, ScreenType.ADMIN)
    # 엔티티 2개 → list 2 + detail 2
    lists = [s for s in plan.screens if s.kind == ScreenKind.LIST]
    details = [s for s in plan.screens if s.kind == ScreenKind.DETAIL]
    assert len(lists) == 2
    assert len(details) == 2


def test_empty_requirement_still_produces_primary() -> None:
    plan = build_ux_plan(RequirementSpec(), ScreenType.DASHBOARD)
    # 엔티티가 없어도 대시보드 주화면 1개는 나온다
    assert plan.screens
    assert any(s.kind == ScreenKind.DASHBOARD for s in plan.screens)


# ---------- State Matrix 완결성 ----------


def test_state_matrix_covers_every_screen(
    sample_requirement: RequirementSpec,
) -> None:
    plan = build_ux_plan(sample_requirement, ScreenType.DASHBOARD)
    assert plan.states
    # 모든 화면에 상태 항목이 있어야 한다 (기획안 18.2)
    for screen in plan.screens:
        assert screen.name in plan.states
        state = plan.states[screen.name]
        assert isinstance(state, ScreenState)


@pytest.mark.parametrize(
    "field", ["loading", "empty", "error", "permission", "mobile"]
)
def test_every_state_has_all_five_fields(
    sample_requirement: RequirementSpec, field: str
) -> None:
    plan = build_ux_plan(sample_requirement, ScreenType.ADMIN)
    for state in plan.states.values():
        value = getattr(state, field)
        assert value and isinstance(value, str)


def test_state_content_differs_by_kind(sample_requirement: RequirementSpec) -> None:
    plan = build_ux_plan(sample_requirement, ScreenType.DASHBOARD)
    dashboard_state = next(
        plan.states[s.name] for s in plan.screens if s.kind == ScreenKind.DASHBOARD
    )
    list_state = next(
        plan.states[s.name] for s in plan.screens if s.kind == ScreenKind.LIST
    )
    # 종류가 다르면 상태 내용도 다르다
    assert dashboard_state.loading != list_state.loading
    assert dashboard_state.empty != list_state.empty


# ---------- flows ----------


def test_flows_connect_primary_to_entity_detail(
    sample_requirement: RequirementSpec,
) -> None:
    plan = build_ux_plan(sample_requirement, ScreenType.ADMIN)
    assert plan.flows
    # 최소 한 흐름은 존재
    assert isinstance(plan.flows[0], str)


def test_flows_cover_every_entity(sample_requirement: RequirementSpec) -> None:
    # 다중 엔티티에서 각 엔티티의 흐름이 모두 포함되어야 한다 (리뷰 P2-1)
    plan = build_ux_plan(sample_requirement, ScreenType.ADMIN)
    joined = " | ".join(plan.flows)
    assert "고객" in joined
    assert "계약" in joined  # 두 번째 엔티티도 흐름에 등장
    assert len(plan.flows) == 2  # 엔티티 2개 → 흐름 2개


def test_dashboard_flow_prefixes_dashboard(sample_requirement: RequirementSpec) -> None:
    plan = build_ux_plan(sample_requirement, ScreenType.DASHBOARD)
    assert plan.flows[0].startswith("대시보드 →")


# ---------- 폴백 / 엣지 ----------


def test_admin_empty_requirement_falls_back_to_single_list() -> None:
    # ADMIN + 엔티티 없음 → 폴백 "목록" 단일 화면 (리뷰 P2-3)
    plan = build_ux_plan(RequirementSpec(), ScreenType.ADMIN)
    assert len(plan.screens) == 1
    assert plan.screens[0].kind == ScreenKind.LIST
    assert plan.screens[0].name in plan.states
    assert plan.flows == ["목록"]


def test_internal_tool_treated_as_list_no_dashboard(
    sample_requirement: RequirementSpec,
) -> None:
    # INTERNAL_TOOL 은 대시보드 없이 list 주화면 (ADR-0002 / ADR-0010)
    plan = build_ux_plan(sample_requirement, ScreenType.INTERNAL_TOOL)
    kinds = [s.kind for s in plan.screens]
    assert ScreenKind.DASHBOARD not in kinds
    assert ScreenKind.LIST in kinds


def test_unknown_entity_label_passes_through() -> None:
    # _entity_label 매핑 미지정 엔티티는 이름 그대로 (리뷰 P2-3)
    req = RequirementSpec(data_entities=["Product"])
    plan = build_ux_plan(req, ScreenType.ADMIN)
    names = [s.name for s in plan.screens]
    assert "Product 목록" in names
    assert "Product 상세" in names
