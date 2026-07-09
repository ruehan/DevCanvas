"""LLM 어댑터 경계 케이스 테스트."""

from __future__ import annotations

import pytest
from pydantic import BaseModel

from devcanvas_api.pipeline.llm import DummyLLMAdapter, GenerationError, GLMAdapter
from devcanvas_api.pipeline.schemas import RequirementSpec


class _UnknownSchema(BaseModel):
    value: str


def test_dummy_raises_on_unknown_schema() -> None:
    adapter = DummyLLMAdapter()
    with pytest.raises(NotImplementedError):
        adapter.generate(_UnknownSchema, "x", {})


def test_dummy_returns_independent_copy() -> None:
    adapter = DummyLLMAdapter()
    first = adapter.generate(RequirementSpec, "x", {})
    second = adapter.generate(RequirementSpec, "x", {})
    first.features.append("새 기능")
    assert "새 기능" not in second.features  # 복사본이므로 격리됨


def test_glm_without_key_raises_generation_error() -> None:
    # 키 미설정 시 GenerationError (ADR-0007)
    adapter = GLMAdapter(api_key=None, api_base="https://x")
    with pytest.raises(GenerationError):
        adapter.generate(RequirementSpec, "x", {})
