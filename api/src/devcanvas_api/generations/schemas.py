"""generations API 스키마."""

from __future__ import annotations

from pydantic import BaseModel, Field, field_validator

from devcanvas_api.pipeline.schemas import (
    GenerationInput,
    GenerationResult,
    ScreenType,
    Tone,
    _normalize_tone,
)


class GenerationRequest(BaseModel):
    """POST /generations 요청 바디."""

    prompt: str
    screen_type: ScreenType = ScreenType.DASHBOARD
    service_type: str = "SaaS"
    role: str = "관리자"
    data_fields: list[str] = Field(default_factory=list)
    tone: Tone = Tone.B2B
    stack: str = "Next.js + Tailwind + shadcn/ui"

    @field_validator("tone", mode="before")
    @classmethod
    def _normalize_request_tone(cls, v: object) -> object:
        # GenerationInput 과 동일 정규화 — API 진입점 계약 일치 (ADR-0008)
        return _normalize_tone(v)

    def to_generation_input(self) -> GenerationInput:
        return GenerationInput(
            prompt=self.prompt,
            screen_type=self.screen_type,
            service_type=self.service_type,
            role=self.role,
            data_fields=self.data_fields,
            tone=self.tone,
            stack=self.stack,
        )


class GenerationResponse(GenerationResult):
    """파이프라인 결과를 그대로 응답한다."""
