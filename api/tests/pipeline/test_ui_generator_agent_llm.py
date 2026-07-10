"""UI 생성기 LLM 전환 테스트 (ADR-0024, 0011 보완)."""

from __future__ import annotations

from typing import Any

from devcanvas_api.pipeline.agents import ui_generator_agent
from devcanvas_api.pipeline.llm import DummyLLMAdapter
from devcanvas_api.pipeline.schemas import (
    DesignSystem,
    GenerationInput,
    ScreenKind,
    ScreenLayout,
    ScreenSpec,
    UIGeneration,
    UXPlan,
)


def _plan() -> UXPlan:
    return UXPlan(
        screens=[
            ScreenSpec(name="대시보드", purpose="지표", kind=ScreenKind.DASHBOARD),
            ScreenSpec(name="고객 목록", purpose="조회", kind=ScreenKind.LIST),
        ],
        flows=[],
        states={},
    )


def _ds() -> DesignSystem:
    return DesignSystem()


def _input() -> GenerationInput:
    return GenerationInput(prompt="테스트")


def test_ui_generator_calls_llm_with_context() -> None:
    captured: dict[str, Any] = {}

    class ProbeLLM:
        def generate(self, schema, instruction, context):  # type: ignore[no-untyped-def]
            captured["schema"] = schema
            captured["instruction"] = instruction
            captured["context"] = context
            return UIGeneration(
                layouts=[
                    ScreenLayout(
                        screen="대시보드",
                        layout="KPI 그리드",
                        kind=ScreenKind.DASHBOARD,
                        component_tree=["KpiCard", "Chart"],
                    ),
                    ScreenLayout(
                        screen="고객 목록",
                        layout="필터+테이블",
                        kind=ScreenKind.LIST,
                        component_tree=["DataTable"],
                    ),
                ]
            )

    ui_generator_agent(_plan(), _ds(), _input(), ProbeLLM())  # type: ignore[arg-type]
    assert captured["schema"] is UIGeneration
    assert "instruction" in captured
    assert "ux_plan" in captured["context"] or "requirement" in captured["context"]


def test_ui_generator_preserves_llm_layout_when_valid() -> None:
    """LLM 결과가 계약(수 일치, kind 일치, tree 비어있지 않음)을 만족하면 그대로 사용."""

    class GoodLLM:
        def generate(self, schema, instruction, context):  # type: ignore[no-untyped-def]
            return UIGeneration(
                layouts=[
                    ScreenLayout(
                        screen="대시보드",
                        layout="KPI 그리드 2x2",
                        kind=ScreenKind.DASHBOARD,
                        component_tree=["KpiCard", "Chart", "ActivityFeed"],
                    ),
                    ScreenLayout(
                        screen="고객 목록",
                        layout="검색바 상단 + 테이블",
                        kind=ScreenKind.LIST,
                        component_tree=["SearchBar", "DataTable", "Pagination"],
                    ),
                ]
            )

    gen = ui_generator_agent(_plan(), _ds(), _input(), GoodLLM())  # type: ignore[arg-type]
    assert len(gen.layouts) == 2
    assert gen.layouts[0].layout == "KPI 그리드 2x2"
    assert gen.layouts[0].component_tree == ["KpiCard", "Chart", "ActivityFeed"]


def test_ui_generator_falls_back_on_kind_mismatch() -> None:
    """LLM이 kind를 잘못 바꾸면 rule-based fallback (ADR-0024)."""

    class WrongKindLLM:
        def generate(self, schema, instruction, context):  # type: ignore[no-untyped-def]
            # 대시보드 kind를 LIST로 잘못 반환
            return UIGeneration(
                layouts=[
                    ScreenLayout(
                        screen="대시보드",
                        layout="x",
                        kind=ScreenKind.LIST,
                        component_tree=["A"],
                    ),
                    ScreenLayout(
                        screen="고객 목록",
                        layout="y",
                        kind=ScreenKind.LIST,
                        component_tree=["B"],
                    ),
                ]
            )

    gen = ui_generator_agent(_plan(), _ds(), _input(), WrongKindLLM())  # type: ignore[arg-type]
    # fallback: rule-based 결과 — 대시보드 kind는 DASHBOARD
    dash = next(lay for lay in gen.layouts if lay.screen == "대시보드")
    assert dash.kind == ScreenKind.DASHBOARD


def test_ui_generator_falls_back_on_empty_component_tree() -> None:
    class EmptyTreeLLM:
        def generate(self, schema, instruction, context):  # type: ignore[no-untyped-def]
            return UIGeneration(
                layouts=[
                    ScreenLayout(
                        screen="대시보드",
                        layout="x",
                        kind=ScreenKind.DASHBOARD,
                        component_tree=[],
                    ),
                    ScreenLayout(
                        screen="고객 목록",
                        layout="y",
                        kind=ScreenKind.LIST,
                        component_tree=[],
                    ),
                ]
            )

    gen = ui_generator_agent(_plan(), _ds(), _input(), EmptyTreeLLM())  # type: ignore[arg-type]
    # fallback → 템플릿의 component_tree 사용
    for lay in gen.layouts:
        assert lay.component_tree


def test_ui_generator_falls_back_on_count_mismatch() -> None:
    """LLM 반환 layout 수가 UX plan screen 수와 다르면 fallback."""

    class TooFewLLM:
        def generate(self, schema, instruction, context):  # type: ignore[no-untyped-def]
            return UIGeneration(
                layouts=[
                    ScreenLayout(
                        screen="대시보드",
                        layout="x",
                        kind=ScreenKind.DASHBOARD,
                        component_tree=["A"],
                    ),
                ]
            )

    gen = ui_generator_agent(_plan(), _ds(), _input(), TooFewLLM())  # type: ignore[arg-type]
    # fallback → 모든 screen에 대해 layout 존재
    assert len(gen.layouts) == 2


def test_ui_generator_with_dummy_runs() -> None:
    """DummyLLMAdapter로도 정상 동작해야 한다 (LLM 키 미설정 환경 대비)."""
    gen = ui_generator_agent(_plan(), _ds(), _input(), DummyLLMAdapter())
    assert len(gen.layouts) == 2
    for lay in gen.layouts:
        assert lay.component_tree


def test_ui_generator_llm_tree_differs_by_kind() -> None:
    """LLM의 component_tree는 kind별로 다른 후보를 줄 수 있어야 한다 (다양화 보장)."""
    seen: set[frozenset[str]] = set()

    class TreeByKindLLM:
        def __init__(self) -> None:
            self._n = 0

        def generate(self, schema, instruction, context):  # type: ignore[no-untyped-def]
            self._n += 1
            if self._n == 1:
                tree = ["KpiCard", "Chart", "ActivityFeed"]
            else:
                tree = ["SearchBar", "DataTable", "Pagination"]
            return UIGeneration(
                layouts=[
                    ScreenLayout(
                        screen="대시보드",
                        layout="KPI 그리드",
                        kind=ScreenKind.DASHBOARD,
                        component_tree=tree,
                    ),
                    ScreenLayout(
                        screen="고객 목록",
                        layout="검색+테이블",
                        kind=ScreenKind.LIST,
                        component_tree=["FilterBar", "DataTable"],
                    ),
                ]
            )

    probe = TreeByKindLLM()
    seen.add(frozenset(probe.generate(UIGeneration, "", {}).layouts[0].component_tree))  # type: ignore[no-untyped-call]
    llm = TreeByKindLLM()
    gen = ui_generator_agent(_plan(), _ds(), _input(), llm)  # type: ignore[arg-type]
    trees = {frozenset(lay.component_tree) for lay in gen.layouts}
    assert len(trees) >= 2  # 두 화면의 tree가 서로 다름