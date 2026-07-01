"""generations 비즈니스 로직."""

from __future__ import annotations

from devcanvas_api.pipeline.llm import LLMAdapter
from devcanvas_api.pipeline.orchestrator import run_pipeline
from devcanvas_api.pipeline.schemas import GenerationInput, GenerationResult


def generate(generation_input: GenerationInput, llm: LLMAdapter) -> GenerationResult:
    """파이프라인을 실행해 생성 결과를 반환한다."""
    return run_pipeline(generation_input, llm)
