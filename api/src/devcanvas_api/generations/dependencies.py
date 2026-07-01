"""generations 도메인 의존성."""

from __future__ import annotations

from functools import lru_cache

from devcanvas_api.core.config import settings
from devcanvas_api.pipeline.llm import DummyLLMAdapter, GLMAdapter, LLMAdapter


@lru_cache
def get_llm_adapter() -> LLMAdapter:
    """설정에 따라 LLM 어댑터를 선택한다.

    GLM 키가 설정돼 있으면 GLMAdapter, 아니면 DummyLLMAdapter.
    (ADR-0005: MVP는 더미로 동작, GLM 키는 .env로 주입)
    """
    if settings.glm_api_key and settings.glm_api_base:
        return GLMAdapter()
    return DummyLLMAdapter()
