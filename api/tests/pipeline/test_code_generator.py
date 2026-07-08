"""코드 생성기 규칙 기반 테스트 (ADR-0012)."""

from __future__ import annotations

import re

import pytest

from devcanvas_api.pipeline.code.generator import build_code_generation
from devcanvas_api.pipeline.schemas import (
    RequirementSpec,
    ScreenType,
    UIGeneration,
)
from devcanvas_api.pipeline.ui.generator import build_ui_generation
from devcanvas_api.pipeline.ux.planner import build_ux_plan


@pytest.fixture()
def dashboard_ui() -> UIGeneration:
    req = RequirementSpec(data_entities=["Customer", "Contract"])
    plan = build_ux_plan(req, ScreenType.DASHBOARD)
    return build_ui_generation(plan)


@pytest.fixture()
def admin_ui() -> UIGeneration:
    req = RequirementSpec(data_entities=["Customer"])
    return build_ui_generation(build_ux_plan(req, ScreenType.ADMIN))


# ---------- 파일 구조 ----------


def test_generates_page_per_screen(dashboard_ui: UIGeneration) -> None:
    gen = build_code_generation(dashboard_ui)
    page_files = [f for f in gen.files if f.path.startswith("app/") and f.path.endswith("page.tsx")]
    # 화면 수만큼 page.tsx (대시보드 + 고객 list/detail + 계약 list/detail = 5)
    assert len(page_files) == len(dashboard_ui.layouts)


def test_generates_types_and_mock(dashboard_ui: UIGeneration) -> None:
    gen = build_code_generation(dashboard_ui)
    paths = {f.path for f in gen.files}
    assert "lib/types.ts" in paths
    assert "lib/mock-data.ts" in paths


def test_dashboard_page_path(dashboard_ui: UIGeneration) -> None:
    gen = build_code_generation(dashboard_ui)
    paths = {f.path for f in gen.files}
    assert "app/dashboard/page.tsx" in paths


def test_list_detail_paths_use_slug(admin_ui: UIGeneration) -> None:
    gen = build_code_generation(admin_ui)
    paths = {f.path for f in gen.files}
    # 고객 → customer. list: app/customer/page.tsx, detail: app/customer/[id]/page.tsx
    assert "app/customer/page.tsx" in paths
    assert "app/customer/[id]/page.tsx" in paths


def test_component_stubs_generated(dashboard_ui: UIGeneration) -> None:
    gen = build_code_generation(dashboard_ui)
    comp_files = [f for f in gen.files if f.path.startswith("components/")]
    assert comp_files  # 컴포넌트 스텁 존재


# ---------- 정합 규칙 (0011 교훈: 계약을 테스트로 고정) ----------


def test_page_imports_match_component_stubs(dashboard_ui: UIGeneration) -> None:
    # page.tsx 가 import 하는 @/components/<kebab> 경로가 실제 스텁 파일과 1:1 대응
    gen = build_code_generation(dashboard_ui)
    stub_paths = {f.path for f in gen.files if f.path.startswith("components/")}
    page_files = [f for f in gen.files if f.path.endswith("page.tsx")]
    for page in page_files:
        imports = re.findall(r'@/components/([a-z0-9-]+)', page.content)
        for kebab in imports:
            assert f"components/{kebab}.tsx" in stub_paths


def test_component_stubs_export_named_function(dashboard_ui: UIGeneration) -> None:
    # 각 스텁은 명명된 함수 export 를 가져야 page import 가 동작
    gen = build_code_generation(dashboard_ui)
    for f in gen.files:
        if f.path.startswith("components/"):
            assert "export function" in f.content or "export const" in f.content


def test_no_collision_with_token_reserved_paths(dashboard_ui: UIGeneration) -> None:
    # ADR-0009 예약 토큰 경로와 충돌 X
    from devcanvas_api.pipeline.design.exporter import RESERVED_TOKEN_PATHS

    gen = build_code_generation(dashboard_ui)
    paths = {f.path for f in gen.files}
    assert not (paths & RESERVED_TOKEN_PATHS)


def test_all_files_are_tsx_or_ts(dashboard_ui: UIGeneration) -> None:
    gen = build_code_generation(dashboard_ui)
    for f in gen.files:
        assert f.language in ("tsx", "ts")


def test_no_duplicate_file_paths(dashboard_ui: UIGeneration) -> None:
    # 중복 엔티티/경로 회귀 방지 (리뷰 P1-2)
    gen = build_code_generation(dashboard_ui)
    paths = [f.path for f in gen.files]
    assert len(paths) == len(set(paths))


def test_kind_preserved_through_ui_to_code() -> None:
    # round-trip: ux kind → ui ScreenLayout.kind → code page_path 정합 (리뷰 P1-1)
    from devcanvas_api.pipeline.code import templates as ct
    from devcanvas_api.pipeline.schemas import ScreenKind

    plan = build_ux_plan(
        RequirementSpec(data_entities=["Customer"]), ScreenType.DASHBOARD
    )
    ui = build_ui_generation(plan)
    # dashboard layout → dashboard path
    dash = next(lay for lay in ui.layouts if lay.kind == ScreenKind.DASHBOARD)
    assert ct.page_path(dash, 0) == "app/dashboard/page.tsx"
    # list layout → list path
    list_lay = next(lay for lay in ui.layouts if lay.kind == ScreenKind.LIST)
    assert ct.page_path(list_lay, 1) == "app/customer/page.tsx"
    # detail layout → detail path
    detail_lay = next(lay for lay in ui.layouts if lay.kind == ScreenKind.DETAIL)
    assert ct.page_path(detail_lay, 2) == "app/customer/[id]/page.tsx"


def test_every_stub_is_imported_by_some_page(dashboard_ui: UIGeneration) -> None:
    # 역방향 정합 — 생성된 스텁은 모두 어떤 page 에서 import 되어야 (리뷰 P2-1)
    gen = build_code_generation(dashboard_ui)
    stub_paths = {f.path for f in gen.files if f.path.startswith("components/")}
    imported: set[str] = set()
    for page in (f for f in gen.files if f.path.endswith("page.tsx")):
        kebabs = re.findall(r'@/components/([a-z0-9-]+)', page.content)
        imported |= {f"components/{kebab}.tsx" for kebab in kebabs}
    assert stub_paths == imported


def test_admin_empty_requirement_uses_item_slug() -> None:
    # 엔티티 없는 ADMIN → 폴백 "항목 목록" → app/item/page.tsx (리뷰 P2-2)
    ui = build_ui_generation(build_ux_plan(RequirementSpec(), ScreenType.ADMIN))
    gen = build_code_generation(ui)
    paths = {f.path for f in gen.files}
    assert "app/item/page.tsx" in paths
    assert "interface Item" in next(f.content for f in gen.files if f.path == "lib/types.ts")
