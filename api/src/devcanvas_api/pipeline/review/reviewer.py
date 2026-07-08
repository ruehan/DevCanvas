"""리뷰 집계 — 체크들을 실행해 ReviewReport 생성 (ADR-0013)."""

from __future__ import annotations

from devcanvas_api.pipeline.review import checks
from devcanvas_api.pipeline.schemas import CodeGeneration, ReviewReport


def run_review(code: CodeGeneration) -> ReviewReport:
    """CodeGeneration 의 모든 파일에 모든 체크를 적용해 findings 를 집계한다."""
    findings = []
    for f in code.files:
        for check in checks.CHECKS:
            findings.extend(check(f))
    return ReviewReport(findings=findings)
