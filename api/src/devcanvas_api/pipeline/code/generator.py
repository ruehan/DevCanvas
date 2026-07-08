"""코드 생성기 — UIGeneration 에서 코드 파일 규칙 기반 도출 (ADR-0012)."""

from __future__ import annotations

from typing import Literal

from devcanvas_api.pipeline.code import templates
from devcanvas_api.pipeline.naming import pascal_to_kebab
from devcanvas_api.pipeline.schemas import CodeFile, CodeGeneration, ScreenKind, UIGeneration


def build_code_generation(ui: UIGeneration) -> CodeGeneration:
    """UIGeneration(layouts)에서 page.tsx + 컴포넌트 스텁 + types/mock 코드를 생성한다."""
    files: list[CodeFile] = []
    seen_paths: set[str] = set()
    stub_components: set[str] = set()
    list_slugs: list[str] = []

    def _add(path: str, language: Literal["tsx", "ts", "css", "json", "md"], content: str) -> None:
        if path in seen_paths:  # 중복 엔티티 등에 의한 동일 경로 회피
            return
        seen_paths.add(path)
        files.append(CodeFile(path=path, language=language, content=content))

    for index, layout in enumerate(ui.layouts):
        _add(templates.page_path(layout, index), "tsx", templates.page_code(layout, index))
        stub_components.update(layout.component_tree)
        if layout.kind == ScreenKind.LIST:
            list_slugs.append(templates._slug_from_screen(layout, index))

    for comp in sorted(stub_components):
        stub_path = f"components/{pascal_to_kebab(comp)}.tsx"
        _add(stub_path, "tsx", templates.component_stub(comp))

    unique_slugs: list[str] = []
    seen: set[str] = set()
    for slug in list_slugs:
        if slug not in seen:
            seen.add(slug)
            unique_slugs.append(slug)
    _add("lib/types.ts", "ts", templates.types_code(unique_slugs))
    _add("lib/mock-data.ts", "ts", templates.mock_data_code(unique_slugs))

    return CodeGeneration(files=files)
