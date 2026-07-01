"""파이프라인 오케스트레이터 — 7단계 에이전트 순차 실행."""

from __future__ import annotations

from devcanvas_api.pipeline import agents
from devcanvas_api.pipeline.design.exporter import to_code_files
from devcanvas_api.pipeline.llm import LLMAdapter
from devcanvas_api.pipeline.schemas import GenerationInput, GenerationResult


def run_pipeline(generation_input: GenerationInput, llm: LLMAdapter) -> GenerationResult:
    """7단계 에이전트를 순차 실행해 GenerationResult를 생산한다."""
    requirement = agents.requirement_agent(generation_input, llm)
    ux_plan = agents.ux_planner_agent(requirement, llm)
    design_system = agents.design_system_agent(generation_input, requirement, llm)
    ui = agents.ui_generator_agent(ux_plan, design_system, llm)
    code = agents.code_generator_agent(generation_input, ui, llm)
    review = agents.review_agent(ui, code, llm)
    handoff = agents.handoff_agent(code, review, llm)

    # 디자인 토큰 산출물을 코드 파일에 병합 (ADR-0009)
    token_files = to_code_files(design_system)

    return GenerationResult(
        input=generation_input,
        requirement=requirement,
        ux_plan=ux_plan,
        design_system=design_system,
        ui=ui,
        code=code.files + token_files,
        review=review.findings,
        handoff=handoff,
    )
