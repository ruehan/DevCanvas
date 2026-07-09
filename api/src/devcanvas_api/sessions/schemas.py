"""세션 스키마 (ADR-0017)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from enum import StrEnum

from pydantic import BaseModel, Field

from devcanvas_api.pipeline.schemas import GenerationResult


class MessageRole(StrEnum):
    USER = "user"
    AGENT = "agent"


class Message(BaseModel):
    role: MessageRole
    content: str
    steps: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class Session(BaseModel):
    id: str = Field(default_factory=lambda: uuid.uuid4().hex)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    messages: list[Message] = Field(default_factory=list)
    current_result: GenerationResult | None = None


class CreateSessionResponse(BaseModel):
    id: str


class PostMessageRequest(BaseModel):
    prompt: str


class PostMessageResponse(BaseModel):
    """편집/생성 후 갱신된 결과와 에이전트 메시지."""

    agent_message: Message
    result: GenerationResult
    session_id: str
