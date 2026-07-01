"""UX 플래너 — RequirementSpec 에서 화면·State Matrix 규칙 기반 도출 (ADR-0010)."""

from __future__ import annotations

from devcanvas_api.pipeline.schemas import (
    RequirementSpec,
    ScreenKind,
    ScreenSpec,
    ScreenState,
    ScreenType,
    UXPlan,
)
from devcanvas_api.pipeline.ux import templates


def _entity_label(entity: str) -> str:
    """엔티티명을 한글 라벨로 단순 변환(Customer → 고객). 정규 매핑은 향후."""
    mapping = {
        "Customer": "고객",
        "Contract": "계약",
        "Payment": "결제",
        "Order": "주문",
        "User": "사용자",
    }
    return mapping.get(entity, entity)


def _build_screen(name: str, purpose: str, kind: ScreenKind, entity: str) -> ScreenSpec:
    return ScreenSpec(
        name=name,
        purpose=purpose,
        kind=kind,
        components=templates.components(kind),
        data_columns=templates.data_columns(kind),
        filters=templates.filters(kind),
        actions=templates.actions(kind, entity),
    )


def build_ux_plan(requirement: RequirementSpec, screen_type: ScreenType) -> UXPlan:
    """요구사항 + 화면 유형으로 UXPlan(화면 목록 + State Matrix + 흐름)을 생성한다."""
    screens: list[ScreenSpec] = []
    states: dict[str, ScreenState] = {}

    # screen_type 주화면: dashboard 유형이면 대시보드, 아니면 첫 엔티티 목록
    if screen_type == ScreenType.DASHBOARD:
        dash = _build_screen(
            name="대시보드",
            purpose="핵심 지표와 최근 활동을 한눈에",
            kind=ScreenKind.DASHBOARD,
            entity="대시보드",
        )
        screens.append(dash)
        states[dash.name] = templates.state(ScreenKind.DASHBOARD, "대시보드")

    entities = requirement.data_entities or []
    for entity in entities:
        label = _entity_label(entity)
        list_screen = _build_screen(
            name=f"{label} 목록",
            purpose=f"{label} 현황을 표 형태로 조회·필터링",
            kind=ScreenKind.LIST,
            entity=label,
        )
        detail_screen = _build_screen(
            name=f"{label} 상세",
            purpose=f"단일 {label} 정보와 관련 이력",
            kind=ScreenKind.DETAIL,
            entity=label,
        )
        screens.extend([list_screen, detail_screen])
        states[list_screen.name] = templates.state(ScreenKind.LIST, label)
        states[detail_screen.name] = templates.state(ScreenKind.DETAIL, label)

    # 엔티티가 없고 dashboard도 아니면(admin/internal_tool) 기본 목록 화면 보장
    if not screens:
        fallback = _build_screen(
            name="목록",
            purpose="데이터 목록 조회·필터링",
            kind=ScreenKind.LIST,
            entity="항목",
        )
        screens.append(fallback)
        states[fallback.name] = templates.state(ScreenKind.LIST, "항목")

    flows = _build_flows(screen_type, screens)

    return UXPlan(screens=screens, flows=flows, states=states)


def _build_flows(screen_type: ScreenType, screens: list[ScreenSpec]) -> list[str]:
    """화면들을 잇는 사용자 흐름을 생성."""
    names = [s.name for s in screens]
    if len(names) >= 2:
        return [" → ".join(names[:3])]  # 주화면 → 목록 → 상세
    return [names[0]] if names else []
