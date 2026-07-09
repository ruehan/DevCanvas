"""파이프라인 공용 의존성 — LLM 어댑터 팩토리.

LLM 포트(pipeline/llm.py)의 소유가 pipeline 이므로, 팩토리도 pipeline 의 public 자원.
LLM 이 필요한 도메인(generations, sessions)은 여기서 의존을 가져간다(리뷰 P2-1).
"""

from __future__ import annotations

from functools import lru_cache

from devcanvas_api.core import settings
from devcanvas_api.pipeline.llm import DummyLLMAdapter, GLMAdapter, LLMAdapter


@lru_cache
def get_llm_adapter() -> LLMAdapter:
    """설정에 따라 LLM 어댑터를 선택한다.

    GLM 키가 설정돼 있으면 GLMAdapter(glm-5.2), 아니면 DummyLLMAdapter.
    (ADR-0005/0007: MVP는 더미로 동작, GLM 키는 .env로 주입)

    캐시 의미론: @lru_cache 는 프로세스당 1회만 평가한다. 런타임에 설정(키 on/off)을
    토글하는 테스트에서는 get_llm_adapter.cache_clear() 로 캐시를 무효화해야 한다.
    """
    if settings.glm_api_key:
        return GLMAdapter()
    return DummyLLMAdapter()
