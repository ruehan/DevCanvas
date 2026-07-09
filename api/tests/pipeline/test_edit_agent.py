"""편집 에이전트 테스트 (ADR-0018)."""

from __future__ import annotations

from typing import Any

from devcanvas_api.pipeline.edit_agent import apply_edit
from devcanvas_api.pipeline.llm import DummyLLMAdapter
from devcanvas_api.pipeline.schemas import GenerationResult


def _result() -> GenerationResult:
    from devcanvas_api.pipeline.fixtures import generation_result

    return generation_result()


def test_apply_edit_returns_generation_result() -> None:
    edited = apply_edit(_result(), "버튼을 더 둥글게", DummyLLMAdapter())
    assert isinstance(edited, GenerationResult)
    assert edited.input  # 결과가 채워져 있음


class _ProbeLLM:
    def generate(
        self,
        schema: type[GenerationResult],
        instruction: str,
        context: dict[str, object],
    ) -> GenerationResult:
        captured["schema"] = schema
        captured["instruction"] = instruction
        captured["context"] = context
        return _result()


captured: dict[str, Any] = {}


def test_apply_edit_passes_current_result_and_instruction_to_llm() -> None:
    captured.clear()
    probe: Any = _ProbeLLM()
    apply_edit(_result(), "고객 테이블에 계약일 추가", probe)
    assert captured["schema"] is GenerationResult
    assert "수정" in captured["instruction"]
    ctx = captured["context"]
    assert isinstance(ctx, dict)
    assert "current_result" in ctx and "instruction" in ctx
    assert ctx["instruction"] == "고객 테이블에 계약일 추가"
