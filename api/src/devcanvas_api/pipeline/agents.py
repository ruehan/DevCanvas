"""7단계 에이전트.

각 에이전트는 누적 컨텍스트와 LLM 어댑터로 자기 단계 산출 스키마를 생성한다.
현재 instruction 은 프롬프트 초안이며, GLM 실구현체 도입 시 시스템 프롬프트·템플릿과
함께 정제한다. 응답 검증/재시도 정책은 ADR-0007(예정)에서 다룬다.
"""

from __future__ import annotations

from devcanvas_api.pipeline.code.generator import build_code_generation
from devcanvas_api.pipeline.design.presets import build_design_system
from devcanvas_api.pipeline.handoff.builder import build_handoff
from devcanvas_api.pipeline.llm import LLMAdapter
from devcanvas_api.pipeline.review.reviewer import run_review
from devcanvas_api.pipeline.schemas import (
    CodeGeneration,
    DesignSystem,
    GenerationInput,
    HandoffDoc,
    RequirementSpec,
    ReviewReport,
    UIGeneration,
    UXPlan,
)
from devcanvas_api.pipeline.ui.generator import build_ui_generation
from devcanvas_api.pipeline.ux.planner import build_ux_plan


def requirement_agent(generation_input: GenerationInput, llm: LLMAdapter) -> RequirementSpec:
    instruction = "요구사항을 분석해 기능·사용자·화면·데이터 엔티티를 추출하라."
    return llm.generate(
        RequirementSpec,
        instruction,
        {"prompt": generation_input.prompt, "screen_type": generation_input.screen_type},
    )


def ux_planner_agent(
    requirement: RequirementSpec,
    generation_input: GenerationInput,
    llm: LLMAdapter,
) -> UXPlan:
    """요구사항에서 화면·State Matrix를 규칙 기반으로 도출한다 (ADR-0010, LLM 미사용)."""
    del llm  # 규칙 기반
    return build_ux_plan(requirement, generation_input.screen_type)


def design_system_agent(
    generation_input: GenerationInput, requirement: RequirementSpec, llm: LLMAdapter
) -> DesignSystem:
    """톤 기반 규칙으로 디자인 토큰을 생성한다 (ADR-0008, LLM 미사용).

    llm 인자는 파이프라인 시그니처 일관성을 위해 유지하되 사용하지 않는다.
    향후 브랜드 키워드 정제를 LLM 에 맡기면 이 지점에서 호출한다.
    """
    del requirement, llm  # 규칙 기반 — 현재 미사용
    return build_design_system(generation_input.tone)


def ui_generator_agent(
    ux_plan: UXPlan,
    design_system: DesignSystem,
    generation_input: GenerationInput,
    llm: LLMAdapter,
) -> UIGeneration:
    """UXPlan 에서 화면별 레이아웃·컴포넌트 트리를 LLM 으로 도출 (ADR-0024, 0011 보완).

    LLM 이 각 layout 의 `layout` 문자열과 `component_tree` 를 자체 결정. 계약 위반 시
    rule-based(build_ui_generation)로 graceful fallback. design_system 은 컨텍스트로
    전달되지만 현재 미사용 — 향후 토큰·테마 기반 변형에 활용 예정.
    """
    instruction = (
        "UXPlan 의 각 화면에 대해 화면 배치(layout 문자열)와 렌더 순서 컴포넌트 트리를 설계하라. "
        "각 layout 의 screen 이름과 kind 는 대응 ScreenSpec 와 정확히 일치해야 한다. "
        "component_tree 는 비어있지 않아야 하며 화면 목적에 맞는 실제 컴포넌트 이름(KpiCard, "
        "DataTable, Tabs 등)을 자유롭게 선택하라."
    )
    generated = llm.generate(
        UIGeneration,
        instruction,
        {
            "ux_plan": ux_plan.model_dump(),
            "design_system": design_system.model_dump(),
            "screen_type": generation_input.screen_type.value,
            "tone": generation_input.tone.value,
        },
    )
    if not _ui_matches_plan(ux_plan, generated):
        return build_ui_generation(ux_plan)
    return generated


def _ui_matches_plan(plan: UXPlan, gen: UIGeneration) -> bool:
    """LLM 반환 UIGeneration 이 UXPlan 과 계약 일치하는지 검증 (ADR-0024 fallback 기준).

    - layout 수가 screen 수와 같고
    - 모든 screen name 이 layout.screen 에 존재하며
    - 각 layout.kind == 대응 ScreenSpec.kind
    - 각 layout.component_tree 비어있지 않음
    """
    if len(gen.layouts) != len(plan.screens):
        return False
    by_name = {lay.screen: lay for lay in gen.layouts}
    for screen in plan.screens:
        lay = by_name.get(screen.name)
        if lay is None:
            return False
        if lay.kind != screen.kind:
            return False
        if not lay.component_tree:
            return False
    return True


def code_generator_agent(
    generation_input: GenerationInput, ui: UIGeneration, llm: LLMAdapter
) -> CodeGeneration:
    """UIGeneration 에서 코드 파일을 규칙 기반 생성 (ADR-0012, LLM 미사용).

    generation_input/llm 은 시그니처 일관성을 위해 유지하되 현재 미사용.
    """
    del generation_input, llm
    return build_code_generation(ui)


def review_agent(
    ui: UIGeneration, code: CodeGeneration, llm: LLMAdapter
) -> ReviewReport:
    """생성 코드를 결정적 린트 체크로 검사 (ADR-0013, LLM 미사용).

    ui/llm 은 시그니처 일관성을 위해 유지하되 현재 미사용.
    """
    del ui, llm
    return run_review(code)


def handoff_agent(
    code: CodeGeneration, review: ReviewReport, llm: LLMAdapter
) -> HandoffDoc:
    """code/review 에서 파일 트리·설치·TODO·가이드를 규칙 기반 유도 (ADR-0016, LLM 미사용)."""
    del llm
    return build_handoff(code, review)
