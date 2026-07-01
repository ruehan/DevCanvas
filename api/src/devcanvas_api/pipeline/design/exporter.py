"""DesignSystem 토큰을 다중 포맷으로 변환하는 exporter (ADR-0008).

순수 함수 — 결정적이고 부작용 없음.
포맷: tokens.ts / tailwind.config.json / design.json / tokens.css / design.md
"""

from __future__ import annotations

import json
from typing import TypeAlias

from devcanvas_api.pipeline.schemas import CodeFile, DesignSystem

TokensTree: TypeAlias = dict[str, dict[str, str]]
TailwindConfig: TypeAlias = dict[str, dict[str, dict[str, dict[str, str]]]]

# CSS 변수 접두사 — 카테고리(복수) → 시맨틱 단수
_CSS_PREFIX: dict[str, str] = {
    "colors": "color",
    "spacing": "spacing",
    "radius": "radius",
    "typography": "font",
    "shadows": "shadow",
}


def _tokens_dict(ds: DesignSystem) -> TokensTree:
    t = ds.tokens
    return {
        "colors": dict(t.colors),
        "spacing": dict(t.spacing),
        "radius": dict(t.radius),
        "typography": dict(t.typography),
        "shadows": dict(t.shadows),
    }


def to_design_json(ds: DesignSystem) -> dict[str, TokensTree]:
    """원본 토큰 딕셔너리(JSON 직렬화 가능)."""
    return {"tokens": _tokens_dict(ds)}


def to_tokens_ts(ds: DesignSystem) -> str:
    """TypeScript 모듈 형태."""
    body = json.dumps(_tokens_dict(ds), ensure_ascii=False, indent=2)
    return f"export const tokens = {body} as const;\n"


def to_tailwind_config(ds: DesignSystem) -> TailwindConfig:
    """Tailwind theme.extend 매핑.

    typography 시맨틱(body/heading/caption)을 fontSize 키로 그대로 사용한다
    (text-body/text-heading/text-caption 클래스 의도). xs~lg 스케일이 아님에 주의.
    """
    t = ds.tokens
    return {
        "theme": {
            "extend": {
                "colors": dict(t.colors),
                "spacing": dict(t.spacing),
                "borderRadius": dict(t.radius),
                "fontSize": dict(t.typography),
                "boxShadow": dict(t.shadows),
            }
        }
    }


def to_tokens_css(ds: DesignSystem) -> str:
    """:root CSS 변수 형태. 시맨틱 단수 접두사(--color-*, --spacing-*, --font-* ...)."""
    lines: list[str] = [":root {"]
    for category, entries in _tokens_dict(ds).items():
        prefix = _CSS_PREFIX[category]
        for key, value in entries.items():
            lines.append(f"  --{prefix}-{key}: {value};")
    lines.append("}")
    return "\n".join(lines) + "\n"


def to_design_md(ds: DesignSystem) -> str:
    """사람이 읽기 좋은 마크다운 문서."""
    t = ds.tokens
    sections: list[str] = ["# 디자인 시스템", ""]

    def _table(title: str, rows: dict[str, str]) -> None:
        sections.append(f"## {title}")
        sections.append("")
        sections.append("| 키 | 값 |")
        sections.append("| --- | --- |")
        for k, v in rows.items():
            sections.append(f"| `{k}` | `{v}` |")
        sections.append("")

    _table("Colors", t.colors)
    _table("Spacing", t.spacing)
    _table("Radius", t.radius)
    _table("Typography", t.typography)
    _table("Shadows", t.shadows)
    return "\n".join(sections)


def to_code_files(ds: DesignSystem) -> list[CodeFile]:
    """DesignSystem 토큰을 핸드오프 가능한 코드 파일 5종으로 변환 (ADR-0009).

    산출:
      - lib/tokens.ts         (TS 모듈)
      - tailwind.config.json  (Tailwind theme.extend, 루트 — Tailwind 관례)
      - tokens/design.json    (원본 토큰)
      - styles/tokens.css     (:root CSS 변수)
      - docs/design.md        (문서)

    제네릭 루트명(design.md/design.json)은 네임스페이스해 충돌 표면을 줄인다.
    """
    return [
        CodeFile(path="lib/tokens.ts", language="ts", content=to_tokens_ts(ds)),
        CodeFile(
            path="tailwind.config.json",
            language="json",
            content=json.dumps(to_tailwind_config(ds), ensure_ascii=False, indent=2),
        ),
        CodeFile(
            path="tokens/design.json",
            language="json",
            content=json.dumps(to_design_json(ds), ensure_ascii=False, indent=2),
        ),
        CodeFile(path="styles/tokens.css", language="css", content=to_tokens_css(ds)),
        CodeFile(path="docs/design.md", language="md", content=to_design_md(ds)),
    ]


# 토큰 파일 경로 예약어 — code_generator 등 다른 소스와 충돌 방지(ADR-0009)
RESERVED_TOKEN_PATHS: frozenset[str] = frozenset(
    f.path for f in to_code_files(DesignSystem())
)
