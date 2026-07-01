"""파이프라인 테스트."""

from __future__ import annotations

import pytest

from devcanvas_api.pipeline.llm import DummyLLMAdapter
from devcanvas_api.pipeline.orchestrator import run_pipeline
from devcanvas_api.pipeline.schemas import GenerationInput, ScreenType


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
