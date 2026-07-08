"""코드 생성 템플릿 (ADR-0012).

종류별 page.tsx, 컴포넌트 스텁, types/mock 생성기. 결정적 문자열 반환.
page 가 import 하는 컴포넌트 경로(@/components/<kebab>)와 스텁 파일 경로가 1:1 대응한다.
"""

from __future__ import annotations

import re

from devcanvas_api.pipeline.schemas import ScreenKind, ScreenLayout

# 화면명 한글 라벨 → URL slug 역매핑
_LABEL_TO_SLUG: dict[str, str] = {
    "고객": "customer",
    "계약": "contract",
    "결제": "payment",
    "사용자": "user",
    "주문": "order",
    "항목": "item",
    "대시보드": "dashboard",
}


def pascal_to_kebab(name: str) -> str:
    """PascalCase → kebab-case (FilterBar → filter-bar)."""
    s1 = re.sub(r"(.)([A-Z][a-z]+)", r"\1-\2", name)
    return re.sub(r"([a-z0-9])([A-Z])", r"\1-\2", s1).lower()


def _kebab_to_pascal(kebab: str) -> str:
    return "".join(part.capitalize() for part in kebab.split("-"))


def _slug_from_screen(layout: ScreenLayout, index: int) -> str:
    """화면명에서 slug 도출. '고객 목록' → '고객' → 'customer'."""
    name = layout.screen
    base = name.replace(" 목록", "").replace(" 상세", "").strip()
    if base in _LABEL_TO_SLUG:
        return _LABEL_TO_SLUG[base]
    # ASCII 가 있으면 kebab, 아니면 kind-index 폴백
    ascii_parts = re.findall(r"[a-zA-Z0-9]+", base)
    if ascii_parts:
        return "-".join(p.lower() for p in ascii_parts)
    return f"{layout.kind.value}-{index}"


def page_path(layout: ScreenLayout, index: int) -> str:
    if layout.kind == ScreenKind.DASHBOARD:
        return "app/dashboard/page.tsx"
    if layout.kind == ScreenKind.DETAIL:
        return f"app/{_slug_from_screen(layout, index)}/[id]/page.tsx"
    return f"app/{_slug_from_screen(layout, index)}/page.tsx"


def page_component_name(layout: ScreenLayout, index: int) -> str:
    if layout.kind == ScreenKind.DASHBOARD:
        return "DashboardPage"
    slug = _slug_from_screen(layout, index)
    entity = _kebab_to_pascal(slug)
    if layout.kind == ScreenKind.DETAIL:
        return f"{entity}DetailPage"
    return f"{entity}ListPage"


def page_code(layout: ScreenLayout, index: int) -> str:
    kind = layout.kind
    comp_name = page_component_name(layout, index)
    # 중복 컴포넌트 제거(등장순 유지)
    unique_components = list(dict.fromkeys(layout.component_tree))
    imports = "\n".join(
        f'import {{ {c} }} from "@/components/{pascal_to_kebab(c)}";'
        for c in unique_components
    )
    body_components = "\n      ".join(f"<{c} />" for c in unique_components)
    slug = _slug_from_screen(layout, index)
    entity_type = _kebab_to_pascal(slug)

    if kind == ScreenKind.LIST:
        return f"""'use client';

{imports}
import {{ mock{entity_type}s }} from "@/lib/mock-data";
import type {{ {entity_type} }} from "@/lib/types";

export default function {comp_name}() {{
  const data: {entity_type}[] = mock{entity_type}s;
  // TODO: loading/empty/error/permission/mobile 상태 분기 (State Matrix 참조)
  return (
    <div className="space-y-4">
      {body_components}
    </div>
  );
}}
"""
    if kind == ScreenKind.DETAIL:
        return f"""'use client';

{imports}

export default function {comp_name}({{ params }}: {{ params: {{ id: string }} }}) {{
  // TODO: id 로 데이터 조회, loading/empty/error 상태 분기
  return (
    <div className="space-y-4">
      {body_components}
    </div>
  );
}}
"""
    # dashboard
    return f"""'use client';

{imports}

export default function {comp_name}() {{
  // TODO: KPI/차트 데이터 조회, loading/error 상태 분기
  return (
    <div className="space-y-4">
      {body_components}
    </div>
  );
}}
"""


def component_stub(component_name: str) -> str:
    """shadcn/ui 기반 컴포넌트 스텁 (본체 TODO)."""
    return f"""'use client';

// TODO: shadcn/ui 기반 {component_name} 구현
export function {component_name}() {{
  return <div>{component_name}</div>;
}}
"""


def types_code(entity_slugs: list[str]) -> str:
    """lib/types.ts — 엔티티별 인터페이스."""
    lines = ["// 자동 생성된 타입 정의 (실제 스키마로 교체 필요)", ""]
    for slug in entity_slugs:
        entity = _kebab_to_pascal(slug)
        lines.append(f"export interface {entity} {{")
        lines.append("  id: string;")
        lines.append('  name: string;')
        lines.append('  status: string;')
        lines.append('  createdAt: string;')
        lines.append("}")
        lines.append("")
    return "\n".join(lines)


def mock_data_code(entity_slugs: list[str]) -> str:
    """lib/mock-data.ts — 엔티티별 mock 배열."""
    lines = ["// 자동 생성된 mock 데이터 (실제 API 응답으로 교체 필요)", ""]
    for slug in entity_slugs:
        entity = _kebab_to_pascal(slug)
        lines.append(f"export const mock{entity}s = [")
        lines.append("  { id: '1', name: '샘플', status: 'active', createdAt: '2026-01-01' },")
        lines.append("  { id: '2', name: '샘플2', status: 'pending', createdAt: '2026-01-02' },")
        lines.append("];")
        lines.append("")
    return "\n".join(lines)
