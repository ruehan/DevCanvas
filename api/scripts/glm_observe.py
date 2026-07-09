"""GLM 실호출 관측 하네스 (ADR-0007 재시도 정책 근거 수집).

실 GLM 키로 두 LLM 호출 표면을 반복 실행해 실패 유형·빈도를 관측한다:
  1) requirement_agent → RequirementSpec  (첫 턴, 작은 스키마)
  2) apply_edit        → GenerationResult (편집 턴, 거대 중첩 스키마)

실패를 유형으로 분류(http / json / schema)해 재시도가 실제로 도움이 될지 판단한다.
스키마 위반이 잦으면 "오류 피드백 재프롬프트" 재시도가, http 오류가 잦으면 "지수 백오프"가 답.

사용:
    cd api
    DEVCANVAS_GLM_API_KEY=... uv run python scripts/glm_observe.py            # 기본 3회
    DEVCANVAS_GLM_API_KEY=... uv run python scripts/glm_observe.py --runs 5

주의: 실 GLM API 를 호출한다(토큰 비용 발생). 프로덕션/고객 데이터와 무관한 관측 전용.
"""

from __future__ import annotations

import argparse
import sys
from collections import Counter
from dataclasses import dataclass, field

from devcanvas_api.core import settings
from devcanvas_api.pipeline.edit_agent import apply_edit
from devcanvas_api.pipeline.llm import (
    DummyLLMAdapter,
    GenerationError,
    GLMAdapter,
)
from devcanvas_api.pipeline.orchestrator import run_pipeline
from devcanvas_api.pipeline.schemas import GenerationInput, RequirementSpec

# 관측용 프롬프트 — 도메인 다양(대시보드/목록/주문관리).
PROMPTS: list[str] = [
    "정기결제 SaaS 관리자 페이지를 만들어줘. MRR 대시보드, 구독자 관리, 환불 이력 포함.",
    "채용 플랫폼 공고 목록을 만들어줘. 필터 사이드바, 카드형 리스트, 상세 모달 포함.",
    "이커머스 주문 관리 페이지를 만들어줘. 주문 상태별 탭, 검색, 일괄 처리 포함.",
]
EDIT_INSTRUCTION = "주문 상태 필터를 하나 더 추가하고, 표에 담당자 열을 넣어줘."


def classify_error(err: GenerationError) -> str:
    """GenerationError 메시지를 실패 유형으로 분류한다(llm.py 의 메시지 프리픽스 기반)."""
    msg = str(err)
    if "호출 실패" in msg:
        return "http"
    if "JSON" in msg:
        return "json"
    if "스키마 검증 실패" in msg:
        return "schema"
    if "키 미설정" in msg:
        return "no_key"
    return "other"


@dataclass
class StageStats:
    """한 호출 표면의 관측 집계."""

    ok: int = 0
    outcomes: Counter[str] = field(default_factory=Counter)
    samples: list[str] = field(default_factory=list)

    def record_ok(self) -> None:
        self.ok += 1
        self.outcomes["ok"] += 1

    def record_error(self, err: GenerationError) -> None:
        kind = classify_error(err)
        self.outcomes[kind] += 1
        if len(self.samples) < 3:
            self.samples.append(f"[{kind}] {str(err)[:200]}")

    @property
    def total(self) -> int:
        return sum(self.outcomes.values())


def observe_requirement(glm: GLMAdapter, prompt: str, stats: StageStats) -> RequirementSpec | None:
    """requirement_agent 1회 실호출 관측. 성공 시 스펙 반환(품질 신호 출력용)."""
    from devcanvas_api.pipeline.agents import requirement_agent

    try:
        spec = requirement_agent(GenerationInput(prompt=prompt), glm)
    except GenerationError as e:
        stats.record_error(e)
        return None
    stats.record_ok()
    return spec


def observe_edit(glm: GLMAdapter, stats: StageStats) -> None:
    """apply_edit 1회 실호출 관측. 베이스라인 결과는 더미(결정적)로 만든다."""
    baseline = run_pipeline(GenerationInput(prompt=PROMPTS[2]), DummyLLMAdapter())
    try:
        apply_edit(baseline, EDIT_INSTRUCTION, glm)
    except GenerationError as e:
        stats.record_error(e)
        return
    stats.record_ok()


def _print_stage(title: str, stats: StageStats) -> None:
    print(f"\n=== {title} ===")
    print(f"  총 {stats.total}회 / 성공 {stats.ok}회 ({_pct(stats.ok, stats.total)})")
    for kind, n in stats.outcomes.most_common():
        if kind == "ok":
            continue
        print(f"  실패[{kind}]: {n}회")
    for s in stats.samples:
        print(f"    · {s}")


def _pct(n: int, total: int) -> str:
    return f"{(100 * n / total):.0f}%" if total else "n/a"


def main() -> int:
    parser = argparse.ArgumentParser(description="GLM 실호출 관측 하네스")
    parser.add_argument("--runs", type=int, default=3, help="프롬프트별 반복 횟수(기본 3)")
    parser.add_argument("--skip-edit", action="store_true", help="편집 턴 관측 생략")
    args = parser.parse_args()

    if not settings.glm_api_key:
        print(
            "GLM 키 미설정 — DEVCANVAS_GLM_API_KEY 를 주입하고 다시 실행하세요.\n"
            "  예: DEVCANVAS_GLM_API_KEY=... uv run python scripts/glm_observe.py",
            file=sys.stderr,
        )
        return 2

    glm = GLMAdapter()
    print(f"설정: model={settings.glm_model} base={settings.glm_api_base} runs={args.runs}")
    print(
        "(model/base 가 실제 계정과 다르면 http 오류 — "
        "DEVCANVAS_GLM_MODEL/_API_BASE 로 override)"
    )

    req_stats = StageStats()
    edit_stats = StageStats()

    for prompt in PROMPTS:
        print(f"\n▶ 프롬프트: {prompt[:40]}...")
        for i in range(args.runs):
            spec = observe_requirement(glm, prompt, req_stats)
            if spec is not None:
                print(
                    f"  [{i + 1}] requirement OK — "
                    f"features={len(spec.features)} screens={len(spec.screens)} "
                    f"entities={spec.data_entities}"
                )
            else:
                print(f"  [{i + 1}] requirement 실패")

    if not args.skip_edit:
        print("\n▶ 편집 턴(apply_edit → 부분 패치 병합, ADR-0023)")
        for i in range(args.runs):
            observe_edit(glm, edit_stats)
            print(f"  [{i + 1}] edit {'OK' if edit_stats.outcomes['ok'] else '실패'}")

    _print_stage("requirement (RequirementSpec)", req_stats)
    if not args.skip_edit:
        _print_stage("edit (GenerationResult)", edit_stats)

    print("\n── 판단 힌트 ──")
    print("  schema 위반 잦음 → 오류 피드백 재프롬프트 재시도가 유효")
    print("  http 오류 잦음   → 지수 백오프/타임아웃 조정 (모델·엔드포인트부터 점검)")
    print("  json 오류 잦음   → 프롬프트에 'JSON 객체만' 강조 강화 or few-shot")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
