"""디자인 시스템 preset/exporter 테스트."""

from __future__ import annotations

import json

import pytest

from devcanvas_api.pipeline.design.exporter import (
    to_code_files,
    to_design_json,
    to_design_md,
    to_tailwind_config,
    to_tokens_css,
    to_tokens_ts,
)
from devcanvas_api.pipeline.design.presets import (
    SUPPORTED_TONES,
    build_design_system,
)
from devcanvas_api.pipeline.schemas import DesignSystem


@pytest.fixture()
def b2b_system() -> DesignSystem:
    return build_design_system(tone="b2b")


# ---------- presets ----------


@pytest.mark.parametrize("tone", list(SUPPORTED_TONES))
def test_each_tone_builds_full_tokens(tone: str) -> None:
    ds = build_design_system(tone=tone)
    t = ds.tokens
    assert t.colors  # 색상 토큰 채워짐
    assert t.spacing
    assert t.radius
    assert t.typography
    assert t.shadows
    # 핵심 시맨틱 색상 키가 존재
    for key in ("primary", "background", "text", "danger"):
        assert key in t.colors


@pytest.mark.parametrize("tone", list(SUPPORTED_TONES))
def test_each_tone_preset_has_all_keys(tone: str) -> None:
    # TypedDict 런타임 검증 없음 → 키 존재 명시 단언
    ds = build_design_system(tone=tone)
    for group in ("colors", "typography", "shadows"):
        assert getattr(ds.tokens, group), f"{tone}.{group} 비어있음"


def test_different_tones_yield_different_palettes() -> None:
    b2b = build_design_system(tone="b2b")
    startup = build_design_system(tone="startup")
    assert b2b.tokens.colors["primary"] != startup.tokens.colors["primary"]


def test_tone_is_case_insensitive() -> None:
    assert build_design_system("B2B").tokens.colors == build_design_system("b2b").tokens.colors


def test_unknown_tone_falls_back_to_b2b() -> None:
    ds = build_design_system(tone="존재안함")
    # 실제로 b2b 폴백인지(고정 primary) 검증 — 단순 truthy 아님
    assert ds.tokens.colors["primary"] == "#2563EB"


# ---------- exporter: tokens.ts ----------


def test_tokens_ts_is_valid_ts(b2b_system: DesignSystem) -> None:
    out = to_tokens_ts(b2b_system)
    assert out.startswith("export const tokens")
    assert "as const" in out
    assert '"primary"' in out


# ---------- exporter: tailwind config ----------


def test_tailwind_config_maps_to_theme_extend(b2b_system: DesignSystem) -> None:
    cfg = to_tailwind_config(b2b_system)
    extend = cfg["theme"]["extend"]
    assert extend["colors"]["primary"] == b2b_system.tokens.colors["primary"]
    # spacing 스케일 키 그대로
    assert set(extend["spacing"]) == set(b2b_system.tokens.spacing)
    # fontSize: typography 시맨틱 키 그대로 매핑(의도 — docstring 참조)
    assert extend["fontSize"]["body"] == b2b_system.tokens.typography["body"]
    # JSON 직렬화 가능(문자열 값)
    json.dumps(cfg)


# ---------- exporter: design.json ----------


def test_design_json_roundtrip(b2b_system: DesignSystem) -> None:
    data = to_design_json(b2b_system)
    assert data["tokens"]["colors"]["primary"] == b2b_system.tokens.colors["primary"]
    # DesignSystem 으로 재구성 가능
    rebuilt = DesignSystem.model_validate(data)
    assert rebuilt.tokens.colors == b2b_system.tokens.colors


# ---------- exporter: tokens.css ----------


def test_tokens_css_uses_css_variables(b2b_system: DesignSystem) -> None:
    css = to_tokens_css(b2b_system)
    assert ":root {" in css
    assert "--color-primary" in css
    assert b2b_system.tokens.colors["primary"] in css


# ---------- exporter: design.md ----------


def test_design_md_documents_tokens(b2b_system: DesignSystem) -> None:
    md = to_design_md(b2b_system)
    assert md.startswith("# ")
    assert "Colors" in md or "색상" in md
    assert b2b_system.tokens.colors["primary"] in md


# ---------- exporter: 빈 DesignSystem 엣지 ----------


def test_exporters_handle_empty_design_system() -> None:
    empty = DesignSystem()
    # 모든 필드가 빈 dict 여도 예외 없이 빈 구조 반환
    data = to_design_json(empty)
    assert set(data["tokens"]) == {"colors", "spacing", "radius", "typography", "shadows"}
    assert all(v == {} for v in data["tokens"].values())
    assert "export const tokens" in to_tokens_ts(empty)
    cfg = to_tailwind_config(empty)
    assert cfg["theme"]["extend"]["colors"] == {}
    css = to_tokens_css(empty)
    assert css == ":root {\n}\n"
    assert to_design_md(empty).startswith("# ")


# ---------- exporter: to_code_files (파이프라인 연결) ----------


def test_to_code_files_produces_five_artifacts(b2b_system: DesignSystem) -> None:
    files = to_code_files(b2b_system)
    paths = {f.path for f in files}
    assert paths == {
        "lib/tokens.ts",
        "tailwind.config.json",
        "design.json",
        "styles/tokens.css",
        "design.md",
    }
    # 언어 일관성
    by_path = {f.path: f for f in files}
    assert by_path["lib/tokens.ts"].language == "ts"
    assert by_path["tailwind.config.json"].language == "json"
    assert by_path["styles/tokens.css"].language == "css"
    assert by_path["design.md"].language == "md"
    # 내용이 exporter 출력과 일관
    assert to_tokens_ts(b2b_system) in by_path["lib/tokens.ts"].content
    assert to_tokens_css(b2b_system) in by_path["styles/tokens.css"].content


def test_to_code_files_empty_design_system() -> None:
    files = to_code_files(DesignSystem())
    # 빈 토큰이어도 5개 파일은 정상 생성
    assert len(files) == 5
