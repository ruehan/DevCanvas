"""핸드오프 빌더 — code/review 에서 HandoffDoc 유도 (ADR-0016, ADR-0009 갭 해소)."""

from __future__ import annotations

from devcanvas_api.pipeline.naming import kebab_to_pascal
from devcanvas_api.pipeline.schemas import CodeGeneration, HandoffDoc, ReviewReport

# 컴포넌트(스텁) → 외부 npm 패키지 매핑. shadcn/ui 기본 제공(Tabs/Card 등)은 제외.
# 새 외부 의존은 여기에 추가.
_KNOWN_DEPS: dict[str, str] = {
    "DataTable": "@tanstack/react-table",
    "Chart": "recharts",
}


def _detect_install_commands(code: CodeGeneration) -> list[str]:
    packages: list[str] = []
    seen: set[str] = set()
    for f in code.files:
        if not f.path.startswith("components/"):
            continue
        # components/filter-bar.tsx → FilterBar
        name = f.path.split("/", 1)[1].removesuffix(".tsx")
        pascal = kebab_to_pascal(name)
        pkg = _KNOWN_DEPS.get(pascal)
        if pkg and pkg not in seen:
            seen.add(pkg)
            packages.append(pkg)
    return [f"pnpm add {' '.join(packages)}"] if packages else []


def _build_todos(code: CodeGeneration, review: ReviewReport) -> list[str]:
    todos: list[str] = []
    # review P1 → 구현 필요
    for finding in review.findings:
        if finding.severity.value == "P1":
            todos.append(f"구현 필요: {finding.category} — {finding.message}")
    # 표준: mock 데이터 교체
    if any("@/lib/mock-data" in f.content or "mock-data" in f.path for f in code.files):
        todos.append("mock 데이터를 실제 API 응답으로 교체")
    # 표준: 컴포넌트 스텁 본체 구현
    stubs = [f for f in code.files if f.path.startswith("components/") and "TODO" in f.content]
    if stubs:
        todos.append(f"shadcn/ui 컴포넌트 본체 구현(스텁 {len(stubs)}개)")
    return todos


def _build_guide(
    file_tree: list[str], install: list[str], todos: list[str], review: ReviewReport
) -> str:
    lines: list[str] = ["# 구현 가이드", ""]
    lines.append("## 파일 구조")
    lines.append("```")
    lines.extend(file_tree)
    lines.append("```")
    lines.append("")
    lines.append("## 설치")
    if install:
        lines.extend(install)
    else:
        lines.append("(추가 패키지 없음)")
    lines.append("")
    lines.append("## TODO")
    if todos:
        lines.extend(f"- {t}" for t in todos)
    else:
        lines.append("- (없음)")
    lines.append("")
    p1 = [f for f in review.findings if f.severity.value == "P1"]
    if p1:
        lines.append("## 우선 해결(P1 리뷰)")
        for f in p1:
            lines.append(f"- [{f.category}] {f.message}")
    return "\n".join(lines) + "\n"


def build_handoff(code: CodeGeneration, review: ReviewReport) -> HandoffDoc:
    """실제 code/review 에서 파일 트리·설치·TODO·가이드를 유도한다."""
    file_tree = sorted({f.path for f in code.files})
    install_commands = _detect_install_commands(code)
    todos = _build_todos(code, review)
    guide_md = _build_guide(file_tree, install_commands, todos, review)
    return HandoffDoc(
        file_tree=file_tree,
        install_commands=install_commands,
        todos=todos,
        guide_md=guide_md,
    )
