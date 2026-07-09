"""편집 에이전트 테스트 (ADR-0023 부분 패치, ADR-0018 대체)."""

from __future__ import annotations

from typing import Any

from devcanvas_api.pipeline.edit_agent import apply_edit, merge_patch
from devcanvas_api.pipeline.llm import DummyLLMAdapter
from devcanvas_api.pipeline.schemas import (
    GenerationResult,
    GenerationResultPatch,
    RequirementSpec,
)


def _result() -> GenerationResult:
    from devcanvas_api.pipeline.fixtures import generation_result

    return generation_result()


def test_apply_edit_returns_generation_result() -> None:
    edited = apply_edit(_result(), "버튼을 더 둥글게", DummyLLMAdapter())
    assert isinstance(edited, GenerationResult)
    assert edited.input  # 결과가 채워져 있음
    # 더미 패치는 requirement 만 수정 → 병합 결과에 반영, 나머지 섹션은 원본 유지
    assert "편집 요청 반영(더미)" in edited.requirement.features
    assert edited.code == _result().code  # 패치에 없던 섹션은 그대로


def test_merge_patch_replaces_only_provided_sections() -> None:
    current = _result()
    patch = GenerationResultPatch(requirement=RequirementSpec(features=["새 기능"]))
    merged = merge_patch(current, patch)
    assert merged.requirement.features == ["새 기능"]  # 교체됨
    assert merged.ux_plan == current.ux_plan  # 미제공 섹션 유지
    assert merged.input == current.input


class _ProbeLLM:
    def generate(
        self,
        schema: type[Any],
        instruction: str,
        context: dict[str, object],
        *,
        include_schema: bool = True,
    ) -> GenerationResultPatch:
        captured["schema"] = schema
        captured["instruction"] = instruction
        captured["context"] = context
        captured["include_schema"] = include_schema
        return GenerationResultPatch()  # 빈 패치(변경 없음)


captured: dict[str, Any] = {}


def test_apply_edit_requests_patch_from_llm() -> None:
    captured.clear()
    probe: Any = _ProbeLLM()
    apply_edit(_result(), "고객 테이블에 계약일 추가", probe)
    # 전체 GenerationResult 가 아니라 부분 패치 스키마를 요청(ADR-0023)
    assert captured["schema"] is GenerationResultPatch
    assert "수정" in captured["instruction"]
    ctx = captured["context"]
    assert isinstance(ctx, dict)
    assert "current_result" in ctx and "instruction" in ctx
    assert ctx["instruction"] == "고객 테이블에 계약일 추가"
    # 편집은 formal 스키마 생략(ADR-0022) — current_result 가 구조 예시
    assert captured["include_schema"] is False
