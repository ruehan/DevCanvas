"""GLM 어댑터 실구현체 테스트 (ADR-0007, glm-5.2). http_post 주입으로 네트워크 없음."""

from __future__ import annotations

import json
from typing import Any

import pytest
from pydantic import BaseModel

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
    assert body["model"] == "glm-5.2"  # settings 기본 모델
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


def test_glm_adapter_without_key_raises() -> None:
    adapter = GLMAdapter(
        api_key=None, api_base="https://x", http_post=lambda *a, **k: _FakeResp({})
    )
    with pytest.raises(GenerationError):
        adapter.generate(_Schema, "x", {})
