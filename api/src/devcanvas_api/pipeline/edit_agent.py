"""편집 에이전트 — 대화로 기존 결과 수정 (ADR-0023, ADR-0018 대체).

부분 패치 방식: LLM 에게 (현재 결과 + 지시)를 주고 **바뀐 최상위 섹션만** 담은 패치를 받아
기존 결과에 병합한다. 전체 재생성(ADR-0018) 대비 출력 토큰을 크게 줄여 timeout/비용을 완화한다.
"""

from __future__ import annotations

from devcanvas_api.pipeline.llm import LLMAdapter
from devcanvas_api.pipeline.schemas import GenerationResult, GenerationResultPatch

EDIT_INSTRUCTION = (
    "사용자 지시에 따라 기존 생성 결과를 수정하라. "
    "변경되는 최상위 섹션만 JSON 으로 반환한다(예: ux_plan, ui). "
    "바뀌지 않는 섹션은 생략한다 — 특히 code, handoff 는 지시가 직접 요구하지 않으면 넣지 않는다. "
    "섹션을 포함할 때는 그 섹션 전체를 완전하게 담아라: 기존 결과의 모든 하위 항목·필드를 "
    "그대로 유지하고(어떤 필드도 생략하지 말 것) 지시에 해당하는 값만 변경한다. "
    "즉 포함하는 섹션은 '기존 값을 복사한 뒤 필요한 부분만 고친' 완전한 형태여야 한다."
)

# 편집 턴의 에이전트 단계(진행 노출용). 편집은 단일 LLM 호출이므로 1단계가 정직(리뷰 P3-2).
EDIT_STEPS = ["결과 수정"]


def merge_patch(current: GenerationResult, patch: GenerationResultPatch) -> GenerationResult:
    """패치의 제공된(non-None) 최상위 필드로 기존 결과를 덮어써 새 결과를 만든다.

    최상위 교체 병합: 섹션 단위로 교체(부분 딥머지 아님). 병합 후 GenerationResult 로
    재검증하므로 결과는 항상 유효한 스키마다.
    """
    data = current.model_dump()
    data.update(patch.model_dump(exclude_none=True))
    return GenerationResult.model_validate(data)


def apply_edit(
    current_result: GenerationResult, instruction: str, llm: LLMAdapter
) -> GenerationResult:
    """사용자 지시에 따라 기존 결과를 부분 수정한 새 GenerationResult 를 반환한다."""
    # include_schema=False: current_result 가 이미 구조 예시(ADR-0022). 패치 스키마의 formal
    # JSON 스키마는 여전히 거대(중첩)하므로 생략하고, 반환 형식은 EDIT_INSTRUCTION 으로 지시.
    patch = llm.generate(
        GenerationResultPatch,
        EDIT_INSTRUCTION,
        {
            "current_result": current_result.model_dump(),
            "instruction": instruction,
        },
        include_schema=False,
    )
    return merge_patch(current_result, patch)
