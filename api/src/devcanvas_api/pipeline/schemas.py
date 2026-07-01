"""파이프라인 단계별 입출력 스키마."""

from __future__ import annotations

from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, Field

# ---------- 입력 ----------


class ScreenType(StrEnum):
    """MVP 지원 화면 유형 (ADR-0002)."""

    ADMIN = "admin"
    DASHBOARD = "dashboard"
    INTERNAL_TOOL = "internal_tool"


class GenerationInput(BaseModel):
    """사용자 생성 요청 입력."""

    prompt: str
    screen_type: ScreenType = ScreenType.DASHBOARD
    service_type: str = "SaaS"
    role: str = "관리자"
    data_fields: list[str] = Field(default_factory=list)
    tone: str = "B2B"
    stack: str = "Next.js + Tailwind + shadcn/ui"


# ---------- 1단계: 요구사항 ----------


class RequirementSpec(BaseModel):
    features: list[str] = Field(default_factory=list)
    users: list[str] = Field(default_factory=list)
    screens: list[str] = Field(default_factory=list)
    data_entities: list[str] = Field(default_factory=list)


# ---------- 2단계: UX 설계 ----------


class ScreenSpec(BaseModel):
    name: str
    purpose: str
    components: list[str] = Field(default_factory=list)
    data_columns: list[str] = Field(default_factory=list)
    filters: list[str] = Field(default_factory=list)
    actions: list[str] = Field(default_factory=list)


class ScreenState(BaseModel):
    """화면 상태 매트릭스 항목 (State Matrix)."""

    loading: str = "skeleton"
    empty: str = "안내 문구 + CTA"
    error: str = "재시도 버튼 + 오류 메시지"
    permission: str = "권한 요청 안내"
    mobile: str = "카드형 리스트 전환"


class UXPlan(BaseModel):
    screens: list[ScreenSpec] = Field(default_factory=list)
    flows: list[str] = Field(default_factory=list)
    states: dict[str, ScreenState] = Field(default_factory=dict)


# ---------- 3단계: 디자인 시스템 ----------


class DesignTokens(BaseModel):
    colors: dict[str, str] = Field(default_factory=dict)
    spacing: dict[str, str] = Field(default_factory=dict)
    radius: dict[str, str] = Field(default_factory=dict)
    typography: dict[str, str] = Field(default_factory=dict)
    shadows: dict[str, str] = Field(default_factory=dict)


class DesignSystem(BaseModel):
    tokens: DesignTokens = Field(default_factory=DesignTokens)


# ---------- 4단계: UI 생성 ----------


class ScreenLayout(BaseModel):
    screen: str
    layout: str
    component_tree: list[str] = Field(default_factory=list)


class UIGeneration(BaseModel):
    layouts: list[ScreenLayout] = Field(default_factory=list)


# ---------- 5단계: 코드 생성 ----------


class CodeFile(BaseModel):
    path: str
    content: str
    language: Literal["tsx", "ts", "css", "json", "md"] = "tsx"


class CodeGeneration(BaseModel):
    files: list[CodeFile] = Field(default_factory=list)


# ---------- 6단계: 리뷰 ----------


class ReviewSeverity(StrEnum):
    P1 = "P1"
    P2 = "P2"


class ReviewFinding(BaseModel):
    severity: ReviewSeverity = ReviewSeverity.P2
    category: str
    message: str


class ReviewReport(BaseModel):
    findings: list[ReviewFinding] = Field(default_factory=list)


# ---------- 7단계: 핸드오프 ----------


class HandoffDoc(BaseModel):
    file_tree: list[str] = Field(default_factory=list)
    install_commands: list[str] = Field(default_factory=list)
    todos: list[str] = Field(default_factory=list)
    guide_md: str = ""


# ---------- 통합 결과 ----------


class GenerationResult(BaseModel):
    input: GenerationInput
    requirement: RequirementSpec = Field(default_factory=RequirementSpec)
    ux_plan: UXPlan = Field(default_factory=UXPlan)
    design_system: DesignSystem = Field(default_factory=DesignSystem)
    ui: UIGeneration = Field(default_factory=UIGeneration)
    code: list[CodeFile] = Field(default_factory=list)
    review: list[ReviewFinding] = Field(default_factory=list)
    handoff: HandoffDoc = Field(default_factory=HandoffDoc)
