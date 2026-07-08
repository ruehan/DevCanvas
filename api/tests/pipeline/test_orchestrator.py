"""파이프라인 테스트."""

from __future__ import annotations

import pytest

from devcanvas_api.pipeline.llm import DummyLLMAdapter
from devcanvas_api.pipeline.orchestrator import run_pipeline
from devcanvas_api.pipeline.schemas import GenerationInput, ScreenType, Tone


@pytest.fixture()
def sample_input() -> GenerationInput:
    return GenerationInput(
        prompt="B2B SaaS 관리자 페이지. 고객 목록, 결제 상태, 계약 만료일, 검색, 필터, 상세 보기.",
        screen_type=ScreenType.ADMIN,
        service_type="SaaS",
        data_fields=["고객명", "결제 상태", "계약일"],
    )


def test_pipeline_produces_full_result(sample_input: GenerationInput) -> None:
    result = run_pipeline(sample_input, DummyLLMAdapter())

    # 모든 7단계 산출물이 채워져야 한다
    assert result.requirement.features
    assert result.requirement.screens
    assert result.ux_plan.screens
    assert result.ux_plan.flows
    # 상태 매트릭스: 각 화면마다 상태 정의
    assert result.ux_plan.states
    for state in result.ux_plan.states.values():
        assert state.loading and state.empty and state.error
    assert result.design_system.tokens.colors
    assert result.design_system.tokens.spacing
    assert result.ui.layouts
    assert result.code  # 최소 한 개 코드 파일
    assert any(f.path.endswith(".tsx") for f in result.code)
    assert result.handoff.file_tree
    assert result.handoff.guide_md


def test_pipeline_input_echoed_in_result(sample_input: GenerationInput) -> None:
    result = run_pipeline(sample_input, DummyLLMAdapter())
    assert result.input.prompt == sample_input.prompt
    assert result.input.screen_type == ScreenType.ADMIN


def test_pipeline_with_empty_prompt_still_runs() -> None:
    # 빈 프롬프트도 더미 파이프라인은 구조적으로 동작해야 한다
    result = run_pipeline(GenerationInput(prompt=""), DummyLLMAdapter())
    assert result.requirement.features  # 더미 fixture는 채워짐
    assert result.input.prompt == ""


def test_pipeline_design_system_reflects_tone() -> None:
    # design_system_agent 는 규칙 기반이므로 톤이 결과에 반영되어야 한다 (ADR-0008)
    b2b = run_pipeline(GenerationInput(prompt="x", tone=Tone.B2B), DummyLLMAdapter())
    startup = run_pipeline(GenerationInput(prompt="x", tone=Tone.STARTUP), DummyLLMAdapter())
    b2b_primary = b2b.design_system.tokens.colors["primary"]
    startup_primary = startup.design_system.tokens.colors["primary"]
    assert b2b_primary != startup_primary
    assert b2b.design_system.tokens.shadows  # shadows 토큰 채워짐


def test_pipeline_ux_plan_state_matrix_complete() -> None:
    # ux_planner_agent 는 규칙 기반 — 모든 화면에 5상태가 완결 (ADR-0010)
    result = run_pipeline(
        GenerationInput(prompt="x", screen_type=ScreenType.DASHBOARD), DummyLLMAdapter()
    )
    assert result.ux_plan.screens
    # 모든 화면이 상태 매트릭스에 존재
    for screen in result.ux_plan.screens:
        assert screen.name in result.ux_plan.states


def test_pipeline_ui_layouts_match_screens() -> None:
    # ui_generator_agent 는 규칙 기반 — 화면마다 레이아웃 1:1 (ADR-0011)
    result = run_pipeline(
        GenerationInput(prompt="x", screen_type=ScreenType.DASHBOARD), DummyLLMAdapter()
    )
    assert len(result.ui.layouts) == len(result.ux_plan.screens)
    layout_screens = {lay.screen for lay in result.ui.layouts}
    plan_screens = {s.name for s in result.ux_plan.screens}
    assert layout_screens == plan_screens


def test_pipeline_review_produces_findings() -> None:
    # review_agent 는 규칙 기반 린트 — 생성 코드에서 findings 생산 (ADR-0013)
    result = run_pipeline(
        GenerationInput(prompt="x", screen_type=ScreenType.DASHBOARD), DummyLLMAdapter()
    )
    assert result.review  # 생성 코드엔 TODO/mock 등 리뷰 대상
    categories = {f.category for f in result.review}
    assert "state" in categories  # 상태 분기 TODO → P1


def test_pipeline_handoff_includes_token_files() -> None:
    # 핸드오프가 토큰 병합본을 받아 file_tree 에 토큰 파일 포함 (ADR-0009/0016 갭 해소)
    result = run_pipeline(
        GenerationInput(prompt="x", screen_type=ScreenType.DASHBOARD), DummyLLMAdapter()
    )
    tree = set(result.handoff.file_tree)
    assert "lib/tokens.ts" in tree
    assert "tailwind.config.json" in tree
    assert "styles/tokens.css" in tree


def test_pipeline_includes_design_token_files_in_code() -> None:
    # exporter 산출이 result.code 에 연결되어야 한다 (ADR-0009)
    result = run_pipeline(GenerationInput(prompt="x", tone=Tone.B2B), DummyLLMAdapter())
    code_paths = {f.path for f in result.code}
    assert {
        "lib/tokens.ts",
        "tailwind.config.json",
        "tokens/design.json",
        "styles/tokens.css",
        "docs/design.md",
    }.issubset(code_paths)
    # 톤이 토큰 파일 내용에도 반영되어야 한다
    tokens_ts = next(f for f in result.code if f.path == "lib/tokens.ts")
    assert "#2563EB" in tokens_ts.content  # b2b primary


def test_pipeline_dedups_code_paths_token_files_win() -> None:
    # code_generator 가 예약 경로(tailwind.config.json)를 침범해도 토큰 파일이 승(단일)
    from devcanvas_api.pipeline.design.exporter import to_code_files
    from devcanvas_api.pipeline.orchestrator import _merge_code
    from devcanvas_api.pipeline.schemas import CodeFile, DesignSystem

    app = [CodeFile(path="tailwind.config.json", content="// LLM이 만든 것")]
    token = to_code_files(DesignSystem())
    merged = _merge_code(app, token)
    paths = [f.path for f in merged]
    assert paths.count("tailwind.config.json") == 1
    tw = next(f for f in merged if f.path == "tailwind.config.json")
    assert tw.content != "// LLM이 만든 것"  # 토큰 파일 우선
