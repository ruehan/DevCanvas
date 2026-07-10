"""파이프라인 단계별 입출력 스키마."""

from __future__ import annotations

from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, Field, field_validator

# ---------- 입력 ----------


class Tone(StrEnum):
    """디자인 톤 — 소문자 정규화(ADR-0008)."""

    B2B = "b2b"
    MINIMAL = "minimal"
    ENTERPRISE = "enterprise"
    STARTUP = "startup"
    FRIENDLY = "friendly"


class ScreenType(StrEnum):
    """MVP 지원 화면 유형 (ADR-0002)."""

    ADMIN = "admin"
    DASHBOARD = "dashboard"
    INTERNAL_TOOL = "internal_tool"


def _normalize_tone(v: object) -> object:
    """tone 대소문자 무관 정규화("B2B"/"b2b"/"Startup" → 소문자 값). 공통 validator."""
    if isinstance(v, str) and not isinstance(v, Tone):
        return v.lower()
    return v


class GenerationInput(BaseModel):
    """사용자 생성 요청 입력."""

    prompt: str
    screen_type: ScreenType = ScreenType.DASHBOARD
    service_type: str = "SaaS"
    role: str = "관리자"
    data_fields: list[str] = Field(default_factory=list)
    tone: Tone = Tone.B2B
    stack: str = "Next.js + Tailwind + shadcn/ui"

    @field_validator("tone", mode="before")
    @classmethod
    def _normalize_input_tone(cls, v: object) -> object:
        return _normalize_tone(v)


# ---------- 1단계: 요구사항 ----------


class RequirementSpec(BaseModel):
    features: list[str] = Field(default_factory=list)
    users: list[str] = Field(default_factory=list)
    screens: list[str] = Field(default_factory=list)
    data_entities: list[str] = Field(default_factory=list)


# ---------- 2단계: UX 설계 ----------


class ScreenKind(StrEnum):
    """화면 종류 — 종류별 컴포넌트·상태 템플릿 적용 (ADR-0010)."""

    LIST = "list"
    DETAIL = "detail"
    DASHBOARD = "dashboard"


class ScreenSpec(BaseModel):
    name: str
    purpose: str
    kind: ScreenKind = ScreenKind.LIST
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
    kind: ScreenKind = ScreenKind.LIST
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


class GenerationResultPatch(BaseModel):
    """편집 턴 부분 수정 패치 (ADR-0023).

    전체 재생성 대신 LLM 이 '바뀐 최상위 섹션만' 반환한다. 모든 필드 Optional —
    제공된(non-None) 필드만 기존 GenerationResult 를 덮어쓴다(최상위 교체 병합).
    `input` 은 편집으로 바뀌지 않으므로 패치 대상에서 제외한다.
    """

    requirement: RequirementSpec | None = None
    ux_plan: UXPlan | None = None
    design_system: DesignSystem | None = None
    ui: UIGeneration | None = None
    code: list[CodeFile] | None = None
    review: list[ReviewFinding] | None = None
    handoff: HandoffDoc | None = None


# ---------- 5단계 LLM 산출 (ADR-0024): 페이지 골격 ----------


class PageSkel(BaseModel):
    """LLM 이 생성하는 페이지 골격 (ADR-0024).

    path 는 우리 템플릿이 계산한 경로와 정확히 일치해야 한다(스키마 자체로는 강제 안 함 —
    code_generator_agent 가 검증 후 채택). content 는 tsx 본문.
    """

    path: str
    content: str


class CodeSkel(BaseModel):
    """LLM 이 반환하는 page.tsx 골격 컨테이너 (ADR-0024).

    code_generator_agent 가 layouts 를 순회하며 우리 path 와 매칭해 content 를 채택한다.
    매칭 안 되면 templates.page_code() 로 graceful fallback.
    """

    pages: list[PageSkel] = Field(default_factory=list)
