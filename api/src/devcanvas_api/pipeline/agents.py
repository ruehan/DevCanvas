"""7단계 에이전트.

각 에이전트는 누적 컨텍스트와 LLM 어댑터로 자기 단계 산출 스키마를 생성한다.
현재 instruction 은 프롬프트 초안이며, GLM 실구현체 도입 시 시스템 프롬프트·템플릿과
함께 정제한다. 응답 검증/재시도 정책은 ADR-0007(예정)에서 다룬다.
"""

from __future__ import annotations

from devcanvas_api.pipeline.design.presets import build_design_system
from devcanvas_api.pipeline.llm import LLMAdapter
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


def requirement_agent(generation_input: GenerationInput, llm: LLMAdapter) -> RequirementSpec:
    instruction = "요구사항을 분석해 기능·사용자·화면·데이터 엔티티를 추출하라."
    return llm.generate(
        RequirementSpec,
        instruction,
        {"prompt": generation_input.prompt, "screen_type": generation_input.screen_type},
    )


def ux_planner_agent(requirement: RequirementSpec, llm: LLMAdapter) -> UXPlan:
    instruction = "사용자 흐름, 화면 구조, 상태 매트릭스를 생성하라."
    return llm.generate(UXPlan, instruction, {"requirement": requirement.model_dump()})


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
    ux_plan: UXPlan, design_system: DesignSystem, llm: LLMAdapter
) -> UIGeneration:
    instruction = "화면별 레이아웃과 컴포넌트 트리를 생성하라."
    return llm.generate(
        UIGeneration,
        instruction,
        {"ux_plan": ux_plan.model_dump(), "design_system": design_system.model_dump()},
    )


def code_generator_agent(
    generation_input: GenerationInput, ui: UIGeneration, llm: LLMAdapter
) -> CodeGeneration:
    instruction = "지정된 스택 기준으로 React 코드 파일을 생성하라."
    return llm.generate(
        CodeGeneration,
        instruction,
        {"stack": generation_input.stack, "ui": ui.model_dump()},
    )


def review_agent(
    ui: UIGeneration, code: CodeGeneration, llm: LLMAdapter
) -> ReviewReport:
    instruction = "접근성·반응형·상태 누락·일관성을 검사하라."
    return llm.generate(
        ReviewReport,
        instruction,
        {"ui": ui.model_dump(), "code": code.model_dump()},
    )


def handoff_agent(
    code: CodeGeneration, review: ReviewReport, llm: LLMAdapter
) -> HandoffDoc:
    instruction = "개발자가 바로 쓸 수 있는 파일 구조·설치 명령·TODO·구현 가이드를 생성하라."
    return llm.generate(
        HandoffDoc,
        instruction,
        {"code": code.model_dump(), "review": review.model_dump()},
    )
