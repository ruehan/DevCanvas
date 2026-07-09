"""LLM 어댑터 포트와 구현체 (ADR-0005, ADR-0006, ADR-0007).

GLM 5.2 OpenAI 호환 chat completions 엔드포인트 사용. 구조화 출력은 JSON 응답을
Pydantic 스키마로 검증(ADR-0007). MVP 재시도 없음 — 검증 실패 시 예외.
"""

from __future__ import annotations

import json
import re
from collections.abc import Callable
from typing import Any, Protocol, TypeVar

import httpx
from pydantic import BaseModel, ValidationError

from devcanvas_api.core import settings
from devcanvas_api.pipeline import fixtures
from devcanvas_api.pipeline.schemas import (
    CodeGeneration,
    DesignSystem,
    GenerationResult,
    HandoffDoc,
    RequirementSpec,
    ReviewReport,
    UIGeneration,
    UXPlan,
)

T = TypeVar("T", bound=BaseModel)

HttpPost = Callable[..., Any]


class LLMAdapter(Protocol):
    """구조화 출력을 내는 LLM 어댑터 포트(ADR-0007)."""

    def generate(self, schema: type[T], instruction: str, context: dict[str, object]) -> T:
        """instruction/context 로 schema 인스턴스를 생성해 반환한다."""
        ...


class DummyLLMAdapter:
    """GLM 키 없이 파이프라인을 end-to-end 돌리기 위한 더미 어댑터."""

    _FIXTURES: dict[type[BaseModel], object] = {
        RequirementSpec: fixtures.requirement(),
        UXPlan: fixtures.ux_plan(),
        DesignSystem: fixtures.design_system(),
        UIGeneration: fixtures.ui_generation(),
        CodeGeneration: fixtures.code_generation(),
        ReviewReport: fixtures.review_report(),
        HandoffDoc: fixtures.handoff(),
        GenerationResult: fixtures.generation_result(),
    }

    def generate(self, schema: type[T], instruction: str, context: dict[str, object]) -> T:
        del instruction, context
        fixture = self._FIXTURES.get(schema)
        if fixture is None:
            raise NotImplementedError(f"DummyLLMAdapter: {schema.__name__} fixture 없음")
        assert isinstance(fixture, BaseModel)
        return fixture.model_copy(deep=True)  # type: ignore[return-value]


class GenerationError(RuntimeError):
    """GLM 응답 생성/검증 실패(ADR-0007)."""


def _build_prompt(schema: type[BaseModel], instruction: str, context: dict[str, object]) -> str:
    """스키마 + 지시 + 컨텍스트를 묶은 프롬프트. JSON 객체만 반환하도록 요구."""
    schema_desc = json.dumps(schema.model_json_schema(), ensure_ascii=False)
    context_desc = json.dumps(context, ensure_ascii=False, default=str)
    return (
        f"{instruction}\n\n"
        f"다음 JSON 스키마에 맞춰 한국어 값으로 응답하라. 반드시 JSON 객체만 반환한다.\n"
        f"스키마:\n{schema_desc}\n\n"
        f"컨텍스트:\n{context_desc}"
    )


_JSON_FENCE_RE = re.compile(r"```(?:json)?\s*(\{.*\})\s*```", re.DOTALL)


def _extract_json(content: str) -> dict[str, Any]:
    """응답 content 에서 JSON 객체를 추출. ```json``` 펜스/여분 텍스트 처리."""
    fenced = _JSON_FENCE_RE.search(content)
    raw = fenced.group(1) if fenced else content
    # JSON 객체 부분 추출(여분 텍스트가 섞였을 때 최초 { 부터 마지막 })
    start = raw.find("{")
    end = raw.rfind("}")
    if start == -1 or end == -1 or end < start:
        raise GenerationError(f"응답에서 JSON 객체를 찾지 못함: {content[:120]!r}")
    try:
        parsed: dict[str, Any] = json.loads(raw[start : end + 1])
    except json.JSONDecodeError as e:
        raise GenerationError(f"JSON 파싱 실패: {e}") from e
    return parsed


class GLMAdapter:
    """GLM 5.2 호출 어댑터(ADR-0007).

    OpenAI 호환 /chat/completions 엔드포인트. response_format json_object 요청,
    응답을 Pydantic 스키마로 검증. 검증 실패 시 GenerationError(재시도 없음, MVP).
    """

    def __init__(
        self,
        api_key: str | None = None,
        api_base: str | None = None,
        model: str | None = None,
        http_post: HttpPost | None = None,
    ) -> None:
        self._api_key = api_key if api_key is not None else settings.glm_api_key
        self._api_base = api_base or settings.glm_api_base
        self._model = model or settings.glm_model
        self._http_post = http_post or httpx.post

    def generate(self, schema: type[T], instruction: str, context: dict[str, object]) -> T:
        if not self._api_key:
            raise GenerationError(
                "GLM API 키 미설정 — DEVCANVAS_GLM_API_KEY 확인"
            )
        prompt = _build_prompt(schema, instruction, context)
        try:
            resp = self._http_post(
                f"{self._api_base}/chat/completions",
                json={
                    "model": self._model,
                    "messages": [{"role": "user", "content": prompt}],
                    "response_format": {"type": "json_object"},
                    "temperature": 0.2,
                },
                headers={"Authorization": f"Bearer {self._api_key}"},
                timeout=60,
            )
            resp.raise_for_status()
            content: str = resp.json()["choices"][0]["message"]["content"]
        except Exception as e:  # http/응답 접근 계열 오류
            raise GenerationError(f"GLM 호출 실패: {e}") from e

        data = _extract_json(content)
        try:
            return schema.model_validate(data)
        except ValidationError as e:
            raise GenerationError(f"GLM 응답 스키마 검증 실패({schema.__name__}): {e}") from e
