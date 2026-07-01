"""generations API 스키마 계약 테스트."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from devcanvas_api.generations.schemas import GenerationRequest


@pytest.mark.parametrize("raw", ["B2B", "b2b", "Startup", "STARTUP", "Friendly"])
def test_request_tone_is_case_insensitive(raw: str) -> None:
    req = GenerationRequest(prompt="x", tone=raw)  # type: ignore[arg-type]
    assert req.tone.value == raw.lower()


def test_request_rejects_truly_unknown_tone() -> None:
    # 정규화 후에도 Tone 값이 아니면 거부
    with pytest.raises(ValidationError):
        GenerationRequest(prompt="x", tone="우주인")  # type: ignore[arg-type]
