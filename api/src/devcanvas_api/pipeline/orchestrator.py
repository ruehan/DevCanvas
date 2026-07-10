"""파이프라인 오케스트레이터 — 7단계 에이전트 순차 실행."""

from __future__ import annotations

import logging

from devcanvas_api.pipeline import agents
from devcanvas_api.pipeline.design.exporter import to_code_files
from devcanvas_api.pipeline.llm import LLMAdapter
from devcanvas_api.pipeline.schemas import (
    CodeFile,
    CodeGeneration,
    GenerationInput,
    GenerationResult,
)

logger = logging.getLogger(__name__)


def _merge_code(app_files: list[CodeFile], token_files: list[CodeFile]) -> list[CodeFile]:
    """앱 코드와 토큰 파일을 병합한다. path 충돌 시 토큰 파일이 우선(예약 경로, ADR-0009).

    충돌이 발생하면 경고 로깅 — 향후 실 code_generator 가 예약 경로를 침범했는지 추적.
    """
    token_paths = {f.path for f in token_files}
    merged: list[CodeFile] = []
    for f in app_files:
        if f.path in token_paths:
            logger.warning(
                "code_generator 산출이 토큰 예약 경로 %r 침범 — 토큰 파일로 대체", f.path
            )
            continue
        merged.append(f)
    return merged + token_files


def run_pipeline(generation_input: GenerationInput, llm: LLMAdapter) -> GenerationResult:
    """7단계 에이전트를 순차 실행해 GenerationResult를 생산한다."""
    requirement = agents.requirement_agent(generation_input, llm)
    ux_plan = agents.ux_planner_agent(requirement, generation_input, llm)
    design_system = agents.design_system_agent(generation_input, requirement, llm)
    ui = agents.ui_generator_agent(ux_plan, design_system, generation_input, llm)
    code = agents.code_generator_agent(generation_input, ui, llm)

    # 디자인 토큰 산출물을 코드 파일에 병합 (ADR-0009).
    # handoff 가 토큰 파일까지 file_tree/guide 에 반영하도록 병합을 handoff 호출 전으로 둔다
    # (ADR-0016).
    token_files = to_code_files(design_system)
    merged_code = CodeGeneration(files=_merge_code(code.files, token_files))

    # review 는 토큰(결정적 산출)을 린트할 필요 없으므로 병합 전 code 사용
    review = agents.review_agent(ui, code, llm)
    handoff = agents.handoff_agent(merged_code, review, llm)

    return GenerationResult(
        input=generation_input,
        requirement=requirement,
        ux_plan=ux_plan,
        design_system=design_system,
        ui=ui,
        code=merged_code.files,
        review=review.findings,
        handoff=handoff,
    )
