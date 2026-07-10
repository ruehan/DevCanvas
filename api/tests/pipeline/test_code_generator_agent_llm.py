"""Code generator LLM page 골격 전환 테스트 (ADR-0024, 0012 보완).

page.tsx content 는 LLM 이 결정. components/types/mock-data 는 기존 rule-based 템플릿 유지.
"""

from __future__ import annotations

from typing import Any

from devcanvas_api.pipeline.agents import code_generator_agent
from devcanvas_api.pipeline.llm import DummyLLMAdapter, GenerationError
from devcanvas_api.pipeline.schemas import (
    GenerationInput,
    ScreenKind,
    ScreenLayout,
    UIGeneration,
)


def _ui() -> UIGeneration:
    return UIGeneration(
        layouts=[
            ScreenLayout(
                screen="대시보드",
                layout="KPI 그리드",
                kind=ScreenKind.DASHBOARD,
                component_tree=["KpiCard", "Chart"],
            ),
            ScreenLayout(
                screen="고객 목록",
                layout="필터+테이블",
                kind=ScreenKind.LIST,
                component_tree=["FilterBar", "DataTable"],
            ),
        ]
    )


def _input() -> GenerationInput:
    return GenerationInput(prompt="테스트")


_DASH_OK = (
    "'use client';\n"
    "export default function DashboardPage() { return <div>KPI</div>; }"
)
_LIST_OK = (
    "'use client';\n"
    "export default function CustomerListPage() { return <div>목록</div>; }"
)


def test_code_generator_calls_llm_with_context() -> None:
    captured: dict[str, Any] = {}

    class ProbeLLM:
        def generate(self, schema, instruction, context):  # type: ignore[no-untyped-def]
            captured["schema"] = schema
            captured["context"] = context
            return schema.model_validate(
                {
                    "pages": [
                        {"path": "app/dashboard/page.tsx", "content": _DASH_OK},
                        {"path": "app/customer/page.tsx", "content": _LIST_OK},
                    ]
                }
            )

    code_generator_agent(_input(), _ui(), ProbeLLM())  # type: ignore[arg-type]
    assert "schema" in captured
    assert "screens" in captured["context"]


def test_code_generator_uses_llm_content_when_valid() -> None:
    llm_content_dash = (
        "'use client';\n"
        "export default function DashboardPage() {\n"
        "  return <main className=\"kpi\">광고 KPI</main>;\n"
        "}\n"
    )

    class GoodLLM:
        def generate(self, schema, instruction, context):  # type: ignore[no-untyped-def]
            return schema.model_validate(
                {
                    "pages": [
                        {"path": "app/dashboard/page.tsx", "content": llm_content_dash},
                        {"path": "app/customer/page.tsx", "content": _LIST_OK},
                    ]
                }
            )

    gen = code_generator_agent(_input(), _ui(), GoodLLM())  # type: ignore[arg-type]
    dash = next(f for f in gen.files if f.path == "app/dashboard/page.tsx")
    assert dash.content == llm_content_dash  # LLM content 그대로 사용


def test_code_generator_falls_back_when_path_missing() -> None:
    """LLM이 한 페이지만 누락하면 그 페이지만 템플릿 fallback."""

    class PartialLLM:
        def generate(self, schema, instruction, context):  # type: ignore[no-untyped-def]
            return schema.model_validate(
                {
                    "pages": [
                        {"path": "app/dashboard/page.tsx", "content": _DASH_OK},
                    ]
                }
            )

    gen = code_generator_agent(_input(), _ui(), PartialLLM())  # type: ignore[arg-type]
    paths = {f.path for f in gen.files}
    assert "app/dashboard/page.tsx" in paths
    assert "app/customer/page.tsx" in paths
    # 누락된 페이지는 템플릿 page_code 형태 — CustomerListPage 보존
    customer = next(f for f in gen.files if f.path == "app/customer/page.tsx")
    assert "CustomerListPage" in customer.content


def test_code_generator_falls_back_when_content_invalid() -> None:
    """content가 'use client'/export default function을 포함하지 않으면 fallback."""

    class InvalidContentLLM:
        def generate(self, schema, instruction, context):  # type: ignore[no-untyped-def]
            return schema.model_validate(
                {
                    "pages": [
                        {"path": "app/dashboard/page.tsx", "content": "이건 tsx 가 아니다"},
                        {"path": "app/customer/page.tsx", "content": _LIST_OK},
                    ]
                }
            )

    gen = code_generator_agent(_input(), _ui(), InvalidContentLLM())  # type: ignore[arg-type]
    dash = next(f for f in gen.files if f.path == "app/dashboard/page.tsx")
    # fallback → 템플릿 page_code
    assert "DashboardPage" in dash.content
    assert "use client" in dash.content  # 템플릿은 'use client' 포함


def test_code_generator_keeps_auxiliary_files() -> None:
    """components/types/mock-data 는 LLM 무관하게 템플릿에서 생성."""

    class GoodLLM:
        def generate(self, schema, instruction, context):  # type: ignore[no-untyped-def]
            return schema.model_validate(
                {
                    "pages": [
                        {"path": "app/dashboard/page.tsx", "content": _DASH_OK},
                        {"path": "app/customer/page.tsx", "content": _LIST_OK},
                    ]
                }
            )

    gen = code_generator_agent(_input(), _ui(), GoodLLM())  # type: ignore[arg-type]
    paths = {f.path for f in gen.files}
    assert "lib/types.ts" in paths
    assert "lib/mock-data.ts" in paths
    assert any(p.startswith("components/") for p in paths)


def test_code_generator_with_dummy_runs() -> None:
    """DummyLLMAdapter도 정상 동작 (LLM 키 미설정 환경 대비)."""
    gen = code_generator_agent(_input(), _ui(), DummyLLMAdapter())
    paths = {f.path for f in gen.files}
    assert "app/dashboard/page.tsx" in paths
    assert "app/customer/page.tsx" in paths
    # page 본문에 'use client' 포함
    for f in gen.files:
        if f.path.startswith("app/") and f.path.endswith("page.tsx"):
            assert "use client" in f.content


def test_code_generator_llm_content_varies_per_prompt() -> None:
    """같은 kind/구성이라도 LLM content는 호출별로 달라질 수 있다 (다양화 보장)."""
    contents: list[str] = []

    class VaryLLM:
        def __init__(self, payload: dict[str, Any]) -> None:
            self._payload = payload

        def generate(self, schema, instruction, context):  # type: ignore[no-untyped-def]
            return schema.model_validate(self._payload)

    body_a = (
        "'use client';\n"
        "export default function DashboardPage() { return <div>A</div>; }"
    )
    body_b = (
        "'use client';\n"
        "export default function DashboardPage() { return <main>B</main>; }"
    )
    for body in (body_a, body_b):
        llm = VaryLLM(
            {
                "pages": [
                    {"path": "app/dashboard/page.tsx", "content": body},
                    {"path": "app/customer/page.tsx", "content": _LIST_OK},
                ]
            }
        )
        gen = code_generator_agent(_input(), _ui(), llm)  # type: ignore[arg-type]
        dash = next(f for f in gen.files if f.path == "app/dashboard/page.tsx")
        contents.append(dash.content)
    assert contents[0] != contents[1]


def test_code_generator_no_duplicate_page_paths() -> None:
    """LLM content 채택 후에도 page 경로 중복 없어야 한다 (기존 결정성 보존)."""

    class GoodLLM:
        def generate(self, schema, instruction, context):  # type: ignore[no-untyped-def]
            return schema.model_validate(
                {
                    "pages": [
                        {"path": "app/dashboard/page.tsx", "content": _DASH_OK},
                        {"path": "app/customer/page.tsx", "content": _LIST_OK},
                    ]
                }
            )

    gen = code_generator_agent(_input(), _ui(), GoodLLM())  # type: ignore[arg-type]
    page_paths = [
        f.path for f in gen.files if f.path.startswith("app/") and f.path.endswith("page.tsx")
    ]
    assert len(page_paths) == len(set(page_paths))


def test_code_generator_page_path_from_template() -> None:
    """LLM 이 다른 path 를 줘도 우리 계산 path 가 우선 (path 결정권은 템플릿)."""

    class WrongPathLLM:
        def generate(self, schema, instruction, context):  # type: ignore[no-untyped-def]
            return schema.model_validate(
                {
                    "pages": [
                        # 무시됨 — 우리 계산 path 와 불일치
                        {"path": "WRONG/path.tsx", "content": _DASH_OK},
                    ]
                }
            )

    gen = code_generator_agent(_input(), _ui(), WrongPathLLM())  # type: ignore[arg-type]
    paths = {f.path for f in gen.files}
    assert "app/dashboard/page.tsx" in paths
    assert "app/customer/page.tsx" in paths
    assert "WRONG/path.tsx" not in paths


def test_code_generator_falls_back_on_generation_error() -> None:
    """LLM 호출 실패(GenerationError) 시 전 페이지 rule-based fallback (ADR-0024)."""

    class BoomLLM:
        def generate(self, schema, instruction, context):  # type: ignore[no-untyped-def]
            raise GenerationError("GLM 다운")

    gen = code_generator_agent(_input(), _ui(), BoomLLM())  # type: ignore[arg-type]
    paths = {f.path for f in gen.files}
    assert "app/dashboard/page.tsx" in paths
    assert "app/customer/page.tsx" in paths
    # fallback은 템플릿 page_code 형태
    dash = next(f for f in gen.files if f.path == "app/dashboard/page.tsx")
    assert "DashboardPage" in dash.content


def test_code_generator_falls_back_on_unknown_component_import() -> None:
    """LLM content가 stub에 존재하지 않는 컴포넌트를 import 하면 페이지 단위 fallback."""
    bad_content = (
        "'use client';\n"
        "import { Ghost } from '@/components/ghost';\n"
        "export default function DashboardPage() { return <Ghost />; }"
    )

    class BadImportLLM:
        def generate(self, schema, instruction, context):  # type: ignore[no-untyped-def]
            return schema.model_validate(
                {
                    "pages": [
                        {"path": "app/dashboard/page.tsx", "content": bad_content},
                        {"path": "app/customer/page.tsx", "content": _LIST_OK},
                    ]
                }
            )

    gen = code_generator_agent(_input(), _ui(), BadImportLLM())  # type: ignore[arg-type]
    dash = next(f for f in gen.files if f.path == "app/dashboard/page.tsx")
    # fallback → 템플릿 page_code (Ghost import 없음)
    assert "Ghost" not in dash.content
    assert "DashboardPage" in dash.content