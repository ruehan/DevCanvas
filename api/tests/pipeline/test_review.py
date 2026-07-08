"""리뷰 체크 규칙 기반 테스트 (ADR-0013)."""

from __future__ import annotations

import pytest

from devcanvas_api.pipeline.code.generator import build_code_generation
from devcanvas_api.pipeline.review.reviewer import run_review
from devcanvas_api.pipeline.schemas import (
    CodeFile,
    CodeGeneration,
    RequirementSpec,
    ScreenType,
)
from devcanvas_api.pipeline.ui.generator import build_ui_generation
from devcanvas_api.pipeline.ux.planner import build_ux_plan


@pytest.fixture()
def generated_code() -> CodeGeneration:
    req = RequirementSpec(data_entities=["Customer"])
    ui = build_ui_generation(build_ux_plan(req, ScreenType.DASHBOARD))
    return build_code_generation(ui)


# ---------- 집계 ----------


def test_review_returns_findings(generated_code: CodeGeneration) -> None:
    report = run_review(generated_code)
    assert report.findings  # 생성 코드엔 TODO/mock 등 리뷰 대상이 있음


def test_review_finds_state_todo(generated_code: CodeGeneration) -> None:
    # 생성된 page.tsx 는 상태 분기를 TODO 로 남김 → P1
    report = run_review(generated_code)
    state_findings = [f for f in report.findings if f.category == "state"]
    assert state_findings
    assert any(f.severity.value == "P1" for f in state_findings)


def test_review_finds_component_stubs_todo(generated_code: CodeGeneration) -> None:
    report = run_review(generated_code)
    comp_findings = [f for f in report.findings if f.category == "component"]
    assert comp_findings


def test_review_finds_mock_usage(generated_code: CodeGeneration) -> None:
    report = run_review(generated_code)
    data_findings = [f for f in report.findings if f.category == "data"]
    assert data_findings


# ---------- 개별 체크 ----------


def test_any_type_detected() -> None:
    code = CodeGeneration(
        files=[
            CodeFile(path="app/x/page.tsx", language="tsx", content="const x: any = 1;\n")
        ]
    )
    report = run_review(code)
    assert any(f.category == "types" and "any" in f.message for f in report.findings)


def test_any_type_as_any_detected() -> None:
    # `as any` 형태도 잡아야 (리뷰 P2)
    code = CodeGeneration(
        files=[
            CodeFile(
                path="app/x/page.tsx", language="tsx", content="const x = data as any;\n"
            )
        ]
    )
    report = run_review(code)
    assert any(f.category == "types" for f in report.findings)


def test_state_missing_entirely_detected() -> None:
    # check_state 분기 (a): 상태 키워드가 아예 없음 → P1 (리뷰 P2)
    code = CodeGeneration(
        files=[
            CodeFile(
                path="app/x/page.tsx",
                language="tsx",
                content="export default function P(){return <div>hello</div>;}\n",
            )
        ]
    )
    report = run_review(code)
    state = [f for f in report.findings if f.category == "state"]
    assert state
    assert "전혀 없음" in state[0].message


def test_checks_skip_non_target_paths() -> None:
    # non-page 파일은 state/a11y/mock 체크 대상 아님; non-components 는 component 체크 대상 아님
    code = CodeGeneration(
        files=[
            CodeFile(path="lib/util.ts", language="ts", content="export const x = 1;\n")
        ]
    )
    report = run_review(code)
    categories = {f.category for f in report.findings}
    assert "state" not in categories
    assert "a11y" not in categories
    assert "component" not in categories
    assert "data" not in categories


def test_a11y_missing_aria_flagged() -> None:
    code = CodeGeneration(
        files=[
            CodeFile(
                path="app/x/page.tsx",
                language="tsx",
                content="export default function P(){return <div>x</div>;}\n",
            )
        ]
    )
    report = run_review(code)
    assert any(f.category == "a11y" for f in report.findings)


def test_a11y_present_not_flagged() -> None:
    code = CodeGeneration(
        files=[
            CodeFile(
                path="app/x/page.tsx",
                language="tsx",
                content='export default function P(){return <div aria-label="x">x</div>;}\n',
            )
        ]
    )
    report = run_review(code)
    assert not any(f.category == "a11y" for f in report.findings)


def test_empty_code_yields_no_findings() -> None:
    report = run_review(CodeGeneration(files=[]))
    assert report.findings == []
