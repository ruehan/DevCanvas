"""LLM 어댑터 경계 케이스 테스트."""

from __future__ import annotations

import pytest
from pydantic import BaseModel

from devcanvas_api.pipeline.llm import DummyLLMAdapter, GLMAdapter
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


def test_glm_stub_raises_without_config() -> None:
    # 키/엔드포인트 미설정 환경에서는 NotImplementedError
    adapter = GLMAdapter(api_key=None, api_base=None)
    with pytest.raises(NotImplementedError):
        adapter.generate(RequirementSpec, "x", {})


def test_glm_stub_raises_not_implemented_with_config() -> None:
    # 설정돼 있어도 실구현체 전이므로 NotImplementedError (ADR-0005)
    adapter = GLMAdapter(api_key="dummy", api_base="https://example.invalid")
    with pytest.raises(NotImplementedError):
        adapter.generate(RequirementSpec, "x", {})
