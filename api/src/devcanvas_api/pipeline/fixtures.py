"""DummyLLMAdapter용 결정적 fixture.

더미이지만 ADR-0002 MVP 도메인(관리자/대시보드/내부툴)에 맞춘 그럴듯한 데이터를 제공하여
파이프라인 전 단계가 의미 있게 연결되는지 검증한다.
"""

from __future__ import annotations

from devcanvas_api.pipeline.schemas import (
    CodeFile,
    CodeGeneration,
    DesignSystem,
    DesignTokens,
    HandoffDoc,
    RequirementSpec,
    ReviewFinding,
    ReviewReport,
    ReviewSeverity,
    ScreenKind,
    ScreenLayout,
    ScreenSpec,
    ScreenState,
    UIGeneration,
    UXPlan,
)


def requirement() -> RequirementSpec:
    return RequirementSpec(
        features=["고객 목록 조회", "결제 상태 필터", "계약 만료일 확인", "고객 상세 보기"],
        users=["관리자", "매니저"],
        screens=["고객 목록", "고객 상세"],
        data_entities=["Customer", "Contract", "Payment"],
    )


def ux_plan() -> UXPlan:
    screens = [
        ScreenSpec(
            name="고객 목록",
            purpose="고객 현황을 표 형태로 조회·필터링",
            kind=ScreenKind.LIST,
            components=["DataTable", "SearchInput", "FilterBar", "StatusBadge"],
            data_columns=["고객명", "결제 상태", "계약일"],
            filters=["결제 상태", "계약 만료 임박"],
            actions=["고객 상세 보기", "내보내기"],
        ),
        ScreenSpec(
            name="고객 상세",
            purpose="단일 고객 정보와 계약/결제 이력",
            kind=ScreenKind.DETAIL,
            components=["Card", "Tabs", "PaymentHistory", "EmptyState"],
            data_columns=["결제일", "금액", "상태"],
            filters=[],
            actions=["계약 갱신", "메모 저장"],
        ),
    ]
    states = {s.name: ScreenState() for s in screens}
    return UXPlan(
        screens=screens,
        flows=["로그인 → 고객 목록 → 고객 상세 → 계약 갱신"],
        states=states,
    )


def design_system() -> DesignSystem:
    return DesignSystem(
        tokens=DesignTokens(
            colors={
                "primary": "#2563EB",
                "background": "#F8FAFC",
                "text": "#0F172A",
                "danger": "#DC2626",
            },
            spacing={"xs": "4px", "sm": "8px", "md": "16px", "lg": "24px", "xl": "32px"},
            radius={"sm": "6px", "md": "10px", "lg": "16px"},
            typography={"body": "14px", "heading": "20px"},
            shadows={"sm": "0 1px 2px rgba(0,0,0,0.06)", "md": "0 4px 12px rgba(0,0,0,0.08)"},
        )
    )


def ui_generation() -> UIGeneration:
    return UIGeneration(
        layouts=[
            ScreenLayout(
                screen="고객 목록",
                layout="FilterBar(검색·필터) 상단 → DataTable 본문 → Pagination 하단",
                kind=ScreenKind.LIST,
                component_tree=["FilterBar", "DataTable", "Pagination"],
            ),
            ScreenLayout(
                screen="고객 상세",
                layout="Card(제목·액션) 상단 → Tabs(이력·메모) 본문",
                kind=ScreenKind.DETAIL,
                component_tree=["Card", "Tabs"],
            ),
        ]
    )


def code_generation() -> CodeGeneration:
    return CodeGeneration(files=code_files())


def code_files() -> list[CodeFile]:
    return [
        CodeFile(
            path="app/customers/page.tsx",
            language="tsx",
            content="'use client';\n// 고객 목록 페이지 (생성 뼈대)\n",
        ),
        CodeFile(
            path="components/customers/customer-table.tsx",
            language="tsx",
            content="'use client';\n// 고객 테이블 (생성 뼈대)\n",
        ),
        CodeFile(
            path="lib/types.ts",
            language="ts",
            content="export interface Customer { id: string; name: string; }\n",
        ),
    ]


def review_report() -> ReviewReport:
    return ReviewReport(findings=review_findings())


def review_findings() -> list[ReviewFinding]:
    return [
        ReviewFinding(
            severity=ReviewSeverity.P1, category="state", message="빈 상태 누락 검토 필요"
        ),
        ReviewFinding(
            severity=ReviewSeverity.P2, category="a11y", message="테이블 aria-label 권장"
        ),
    ]


def handoff() -> HandoffDoc:
    return HandoffDoc(
        file_tree=[
            "app/customers/page.tsx",
            "components/customers/customer-table.tsx",
            "lib/types.ts",
        ],
        install_commands=["pnpm add @radix-ui/react-tabs"],
        todos=["mock 데이터를 실제 API로 교체", "권한별 분기 추가"],
        guide_md="# 고객 관리 페이지 구현 가이드\n(생성 뼈대)",
    )
