"""핸드오프 빌더 규칙 기반 테스트 (ADR-0016)."""

from __future__ import annotations

import pytest

from devcanvas_api.pipeline.code.generator import build_code_generation
from devcanvas_api.pipeline.handoff.builder import build_handoff
from devcanvas_api.pipeline.review.reviewer import run_review
from devcanvas_api.pipeline.schemas import (
    CodeGeneration,
    RequirementSpec,
    ReviewReport,
    ScreenType,
)
from devcanvas_api.pipeline.ui.generator import build_ui_generation
from devcanvas_api.pipeline.ux.planner import build_ux_plan


@pytest.fixture()
def generated() -> tuple[CodeGeneration, ReviewReport]:
    req = RequirementSpec(data_entities=["Customer"])
    ui = build_ui_generation(build_ux_plan(req, ScreenType.DASHBOARD))
    code = build_code_generation(ui)
    review = run_review(code)
    return code, review


def test_file_tree_reflects_code_paths(generated: tuple[CodeGeneration, ReviewReport]) -> None:
    code, _ = generated
    handoff = build_handoff(code, ReviewReport())
    expected = sorted(f.path for f in code.files)
    assert handoff.file_tree == expected


def test_install_commands_detect_known_deps(generated: tuple[CodeGeneration, ReviewReport]) -> None:
    code, _ = generated
    handoff = build_handoff(code, ReviewReport())
    joined = " ".join(handoff.install_commands)
    # Chart→recharts, DataTable→@tanstack/react-table, Tabs→@radix-ui/react-tabs
    assert "recharts" in joined
    assert "@tanstack/react-table" in joined
    assert "@radix-ui/react-tabs" in joined


def test_todos_include_review_p1(generated: tuple[CodeGeneration, ReviewReport]) -> None:
    code, review = generated
    handoff = build_handoff(code, review)
    # review 에 state P1 finding 이 있으므로 todos 에 반영
    assert any("구현 필요" in t for t in handoff.todos)


def test_todos_include_standard_items(generated: tuple[CodeGeneration, ReviewReport]) -> None:
    code, _ = generated
    handoff = build_handoff(code, ReviewReport())
    joined = " ".join(handoff.todos)
    # 컴포넌트 스텁 TODO + mock 데이터 교체 표준 항목
    assert "컴포넌트" in joined or "구현" in joined


def test_guide_md_documents_structure(generated: tuple[CodeGeneration, ReviewReport]) -> None:
    code, review = generated
    handoff = build_handoff(code, review)
    assert handoff.guide_md.startswith("# ")
    # 파일 트리의 일부 경로가 가이드에 등장
    assert code.files[0].path in handoff.guide_md or any(
        f.path in handoff.guide_md for f in code.files
    )


def test_empty_code_yields_minimal_handoff() -> None:
    handoff = build_handoff(CodeGeneration(files=[]), ReviewReport())
    assert handoff.file_tree == []
    assert handoff.install_commands == []
    assert handoff.guide_md.startswith("# ")
