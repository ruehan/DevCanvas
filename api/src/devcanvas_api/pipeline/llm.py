"""LLM 어댑터 포트와 구현체 (ADR-0005, ADR-0006, ADR-0007).

GLM 5.2 OpenAI 호환 chat completions 엔드포인트 사용. 구조화 출력은 JSON 응답을
Pydantic 스키마로 검증(ADR-0007). MVP 재시도 없음 — 검증 실패 시 예외.
"""

from __future__ import annotations

import json
import re
import time
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
Sleep = Callable[[float], None]

# 재시도 대상 HTTP 상태(일시적 오류). 429=레이트리밋, 5xx=서버측 일시 오류.
_RETRYABLE_STATUS = frozenset({429, 500, 502, 503, 504})


def _is_transient(exc: BaseException) -> bool:
    """전송 계층 일시 오류인지 판별(재시도 대상). 타임아웃·네트워크·429/5xx."""
    if isinstance(exc, httpx.TimeoutException | httpx.TransportError):
        return True
    if isinstance(exc, httpx.HTTPStatusError):
        return exc.response.status_code in _RETRYABLE_STATUS
    return False


class LLMAdapter(Protocol):
    """구조화 출력을 내는 LLM 어댑터 포트(ADR-0007)."""

    def generate(
        self,
        schema: type[T],
        instruction: str,
        context: dict[str, object],
        *,
        include_schema: bool = True,
    ) -> T:
        """instruction/context 로 schema 인스턴스를 생성해 반환한다.

        include_schema=False 면 프롬프트에 formal JSON 스키마를 넣지 않는다(ADR-0022):
        context 가 이미 대상 스키마의 완전한 인스턴스를 담은 편집 턴에서 중복 제거·토큰 절감.
        """
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

    def generate(
        self,
        schema: type[T],
        instruction: str,
        context: dict[str, object],
        *,
        include_schema: bool = True,
    ) -> T:
        del instruction, context, include_schema
        fixture = self._FIXTURES.get(schema)
        if fixture is None:
            raise NotImplementedError(f"DummyLLMAdapter: {schema.__name__} fixture 없음")
        assert isinstance(fixture, BaseModel)
        return fixture.model_copy(deep=True)  # type: ignore[return-value]


class GenerationError(RuntimeError):
    """GLM 응답 생성/검증 실패(ADR-0007)."""


def _build_prompt(
    schema: type[BaseModel],
    instruction: str,
    context: dict[str, object],
    *,
    include_schema: bool = True,
) -> str:
    """스키마 + 지시 + 컨텍스트를 묶은 프롬프트. JSON 객체만 반환하도록 요구.

    include_schema=False 면 formal JSON 스키마 블록을 생략한다(ADR-0022). context 가 이미
    대상 스키마의 완전한 인스턴스를 담은 편집 턴에서 스키마가 중복이므로, 그 인스턴스와
    "동일한 구조"를 유지하라고 지시하는 것으로 대체 — 토큰(관측상 payload 의 ~68%) 절감.
    """
    context_desc = json.dumps(context, ensure_ascii=False, default=str)
    if not include_schema:
        return (
            f"{instruction}\n\n"
            f"반드시 JSON 객체만 반환한다. 컨텍스트의 기존 결과와 완전히 동일한 JSON 구조"
            f"(같은 키·중첩)를 유지한 채 지시에 해당하는 부분만 수정하라.\n"
            f"컨텍스트:\n{context_desc}"
        )
    schema_desc = json.dumps(schema.model_json_schema(), ensure_ascii=False)
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
        timeout: float | None = None,
        max_retries: int | None = None,
        retry_base_delay: float | None = None,
        sleep: Sleep | None = None,
    ) -> None:
        self._api_key = api_key if api_key is not None else settings.glm_api_key
        self._api_base = api_base or settings.glm_api_base
        self._model = model or settings.glm_model
        self._http_post = http_post or httpx.post
        self._timeout = timeout if timeout is not None else settings.glm_timeout
        raw_retries = max_retries if max_retries is not None else settings.glm_max_retries
        self._max_retries = max(0, raw_retries)  # 음수는 무의미 → 재시도 없음(0)
        self._retry_base_delay = (
            retry_base_delay if retry_base_delay is not None else settings.glm_retry_base_delay
        )
        self._sleep = sleep or time.sleep

    def _fetch_content(self, prompt: str) -> str:
        """chat completions 호출 → content 반환. transient http 오류는 지수 백오프 재시도.

        재시도 대상은 전송 계층 일시 오류(429/timeout/5xx)뿐(ADR-0007). 응답이 와서
        JSON/스키마가 틀린 경우는 재호출해도 결정적으로 반복되므로 재시도하지 않는다.
        """
        last_exc: Exception | None = None
        for attempt in range(self._max_retries + 1):
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
                    timeout=self._timeout,
                )
                resp.raise_for_status()
                content: str = resp.json()["choices"][0]["message"]["content"]
                return content
            except Exception as e:  # http/응답 접근 계열 오류
                last_exc = e
                if _is_transient(e) and attempt < self._max_retries:
                    self._sleep(self._retry_base_delay * (2**attempt))
                    continue
                raise GenerationError(f"GLM 호출 실패: {e}") from e
        # 도달 불가(루프는 반환 또는 raise 로 종료) — 타입 완결성용
        raise GenerationError(f"GLM 호출 실패: {last_exc}")

    def generate(
        self,
        schema: type[T],
        instruction: str,
        context: dict[str, object],
        *,
        include_schema: bool = True,
    ) -> T:
        if not self._api_key:
            raise GenerationError(
                "GLM API 키 미설정 — DEVCANVAS_GLM_API_KEY 확인"
            )
        prompt = _build_prompt(schema, instruction, context, include_schema=include_schema)
        content = self._fetch_content(prompt)

        data = _extract_json(content)
        try:
            return schema.model_validate(data)
        except ValidationError as e:
            raise GenerationError(f"GLM 응답 스키마 검증 실패({schema.__name__}): {e}") from e
