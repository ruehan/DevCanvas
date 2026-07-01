"""톤별 디자인 토큰 프리셋 (ADR-0008).

도메인 지식의 단일 소스. 새 톤 추가 = 새 프리셋 추가.
각 프리셋은 colors/spacing/radius/typography/shadows 스케일을 제공한다.
"""

from __future__ import annotations

from typing import TypedDict

from devcanvas_api.pipeline.schemas import DesignSystem, DesignTokens

# 공통 spacing/radius 스케일 — 톤 무관 일관성 유지
_SPACING = {"xs": "4px", "sm": "8px", "md": "16px", "lg": "24px", "xl": "32px"}
_RADIUS = {"sm": "6px", "md": "10px", "lg": "16px"}


class TonePreset(TypedDict):
    colors: dict[str, str]
    typography: dict[str, str]
    shadows: dict[str, str]


_TONE_PRESETS: dict[str, TonePreset] = {
    "B2B": {
        "colors": {
            "primary": "#2563EB",
            "background": "#F8FAFC",
            "surface": "#FFFFFF",
            "text": "#0F172A",
            "muted": "#64748B",
            "danger": "#DC2626",
            "success": "#16A34A",
        },
        "typography": {"body": "14px", "heading": "20px", "caption": "12px"},
        "shadows": {"sm": "0 1px 2px rgba(0,0,0,0.06)", "md": "0 4px 12px rgba(0,0,0,0.08)"},
    },
    "minimal": {
        "colors": {
            "primary": "#111827",
            "background": "#FFFFFF",
            "surface": "#FAFAFA",
            "text": "#111827",
            "muted": "#6B7280",
            "danger": "#EF4444",
            "success": "#10B981",
        },
        "typography": {"body": "14px", "heading": "22px", "caption": "12px"},
        "shadows": {"sm": "0 1px 2px rgba(0,0,0,0.04)", "md": "0 2px 8px rgba(0,0,0,0.06)"},
    },
    "enterprise": {
        "colors": {
            "primary": "#1E3A8A",
            "background": "#F1F5F9",
            "surface": "#FFFFFF",
            "text": "#1E293B",
            "muted": "#475569",
            "danger": "#B91C1C",
            "success": "#15803D",
        },
        "typography": {"body": "14px", "heading": "20px", "caption": "12px"},
        "shadows": {"sm": "0 1px 3px rgba(0,0,0,0.08)", "md": "0 6px 16px rgba(0,0,0,0.10)"},
    },
    "startup": {
        "colors": {
            "primary": "#7C3AED",
            "background": "#FAFAFF",
            "surface": "#FFFFFF",
            "text": "#1F2937",
            "muted": "#6B7280",
            "danger": "#EF4444",
            "success": "#22C55E",
        },
        "typography": {"body": "15px", "heading": "24px", "caption": "12px"},
        "shadows": {
            "sm": "0 2px 4px rgba(124,58,237,0.08)",
            "md": "0 8px 20px rgba(124,58,237,0.12)",
        },
    },
    "friendly": {
        "colors": {
            "primary": "#F59E0B",
            "background": "#FFFBEB",
            "surface": "#FFFFFF",
            "text": "#292524",
            "muted": "#78716C",
            "danger": "#E11D48",
            "success": "#16A34A",
        },
        "typography": {"body": "15px", "heading": "22px", "caption": "13px"},
        "shadows": {"sm": "0 1px 3px rgba(0,0,0,0.06)", "md": "0 4px 14px rgba(245,158,11,0.16)"},
    },
}

SUPPORTED_TONES = frozenset(_TONE_PRESETS)
_FALLBACK_TONE = "B2B"


def build_design_system(tone: str) -> DesignSystem:
    """톤에 해당하는 프리셋으로 DesignSystem 을 생성한다.

    알 수 없는 톤은 _FALLBACK_TONE(B2B)으로 폴백한다.
    """
    preset = _TONE_PRESETS.get(tone, _TONE_PRESETS[_FALLBACK_TONE])
    tokens = DesignTokens(
        colors=dict(preset["colors"]),
        spacing=dict(_SPACING),
        radius=dict(_RADIUS),
        typography=dict(preset["typography"]),
        shadows=dict(preset["shadows"]),
    )
    return DesignSystem(tokens=tokens)
