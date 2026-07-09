"""편집 에이전트 — 대화로 기존 결과 수정 (ADR-0018).

전체 결과 재생성 방식: LLM 에게 (현재 결과 + 지시) 를 주고 수정된 전체 GenerationResult 반환.
"""

from __future__ import annotations

from devcanvas_api.pipeline.llm import LLMAdapter
from devcanvas_api.pipeline.schemas import GenerationResult

EDIT_INSTRUCTION = "사용자 지시에 따라 기존 생성 결과를 수정하라."

# 편집 턴의 에이전트 단계(진행 노출용)
EDIT_STEPS = ["요청 분석", "결과 수정"]


def apply_edit(
    current_result: GenerationResult, instruction: str, llm: LLMAdapter
) -> GenerationResult:
    """사용자 지시에 따라 기존 결과를 수정한 새 GenerationResult 를 반환한다."""
    return llm.generate(
        GenerationResult,
        EDIT_INSTRUCTION,
        {
            "current_result": current_result.model_dump(),
            "instruction": instruction,
        },
    )
