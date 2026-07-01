"""디자인 시스템 preset/exporter 테스트."""

from __future__ import annotations

import json

import pytest

from devcanvas_api.pipeline.design.exporter import (
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
    return build_design_system(tone="B2B")


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


def test_different_tones_yield_different_palettes() -> None:
    b2b = build_design_system(tone="B2B")
    startup = build_design_system(tone="startup")
    assert b2b.tokens.colors["primary"] != startup.tokens.colors["primary"]


def test_unknown_tone_falls_back() -> None:
    ds = build_design_system(tone="존재안함")
    assert ds.tokens.colors  # 폴백 preset 으로도 토큰 생성


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
