"""GLM 어댑터 실구현체 테스트 (ADR-0007, glm-5.2). http_post 주입으로 네트워크 없음."""

from __future__ import annotations

import json
from typing import Any

import httpx
import pytest
from pydantic import BaseModel

from devcanvas_api.core import settings
from devcanvas_api.pipeline.llm import GenerationError, GLMAdapter


class _Schema(BaseModel):
    title: str
    items: list[str]


class _FakeResp:
    def __init__(self, payload: dict[str, Any], status: int = 200) -> None:
        self._payload = payload
        self.status_code = status

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise RuntimeError(f"http {self.status_code}")

    def json(self) -> dict[str, Any]:
        return self._payload


def _glm_response(content: str) -> _FakeResp:
    """GLM chat completions 응답 형태."""
    return _FakeResp({"choices": [{"message": {"content": content}}]})


def _make_adapter(captured: dict[str, Any], content: str, *, key: str = "k") -> GLMAdapter:
    def fake_post(url: str, **kwargs: Any) -> _FakeResp:
        captured["url"] = url
        captured["kwargs"] = kwargs
        return _glm_response(content)

    return GLMAdapter(api_key=key, api_base="https://glm.example/api/paas/v4", http_post=fake_post)


def test_glm_generate_returns_validated_schema() -> None:
    captured: dict[str, Any] = {}
    adapter = _make_adapter(captured, json.dumps({"title": "고객", "items": ["a", "b"]}))
    result = adapter.generate(_Schema, "요구사항을 분석하라", {"prompt": "고객 관리"})
    assert isinstance(result, _Schema)
    assert result.title == "고객"
    assert result.items == ["a", "b"]


def test_glm_generate_sends_chat_completion_request() -> None:
    captured: dict[str, Any] = {}
    adapter = _make_adapter(captured, json.dumps({"title": "x", "items": []}))
    adapter.generate(_Schema, "instruction", {"prompt": "p"})
    assert captured["url"].endswith("/chat/completions")
    body = captured["kwargs"]["json"]
    assert body["model"] == settings.glm_model  # settings 설정 모델(.env 무관 검증)
    assert body["messages"][0]["content"]  # 프롬프트 채워짐
    assert captured["kwargs"]["headers"]["Authorization"].startswith("Bearer ")


def test_glm_generate_includes_schema_and_context_in_prompt() -> None:
    captured: dict[str, Any] = {}
    adapter = _make_adapter(captured, json.dumps({"title": "x", "items": []}))
    adapter.generate(_Schema, "화면을 생성하라", {"prompt": "고객 목록", "tone": "b2b"})
    content = captured["kwargs"]["json"]["messages"][0]["content"]
    assert "화면을 생성하라" in content  # instruction
    assert "고객 목록" in content  # context
    assert "title" in content  # 스키마 키


def test_glm_generate_omits_schema_when_include_schema_false() -> None:
    # 편집 턴(ADR-0022): formal JSON 스키마를 프롬프트에서 생략, context 는 유지
    captured: dict[str, Any] = {}
    adapter = _make_adapter(captured, json.dumps({"title": "x", "items": []}))
    adapter.generate(
        _Schema, "결과를 수정하라", {"current_result": {"title": "old"}}, include_schema=False
    )
    content = captured["kwargs"]["json"]["messages"][0]["content"]
    assert "결과를 수정하라" in content  # instruction 유지
    assert "current_result" in content  # context 유지
    assert "동일한 JSON 구조" in content  # 스키마 대체 지시
    assert "$defs" not in content and "properties" not in content  # formal 스키마 미포함


def test_glm_generate_raises_on_invalid_json() -> None:
    adapter = _make_adapter({}, "이건 JSON이 아님")
    with pytest.raises(GenerationError):  # JSON 파싱/검증 실패
        adapter.generate(_Schema, "x", {})


def test_glm_generate_raises_on_schema_violation() -> None:
    # items 가 스키마상 list 인데 문자열로 옴
    adapter = _make_adapter({}, json.dumps({"title": "x", "items": "not-a-list"}))
    with pytest.raises(GenerationError):
        adapter.generate(_Schema, "x", {})


def test_glm_generate_raises_on_http_error() -> None:
    def post(url: str, **kwargs: Any) -> _FakeResp:
        return _FakeResp({}, status=500)

    adapter = GLMAdapter(
        api_key="k", api_base="https://glm.example/api/paas/v4", http_post=post
    )
    with pytest.raises(GenerationError):
        adapter.generate(_Schema, "x", {})


def test_glm_generate_strips_markdown_fences() -> None:
    # GLM 이 ```json ... ``` 로 감싸는 경우
    fenced = "```json\n" + json.dumps({"title": "x", "items": []}) + "\n```"
    adapter = _make_adapter({}, fenced)
    result = adapter.generate(_Schema, "x", {})
    assert result.title == "x"


def test_glm_generate_handles_surrounding_prose() -> None:
    # JSON 앞뒤로 평문이 섞인 경우 (회귀망 — _extract_json rfind 로직)
    obj = json.dumps({"title": "고객", "items": ["a"]}, ensure_ascii=False)
    content = f"설명입니다.\n{obj}\n끝."
    adapter = _make_adapter({}, content)
    result = adapter.generate(_Schema, "x", {})
    assert result.title == "고객"
    assert result.items == ["a"]


def test_glm_adapter_without_key_raises() -> None:
    adapter = GLMAdapter(
        api_key=None, api_base="https://x", http_post=lambda *a, **k: _FakeResp({})
    )
    with pytest.raises(GenerationError):
        adapter.generate(_Schema, "x", {})


# ---------- 전송 계층 재시도 (ADR-0007) ----------


def _http_status_error(status: int) -> httpx.HTTPStatusError:
    """raise_for_status 가 낼 법한 httpx.HTTPStatusError 를 만든다."""
    req = httpx.Request("POST", "https://glm.example/api/paas/v4/chat/completions")
    resp = httpx.Response(status, request=req)
    return httpx.HTTPStatusError(f"http {status}", request=req, response=resp)


class _SeqPost:
    """호출 순서대로 정해진 동작을 수행하는 fake http_post. 예외는 raise, resp 는 반환."""

    def __init__(self, actions: list[_FakeResp | BaseException]) -> None:
        self._actions = actions
        self.calls = 0

    def __call__(self, url: str, **kwargs: Any) -> _FakeResp:
        action = self._actions[self.calls]
        self.calls += 1
        if isinstance(action, BaseException):
            raise action
        return action


def _ok() -> _FakeResp:
    return _glm_response(json.dumps({"title": "x", "items": []}))


def _adapter_with(post: Any, sleeps: list[float], **kw: Any) -> GLMAdapter:
    return GLMAdapter(
        api_key="k",
        api_base="https://glm.example/api/paas/v4",
        http_post=post,
        retry_base_delay=1.0,
        sleep=sleeps.append,
        **kw,
    )


def test_glm_retries_on_timeout_then_succeeds() -> None:
    post = _SeqPost([httpx.ReadTimeout("read timed out"), _ok()])
    sleeps: list[float] = []
    adapter = _adapter_with(post, sleeps, max_retries=2)
    result = adapter.generate(_Schema, "x", {})
    assert result.title == "x"
    assert post.calls == 2  # 1 실패 + 1 성공
    assert sleeps == [1.0]  # base * 2**0


def test_glm_retries_on_429_then_succeeds() -> None:
    resp = _FakeResp({}, status=429)
    # raise_for_status 가 httpx.HTTPStatusError(429) 를 내도록 교체
    resp.raise_for_status = lambda: (_ for _ in ()).throw(_http_status_error(429))  # type: ignore[method-assign]
    post = _SeqPost([resp, _ok()])
    sleeps: list[float] = []
    adapter = _adapter_with(post, sleeps, max_retries=2)
    result = adapter.generate(_Schema, "x", {})
    assert result.title == "x"
    assert post.calls == 2


def test_glm_gives_up_after_max_retries() -> None:
    post = _SeqPost([httpx.ReadTimeout("t")] * 3)  # 항상 타임아웃
    sleeps: list[float] = []
    adapter = _adapter_with(post, sleeps, max_retries=2)
    with pytest.raises(GenerationError):
        adapter.generate(_Schema, "x", {})
    assert post.calls == 3  # 1 + max_retries
    assert sleeps == [1.0, 2.0]  # 지수 백오프


def test_glm_does_not_retry_schema_violation() -> None:
    # 응답은 정상 도착(200)이나 스키마 위반 — 재호출해도 결정적 반복 → 재시도 금지
    bad = _glm_response(json.dumps({"title": "x", "items": "not-a-list"}))
    post = _SeqPost([bad, _ok()])
    sleeps: list[float] = []
    adapter = _adapter_with(post, sleeps, max_retries=2)
    with pytest.raises(GenerationError):
        adapter.generate(_Schema, "x", {})
    assert post.calls == 1  # 재시도 없음
    assert sleeps == []
