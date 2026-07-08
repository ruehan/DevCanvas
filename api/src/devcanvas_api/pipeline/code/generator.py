"""코드 생성기 — UIGeneration 에서 코드 파일 규칙 기반 도출 (ADR-0012)."""

from __future__ import annotations

from devcanvas_api.pipeline.code import templates
from devcanvas_api.pipeline.schemas import CodeFile, CodeGeneration, ScreenKind, UIGeneration


def build_code_generation(ui: UIGeneration) -> CodeGeneration:
    """UIGeneration(layouts)에서 page.tsx + 컴포넌트 스텁 + types/mock 코드를 생성한다."""
    files: list[CodeFile] = []
    stub_components: set[str] = set()
    list_slugs: list[str] = []

    for index, layout in enumerate(ui.layouts):
        # page.tsx
        files.append(
            CodeFile(
                path=templates.page_path(layout, index),
                language="tsx",
                content=templates.page_code(layout, index),
            )
        )
        stub_components.update(layout.component_tree)

        # list 화면의 slug 수집 → types/mock 엔티티
        if templates.layout_screen_kind(layout) == ScreenKind.LIST:
            list_slugs.append(templates._slug_from_screen(layout, index))

    # 컴포넌트 스텁 (유니크)
    for comp in sorted(stub_components):
        files.append(
            CodeFile(
                path=f"components/{templates.pascal_to_kebab(comp)}.tsx",
                language="tsx",
                content=templates.component_stub(comp),
            )
        )

    # types/mock (중복 slug 제거)
    unique_slugs: list[str] = []
    seen: set[str] = set()
    for slug in list_slugs:
        if slug not in seen:
            seen.add(slug)
            unique_slugs.append(slug)
    files.append(
        CodeFile(path="lib/types.ts", language="ts", content=templates.types_code(unique_slugs))
    )
    files.append(
        CodeFile(
            path="lib/mock-data.ts",
            language="ts",
            content=templates.mock_data_code(unique_slugs),
        )
    )

    return CodeGeneration(files=files)
