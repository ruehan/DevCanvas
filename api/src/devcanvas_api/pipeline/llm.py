"""LLM 어댑터 포트와 구현체 (ADR-0005, ADR-0006).

포트(Protocol)로 추상화하여:
- DummyLLMAdapter: 고정 fixture 반환, GLM 키 없이 전 파이프라인 검증용.
- GLMAdapter: GLM 5 Turbo 호출. 키/엔드포인트 미설정 시 NotImplementedError.
"""

from __future__ import annotations

from typing import Protocol, TypeVar

from pydantic import BaseModel

from devcanvas_api.core import settings
from devcanvas_api.pipeline import fixtures
from devcanvas_api.pipeline.schemas import (
    CodeGeneration,
    DesignSystem,
    HandoffDoc,
    RequirementSpec,
    ReviewReport,
    UIGeneration,
    UXPlan,
)

T = TypeVar("T", bound=BaseModel)


class LLMAdapter(Protocol):
    """구조화 출력을 내는 LLM 어댑터 포트."""

    def generate(self, schema: type[T], instruction: str, context: dict[str, object]) -> T:
        """instruction/context 로 schema 인스턴스를 생성해 반환한다."""
        ...


class DummyLLMAdapter:
    """GLM 키 없이 파이프라인을 end-to-end 돌리기 위한 더미 어댑터.

    스키마 타입별로 미리 준비된 fixture를 반환한다.
    반환 시 fixture의 깊은 복사본을 주어 호출부 수정이 전역 fixture를 오염시키지 않게 한다.
    """

    _FIXTURES: dict[type[BaseModel], object] = {
        RequirementSpec: fixtures.requirement(),
        UXPlan: fixtures.ux_plan(),
        DesignSystem: fixtures.design_system(),
        UIGeneration: fixtures.ui_generation(),
        CodeGeneration: fixtures.code_generation(),
        ReviewReport: fixtures.review_report(),
        HandoffDoc: fixtures.handoff(),
    }

    def generate(self, schema: type[T], instruction: str, context: dict[str, object]) -> T:
        fixture = self._FIXTURES.get(schema)
        if fixture is None:
            raise NotImplementedError(f"DummyLLMAdapter: {schema.__name__} fixture 없음")
        assert isinstance(fixture, BaseModel)
        return fixture.model_copy(deep=True)  # type: ignore[return-value]


class GLMAdapter:
    """GLM 5 Turbo 호출 어댑터 (ADR-0005).

    키/엔드포인트가 설정되지 않았으면 호출 시 즉시 실패한다.
    실제 HTTP 호출 구현은 키 확보 후 별도 커밋으로 채운다.
    """

    def __init__(self, api_key: str | None = None, api_base: str | None = None) -> None:
        self._api_key = api_key or settings.glm_api_key
        self._api_base = api_base or settings.glm_api_base

    def generate(self, schema: type[T], instruction: str, context: dict[str, object]) -> T:
        if not self._api_key or not self._api_base:
            raise NotImplementedError(
                "GLM API 미설정 — DEVCANVAS_GLM_API_KEY / DEVCANVAS_GLM_API_BASE 확인"
            )
        raise NotImplementedError("GLM HTTP 호출 구현은 키 확정 후 추가 예정 (ADR-0005)")
