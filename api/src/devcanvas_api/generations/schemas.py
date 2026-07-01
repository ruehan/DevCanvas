"""generations API 스키마."""

from __future__ import annotations

from pydantic import BaseModel, Field

from devcanvas_api.pipeline.schemas import (
    GenerationInput,
    GenerationResult,
    ScreenType,
    Tone,
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
